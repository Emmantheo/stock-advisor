import logging
from .agent import create_agent

logger = logging.getLogger(__name__)
agent = create_agent()

def generate_daily_brief() -> str:
    try:
        result = agent.run(
            "Generate today's US stock market brief. "
            "Structure: 1) Macro summary 2) Company news 3) Trade ideas. "
            "Use each tool only once per category."
        )
        return result
    except Exception as exc:
        logger.error("Agent error: %s", exc)
        return "Agent failed to generate brief."
