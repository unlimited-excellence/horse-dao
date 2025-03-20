import logging
import time
import requests

from database.database_worker import DatabaseWorker
from services.UsersService import UsersService

class CodeforcesService:
    def __init__(self, database_worker: DatabaseWorker, users_service: UsersService, config: dict):
        self.database_worker = database_worker
        self.users_service = users_service
        self.config = config


    def get_contests(self):
        contest_list_response = requests.get(f"https://codeforces.com/api/contest.list?gym=false")
        contest_list_response_dict = contest_list_response.json()
        contest_list = list(contest_list_response_dict['result'])
        return contest_list

    def get_registered_users_with_handle(self):
        registered_users_with_handle = self.database_worker.find('users', {
            'codeforces.handle': {
                '$exists': True
            }
        })
        registered_users_with_handle_dict = {}
        for registered_user_with_handle in registered_users_with_handle:
            registered_users_with_handle_dict[registered_user_with_handle['codeforces']['handle']] = registered_user_with_handle['userId']
        return registered_users_with_handle_dict

    def filter_for_contests(self, contest: dict):
        # condition contest finished
        if str(contest["phase"]) != "FINISHED":
            return False
        
        # condition contest finished more than *some* days before
        if int(contest['relativeTimeSeconds']) - int(contest['durationSeconds']) <= int(self.config["codeforces"]["proceed_contests_after"]) / 1000:
            return False
        
        # condition contest finished less than *some* days before
        if int(contest['relativeTimeSeconds']) - int(contest['durationSeconds']) >= int(self.config["codeforces"]["not_proceed_contests_after"]) / 1000:
            return False
        
        # condition exists at least one rating changes
        rating_changes_request = requests.get(f"https://codeforces.com/api/contest.ratingChanges?contestId={contest['id']}").json()
        if rating_changes_request["status"] != 'OK':
            return False
        if len(list(rating_changes_request["result"])) <= 0:
            return False

        return True

    def calculate_contest_coefficient(self, contest):
        # 1 - Div4; 1.5 - Div3; 2 - Div2; 2.5 - Div1+Div2; 3 - Div1

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
    
    def filter_for_participants(self, participant_info: dict):
        problems_results = list(participant_info["problemResults"])
        is_solve_at_least_one_problem = False
        for problem_results in problems_results:
            is_solve_at_least_one_problem |= (int(problem_results["points"]) > 0)
        return is_solve_at_least_one_problem

    def calculate_reward(self, contest: list, registered_users_with_handle: dict):
        # (P - S + 1) / P * K * 100 / M
        # P - кількість учасників у змаганні загалом
        # S - позиція учасника в рейтингу
        # M - кількість учасників у команді користувача
        # K - коефіцієнт, який залежить від рівня контесту
        all_participants = list(filter(self.filter_for_participants, list(requests.get(f"https://codeforces.com/api/contest.standings?contestId={contest['id']}&showUnofficial=false").json()["result"]["rows"])))

        P = len(all_participants)
        K = self.calculate_contest_coefficient(contest)
        logging.debug(f"CODEFORCES_SERVICE: Proceeding contest {contest['name']} with K = {K} and P = {P}")
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
                })
                if is_handle_proceeded is not None:
                    continue

                reward_amount = (((P - S + 1.) / P) * K * 100.) / M
                self.database_worker.insert_one('proceeded-results', {
                    "platform": "codeforces", 
                    "contestId": contest['id'], 
                    "proceeded_handle": handle
                })
                self.users_service.give_tokens(registered_users_with_handle[handle], reward_amount, f"You received {reward_amount} HORSE for your performance in {contest['name']}. Congratulations!")

                logging.debug(f"CODEFORCES_SERVICE: User {registered_users_with_handle[handle]} with handle {handle} received {reward_amount} for his performance in contest {contest['name']}")
        

    def mainloop(self):
        while True:
            try:
                all_contests_list = self.get_contests()
                contests_to_process = list(filter(self.filter_for_contests, all_contests_list))

                logging.info(contests_to_process)

                registered_users_with_handle_dict = self.get_registered_users_with_handle()

                for contest in contests_to_process:
                    self.calculate_reward(contest, registered_users_with_handle_dict)

                time.sleep(int(self.config['codeforces']['refresh_contests_results_cooldown']) / 1000)
            except Exception as e:
                logging.error(f"CODEFORCES_SERVICE: {e}")
                time.sleep(60)
