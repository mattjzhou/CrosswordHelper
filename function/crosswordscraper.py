import asyncio
import logging
import os
from datetime import date, timedelta

import pandas as pd
import tqdm
import tqdm.asyncio
from aiohttp import ClientSession
from sqlalchemy import create_engine
from utils import getUrl, initLogger

log = initLogger(module="crosswordscraper", level=logging.INFO)

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
driver = "ODBC+Driver+18+for+SQL+Server"


class CrosswordScraper:
    def __init__(self):
        self.clues = []

    async def run(self):
        start = date.today() + date.timedelta(days=1)  # date(1993, 11, 21)
        end = date.today() + date.timedelta(days=1)
        dates = [start + timedelta(days=x) for x in range((end - start).days + 1)]
        tasks = []
        responses = []
        async with ClientSession() as session:
            for d in dates:
                tasks.append(asyncio.ensure_future(self.get(session, d)))
            responses = await tqdm.asyncio.tqdm.gather(*tasks)
        for response, d in tqdm.tqdm(zip(responses, dates)):
            self.process(response, d)
        self.save_to_sql()

    async def get(self, session, date):
        params = {}
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:128.0) Gecko/20100101 Firefox/128.0",
            "X-Games-Auth-Bypass": "true",
        }
        url = f"https://www.nytimes.com/svc/crosswords/v6/puzzle/daily/{date}.json"
        return await getUrl(
            log, session, url, params=params, headers=headers, json=True
        )

    def process(self, data, date: date):
        for clue in data["body"][0]["clues"]:
            try:
                clue_text = clue["text"][0]["plain"]
            except KeyError as e:
                log.warning(
                    f"Abnormal Clue: {clue['text'][0]}, Received KeyError {e}, Skipping clue..."
                )
                continue
            except Exception as e:
                log.warning(f"Abnormal Clue: {clue['text'][0]}, Skipping clue...")
                log.warning(e, exc_info=True)
                continue
            answer = ""
            abnormal = False
            for cell in clue["cells"]:
                try:
                    answer += data["body"][0]["cells"][cell]["answer"]
                except KeyError as e:
                    abnormal = True
                    log.warning(
                        f"Abnormal Cell: {data['body'][0]['cells'][cell]}, Received KeyError {e}, Skipping clue..."
                    )
                except Exception as e:
                    abnormal = True
                    log.warning(
                        f"Abnormal Cell: {data['body'][0]['cells'][cell]}, Skipping clue..."
                    )
                    log.warning(e, exc_info=True)
                    break
            if abnormal:
                continue
            self.clues.append(
                (clue_text, answer, len(answer), str(date), date.weekday())
            )

    def save_to_sql(self):
        clues_df = pd.DataFrame(
            self.clues, columns=["clue", "answer", "answer_len", "date", "weekday"]
        )
        connection_url = (
            f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
        )
        engine = create_engine(connection_url)
        clues_df.to_sql("clues", engine, if_exists="append", index=False)


if __name__ == "__main__":
    log.info("Starting Crossword Scraper")
    try:
        scraper = CrosswordScraper()
        asyncio.run(scraper.run())
    except Exception as e:
        log.critical(e, exc_info=True)
