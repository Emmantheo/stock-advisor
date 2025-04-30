import logging
from .agent import create_agent

logger = logging.getLogger(__name__)
_agent = create_agent()

def generate_daily_brief() -> str:
    try:
        result = _agent.invoke({
            "input": "Generate today's US stock market brief.",
            "intermediate_steps": [],  # Required for ZeroShotAgent to start clean
        })
        return result["output"]
    except Exception as exc:
        logger.error("Agent error: %s", exc)
        return "Agent failed to generate brief."

        return "Agent failed to generate brief."

