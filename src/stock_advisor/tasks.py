import logging
from .agent import create_agent

logger = logging.getLogger(__name__)
_agent = create_agent()

def generate_daily_brief() -> str:
    try:
        result = _agent.agent.plan(
            {"input": "Generate today's US stock market brief."},
            intermediate_steps=[],
        )
        return result.return_values["output"]
    except Exception as exc:
        logger.error("Agent error: %s", exc)
        return "Agent failed to generate brief."

