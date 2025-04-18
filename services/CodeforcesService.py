import hashlib
import logging
import time
import requests
from pymongo.auth import authenticate

from database.database_worker import DatabaseWorker
from services.UsersService import UsersService

class CodeforcesService:
    ray_id = -2
    def __init__(self, database_worker: DatabaseWorker, users_service: UsersService, config: dict):
        self.database_worker = database_worker
        self.users_service = users_service
        self.config = config

    def sign_request(self, method: str, request: str) -> str:
        time_for_request = int(time.time())
        url_parts = request.split('&')
        url_parts.append(f"time={time_for_request}")
        url_parts.append(f"apiKey={self.config["codeforces"]["APIKey"]}")
        url_parts.sort()

        generated_hash = hashlib.sha512(f"123456/{method}?{"&".join(url_parts)}#{self.config["codeforces"]["APISecret"]}".encode()).hexdigest()
        logging.info(f"Generated request: " + f"https://codeforces.com/api/{method}?{"&".join(url_parts)}&apiSig=123456{generated_hash}")
        return f"https://codeforces.com/api/{method}?{"&".join(url_parts)}&apiSig=123456{generated_hash}"
    def get_contests(self, group_code: str | None = None) -> list:
        request = f"gym=false"
        if group_code is not None:
            request += f"&groupCode={group_code}"
        signed_request = self.sign_request('contest.list', request)
        contest_list_response = requests.get(signed_request)
        logging.debug(f"CODEFORCES_SERVICE: List of contests raw response is: {contest_list_response.text}")
        contest_list = list(contest_list_response.json()['result'])
        return contest_list

    def get_registered_users_with_handle(self):
        registered_users_with_handle = self.database_worker.find('users', {
            'codeforces.handle': {
                '$exists': True
            }
        }, self.ray_id)
        registered_users_with_handle_dict = {}
        for registered_user_with_handle in registered_users_with_handle:
            registered_users_with_handle_dict[registered_user_with_handle['codeforces']['handle']] = registered_user_with_handle['userId']
        return registered_users_with_handle_dict

    def filter_for_contests(self, contest: dict, is_group_contest: bool = False):
        # condition contest finished
        if str(contest["phase"]) != "FINISHED":
            return False
        
        # condition contest finished more than *some* days before
        if not is_group_contest:
            if not contest.__contains__('relativeTimeSeconds') or int(contest['relativeTimeSeconds']) - int(contest['durationSeconds']) <= int(self.config["codeforces"]["public_contest_postprocess_delay"]) / 1000:
                return False
        else:
            if not contest.__contains__('relativeTimeSeconds') or int(contest['relativeTimeSeconds']) - int(contest['durationSeconds']) <= int(self.config["codeforces"]["private_contest_postprocess_delay"]) / 1000:
                return False
        # condition contest finished less than *some* days before
        if int(contest['relativeTimeSeconds']) - int(contest['durationSeconds']) >= int(self.config["codeforces"]["not_proceed_contests_after"]) / 1000:
            return False
        
        # condition exists at least one rating changes
        rating_changes_request = requests.get(f"https://codeforces.com/api/contest.ratingChanges?contestId={contest['id']}").json()
        if not is_group_contest and rating_changes_request["status"] != 'OK':
            return False
        if not is_group_contest and len(list(rating_changes_request["result"])) <= 0:
            return False

        return True

    @staticmethod
    def calculate_contest_coefficient(contest):
        # 1 - Div4; 1.5 - Div3; 2 - Div2; 2.5 - Div1+Div2; 3 - Div1

        if str(contest["name"]).find("Horse.Run()") != -1:
            return 3
        if str(contest["name"]).find("{HORSE} Marathon") != -1:
            return 1.5
        if str(contest["name"]).find("Div. 1 + Div. 2") != -1:
            return 2.5
        if str(contest["name"]).find("Div. 1") != -1:
            return 3
        if str(contest["name"]).find("Div. 2") != -1:
            return 2
        if str(contest["name"]).find("Div. 3") != -1:
            return 1.5
        if str(contest["name"]).find("Div. 4") != -1:
            return 1
        
        return None
    
    @staticmethod
    def filter_for_participants(participant_info: dict):
        problems_results = list(participant_info["problemResults"])
        is_solve_at_least_one_problem = False
        for problem_results in problems_results:
            is_solve_at_least_one_problem |= (int(problem_results["points"]) > 0)
        return is_solve_at_least_one_problem

    def calculate_reward(self, contest: dict, registered_users_with_handle: dict, group_code: str | None = None):
        # (P - S + 1) / P * K * 100 / M
        # P - кількість учасників у змаганні загалом
        # S - позиція учасника в рейтингу
        # M - кількість учасників у команді користувача
        # K - коефіцієнт, який залежить від рівня контесту
        request = f"contestId={contest['id']}&showUnofficial=false"
        if group_code is not None:
            request += f"&groupCode={group_code}"
        all_participants = list(filter(self.filter_for_participants, list(requests.get(self.sign_request("contest.standings", request)).json()["result"]["rows"])))

        P = len(all_participants)
        K = self.calculate_contest_coefficient(contest)
        logging.debug(f"CODEFORCES_SERVICE: Processing contest {contest['name']} from group {group_code} with K = {K} and P = {P}")
        if K is None:
            return

        for participant_info in all_participants:
            S = int(participant_info["rank"])

            party = list(participant_info["party"]["members"])
            M = len(party)

            handles = []
            for party_member in party:
                handles.append(party_member["handle"])

            for handle in handles:
                if not (registered_users_with_handle.get(handle) is not None):
                    continue

                is_handle_proceeded = self.database_worker.find_one("proceeded-results", {
                    "platform": "codeforces", 
                    "contestId": contest['id'], 
                    "proceeded_handle": handle 
                }, self.ray_id)
                if is_handle_proceeded is not None:
                    continue

                reward_amount = (((P - S + 1.) / P) ** 3 * K * 10.) / M
                self.database_worker.insert_one('proceeded-results', {
                    "platform": "codeforces", 
                    "contestId": contest['id'], 
                    "proceeded_handle": handle
                }, self.ray_id)
                self.users_service.give_tokens(registered_users_with_handle[handle], reward_amount, f"You received {reward_amount} HORSE for your performance in {contest['name']}. Congratulations!", self.ray_id)

                logging.debug(f"CODEFORCES_SERVICE: User {registered_users_with_handle[handle]} with handle {handle} received {reward_amount} for his performance in contest {contest['name']}")

    def mainloop(self):
        while True:
            try:
                groups = self.database_worker.find('contest-groups', {
                    "platform": "codeforces"
                }, self.ray_id)
                for group_code in [group["groupCode"] for group in groups]+[None]:
                    logging.debug(f"CODEFORCES_SERVICE: Processing group {group_code}")

                    all_contests_list = self.get_contests(group_code)
                    contests_to_process = list(filter(lambda contest : self.filter_for_contests(contest, group_code is not None), all_contests_list))
                    logging.debug("CODEFORCES_SERVICE: Contests to process: " + str(contests_to_process))

                    registered_users_with_handle_dict = self.get_registered_users_with_handle()

                    for contest in contests_to_process:
                        self.calculate_reward(contest, registered_users_with_handle_dict, group_code)

                time.sleep(int(self.config['codeforces']['refresh_contests_results_cooldown']) / 1000)
            except Exception as e:
                logging.error(f"CODEFORCES_SERVICE: {e.with_traceback(None)}")
                time.sleep(60)
