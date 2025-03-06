import logging
import time
import requests

from database.database_worker import DatabaseWorker

class CodeforcesService:
    def __init__(self, database_worker: DatabaseWorker, time_between_updates: int):
        self.database_worker = database_worker
        self.time_between_updates = time_between_updates

           
    def get_all_contests(self):
        contest_list = None
        try:
            contest_list_response = requests.get(f"https://codeforces.com/api/contest.list?gym=false")
            contest_list_response_dict = contest_list_response.json()
            contest_list = list(contest_list_response_dict['result'])
        except Exception as e:
            logging.error(e)
        
        return contest_list
        
    def filter_for_contest(contest):
        # condition contest finished
        if !(contest["type"] == "FINISHED"):
            return false
        
        # condition contest finished more than 3 days before
        if !(contest['relativeTimeSeconds'] > 3 * 24 * 60 * 60):
            return false
        
        # condition contest finished less than 7 days before
        if !(contest['relativeTimeSeconds'] < 7 * 24 * 60 * 60):
            return false
        
        # condition exist at least one rating changes
        rating_changes_request = requests.get(f"https://codeforces.com/api/contest.ratingChanges?contestId={contest['id']}").json()
        if !(len(list(rating_changes_request["result"])) > 0):
            return false

        return true

    def calculate_contest_coefficient(self, contest):
        # 1 - Div4; 1.5 - Div3; 2 - Div2; 2.5 - Div1+Div2; 3 - Div1

        if (str(contest["name"]).find("Div. 1 + Div. 2") != -1):
            return 2.5
        
        if (str(contest["name"]).find("Div. 1") != -1):
            return 3
        
        if (str(contest["name"]).find("Div. 2") != -1):
            return 2
        
        if (str(contest["name"]).find("Div. 3") != -1):
            return 1.5
        
        if (str(contest["name"]).find("Div. 4") != -1):
            return 1
        
        return None
        

    def calculate_reward(self, constest):
        # (P - S + 1) / P * K * 100 / M
        # P - кількість учасників у змаганні загалом
        # S - позиція учасника в рейтингу
        # M - кількість учасників у команді користувача
        # K - коефіцієнт, який в залежності від рівня контесту 1 - Div4; 1.5 - Div3; 2 - Div2; 2.5 - Div1+Div2; 3 - Div1
        all_participants = list(requests.get(f"https://codeforces.com/api/contest.standings?contestId={contest['id']}&showUnofficial=false").json()["result"]["rows"])

        P = len(all_participants)
        K = self.calculate_contest_coefficient()

        if K is None:
            return []

        reward = []
        for participant_info in all_participants:
            S = int(participant_info["rank"])

            party = list(participant_info["party"]["members"])
            M = len(party)

            handles = []
            for party_member in party:
                handles.append(party_member["handle"])
            
            for handle in handles:
                db_record = self.database_worker.find_one("proceeded-results", {
                    "platform": "codeforces", 
                    "contestId": contest['id'], 
                    "proceeded_handle": handle 
                })

                if db_record is not None:
                    reward.append((handle, (((P - S + 1.) / P) * K * 100.) / M))
            
            return reward
            


        

    def mainloop(self):
        while True:
            all_contests_list = self.get_all_contest()
            contests_to_process = filter(filter_for_contests, all_contests_list)

            total_reward = []
            for contest in contest_to_process:
                total_reward.extend(self.calculate_reward(contest))

            # todo adding real reward

            time.sleep(self.time_between_updates)
        


"""
# (P - S + 1) / P * K * 100 / M
# P - кількість учасників у змаганні загалом
# S - позиція учасника в рейтингу
# M - кількість учасників у команді користувача
# K - коефіцієнт, який в залежності від рівня контесту становить: 1 - Div4; 1.5 - Div3; 2 - Div2; 2.5 - Div1+Div2; 3 - Div1
 """