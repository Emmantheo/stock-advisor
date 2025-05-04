import os
import json
import requests
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def post_to_slack(message: str) -> bool:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.error("Slack webhook URL not configured")
        return False

    # Parse the markdown content into Slack blocks
    blocks = []
    
    # Add header section
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "📈 Daily Market Brief",
            "emoji": True
        }
    })
    
    # Add divider
    blocks.append({"type": "divider"})
    
    # Process each section
    current_section = None
    for line in message.split('\n'):
        line = line.strip()
        
        # Handle main headers
        if line.startswith("# Market Brief"):
            continue  # Skip redundant title
            
        elif line.startswith("## Key Macroeconomic Developments"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Key Macroeconomic Developments*"
                }
            })
            
        elif line.startswith("## Notable Company News"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏢 Notable Company News*"
                }
            })
            
        elif line.startswith("## Actionable Trade Ideas"):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*💡 Actionable Trade Ideas*"
                }
            })
            
        # Process bullet points
        elif line.startswith(("1.", "2.", "3.", "- **")):
            if not current_section:
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": ""}})
                current_section = blocks[-1]
            
            current_section["text"]["text"] += f"{line}\n"
            
        # Process company news headers
        elif line.startswith("### "):
            company = line[4:].split(" (")[0]
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{company}*"
                }
            })
            
    # Add footer and disclaimer
    blocks.extend([
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "📅 " + datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "type": "mrkdwn",
                    "text": "_This is educational, not investment advice._"
                }
            ]
        }
    ])
    
    payload = {
        "blocks": blocks,
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
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Slack post failed: {str(e)}")
        return False
