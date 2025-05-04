import os
import json
import requests
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def post_to_slack(message: str) -> bool:
    """Post message to Slack with enhanced debugging"""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL environment variable not set!")
        return False
    
    logger.debug(f"Attempting to post to Slack webhook: {webhook_url[:30]}...")  # Log partial URL
    
    if not message or not isinstance(message, str):
        logger.error(f"Invalid message content: {type(message)}")
        return False

    payload = {
        "text": message,
        "username": "Stock Advisor",
        "icon_emoji": ":chart_with_upwards_trend:"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        logger.debug(f"Slack API response: {response.status_code} - {response.text}")
        
        if response.status_code != 200:
            logger.error(f"Slack API error: {response.status_code} - {response.text}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Slack connection failed: {str(e)}")
        return False
