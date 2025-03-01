import logging
import time
import requests

from database.database_worker import DatabaseWorker

class CodeforcesService:
    def __init__(self, database_worker: DatabaseWorker):
        self.database_worker = database_worker

           

        
    def run():
        while True:
            try:
                contest_list_response = requests.get(f"https://codeforces.com/api/contest.list?gym=false")
                contest_list_response_dict = contest_list_response.json()
                contest_list = list(contest_list_response_dict['result'])
                
                for contest in contest_list:
                    if contest["phase"] != "FINISHED":
                        continue
                
                    contest_info = self.databaseWorker.find_one('codeforces-contests', {
                        "id": str(contest["id"]),
                        "status": "PROCEEDED"
                    })

                    if contest_info is not None:
                        continue
                    
                    # (P - S + 1) / P * K * 100 / M
                    # P - кількість учасників у змаганні загалом
                    # S - позиція учасника в рейтингу
                    # M - кількість учасників у команді користувача
                    # K - коефіцієнт, який в залежності від рівня контесту становить: 1 - Div4; 1.5 - Div3; 2 - Div2; 2.5 - Div1+Div2; 3 - Div1

            except Exception as e:
                logging.error(e)

            time.sleep(1 * 60)
        