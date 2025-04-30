import logging
from .agent import create_agent

logger = logging.getLogger(__name__)
_agent = create_agent()


def generate_daily_brief() -> str:
    """Run the agent to generate today's market brief."""
    try:
        return _agent.invoke({"input": "Generate today's US stock market brief."})

    except Exception as exc:
        logger.error("Agent error: %s", exc)
        return "Agent failed to generate brief."
