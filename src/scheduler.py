import os
import time
import schedule
import logging
import requests
from tasks import generate_daily_brief

logger = logging.getLogger(__name__)


def post_to_slack(markdown: str):
    hook = os.getenv("SLACK_WEBHOOK_URL")
    if not hook:
        logger.warning("SLACK_WEBHOOK_URL missing – skipping post")
        return
    try:
        requests.post(hook, json={"text": markdown}, timeout=10).raise_for_status()
    except Exception as exc:
        logger.error("Slack error: %s", exc)


def schedule_daily(hour: int = 9, minute: int = 0):
    def job():
        brief = generate_daily_brief()
        post_to_slack(brief)

    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(job)
    logger.info("Scheduled daily brief for %02d:%02d", hour, minute)
    while True:
        schedule.run_pending()
        time.sleep(30)