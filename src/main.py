"""CLI entry‑point.
Run once:      python -m stock_advisor.main
Daemon mode:   python -m stock_advisor.main --schedule 09:00
"""

import argparse
from .tasks import generate_daily_brief
from .scheduler import schedule_daily


def _parse_time(s: str):
    h, m = map(int, s.split(":"))
    return h, m


def cli():
    p = argparse.ArgumentParser(description="Stock Advisor Agent")
    p.add_argument("--schedule", help="HH:MM daily run time (24h)")
    args = p.parse_args()

    if args.schedule:
        h, m = _parse_time(args.schedule)
        schedule_daily(h, m)
    else:
        print(generate_daily_brief())


if __name__ == "__main__":
    cli()