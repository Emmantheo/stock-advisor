import os
import json
import requests
from typing import Dict

def post_to_slack(message: str) -> bool:
    """Post message to Slack via webhook"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return False
    
    payload = {
        "text": message,
        "username": "Stock Advisor",
        "icon_emoji": ":chart_with_upwards_trend:"
    }
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code == 200
    except Exception:
        return False
