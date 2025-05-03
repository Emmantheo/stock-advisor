"""CLI entry‑point.
Run once:      python -m stock_advisor.main
Daemon mode:   python -m stock_advisor.main --schedule 09:00
"""

import argparse
import logging
from .tasks import generate_daily_brief
from .scheduler import schedule_daily
from .slack import post_to_slack  # New import

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _parse_time(s: str):
    """Parse HH:MM time string into hours and minutes."""
    h, m = map(int, s.split(":"))
    return h, m

def _generate_and_post():
    """Generate brief and post to Slack, returns brief text."""
    try:
        brief = generate_daily_brief()
        logger.info("Successfully generated daily brief")
        
        # Post to Slack
        if post_to_slack(brief):
            logger.info("Posted daily brief to Slack successfully")
        else:
            logger.warning("Failed to post to Slack (missing webhook?)")
        
        return brief
    except Exception as e:
        logger.error(f"Error generating brief: {str(e)}")
        raise

def cli():
    """Command line interface handler."""
    p = argparse.ArgumentParser(description="Stock Advisor Agent")
    p.add_argument("--schedule", help="HH:MM daily run time (24h)")
    args = p.parse_args()

    if args.schedule:
        h, m = _parse_time(args.schedule)
        logger.info(f"Scheduling daily runs at {h:02d}:{m:02d}")
        
        # Update scheduled task to use new posting function
        schedule_daily(h, m, task=_generate_and_post)
    else:
        # Run once and print to console
        print(_generate_and_post())

if __name__ == "__main__":
    cli()
