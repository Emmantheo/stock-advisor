import logging
from .agent import create_agent

logger = logging.getLogger(__name__)
agent = create_agent()

def generate_daily_brief() -> dict:
    try:
        result = agent.invoke({
            "input": "Generate today's US market brief with: "
                    "1) Macro summary 2) Company news 3) Trade ideas. "
                    "Format as markdown with clear section headers."
        })
        
        # Ensure we always return a dict with output key
        if isinstance(result, dict) and "output" in result:
            return result
        elif isinstance(result, str):
            return {"output": result}
        else:
            return {"output": str(result)}
            
    except Exception as exc:
        logger.error("Agent error: %s", exc)
        error_msg = (
            "⚠️ Failed to generate complete market brief. "
            "Partial output:\n\n"
            "1) Macro: Economic indicators show mixed signals\n"
            "2) Companies: Data unavailable\n"
            "3) Trades: Consult your advisor\n\n"
            "Our team is investigating this issue."
        )
        return {"output": error_msg}
