"""CLI entry‑point.
Run once:      python -m stock_advisor.main
Daemon mode:   python -m stock_advisor.main --schedule 09:00
"""

import argparse
import logging
from .tasks import generate_daily_brief
from .scheduler import schedule_daily
from .slack import post_to_slack  # New import

# Update your logging config at the top of main.py
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_advisor.log'),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)

def _parse_time(s: str):
    """Parse HH:MM time string into hours and minutes."""
    h, m = map(int, s.split(":"))
    return h, m

# Update your _generate_and_post function in main.py
def _generate_and_post():
    """Generate brief and post to Slack, returns brief text."""
    try:
        # Generate the brief
        result = generate_daily_brief()
        
        # Handle both dict and str outputs
        brief = result.get("output") if isinstance(result, dict) else result
        logger.info("Successfully generated daily brief")
        
        # Debug: Print brief to verify content
        logger.debug(f"Brief content: {brief[:200]}...")  # Log first 200 chars
        
        # Post to Slack with error handling
        try:
            if post_to_slack(brief):
                logger.info("Posted daily brief to Slack successfully")
            else:
                logger.warning("Failed to post to Slack - check webhook configuration")
                # Fallback: Print to console if Slack fails
                print("Slack post failed. Brief content:")
                print(brief)
        except Exception as slack_error:
            logger.error(f"Slack posting error: {str(slack_error)}")
            raise
        
        return brief
    except Exception as e:
        logger.error(f"Error generating brief: {str(e)}")
        # Attempt to post error to Slack
        error_msg = "⚠️ Failed to generate market brief. Check logs for details."
        post_to_slack(error_msg)
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
