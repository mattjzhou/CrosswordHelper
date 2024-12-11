import asyncio
import logging

import azure.functions as func
from crosswordscraper import CrosswordScraper

app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 0 4 * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def crosswordfunction(myTimer: func.TimerRequest) -> None:

    logging.info("Starting Crossword Scraper")
    try:
        scraper = CrosswordScraper()
        asyncio.run(scraper.run())
    except Exception as e:
        logging.critical(e, exc_info=True)

    logging.info("Python timer trigger function executed.")
