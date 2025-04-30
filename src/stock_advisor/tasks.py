import logging
from .agent import create_agent

logger = logging.getLogger(__name__)
_agent = create_agent()

def generate_daily_brief() -> str:
    try:
        # ✅ Only pass 'input' – AgentExecutor adds intermediate_steps internally
        result = _agent.invoke({"input": "Generate today's US stock market brief."})
        return result["output"]
    except Exception as exc:
        logger.error("Agent error: %s", exc)
        return "Agent failed to generate brief."
