import logging
from .agent import create_agent

logger = logging.getLogger(__name__)
agent = create_agent()

def generate_daily_brief() -> dict:
    try:
        result = agent.invoke({
            "input": (
                "Generate today's comprehensive US market brief with:\n"
                "1) 3-5 key macroeconomic developments\n"
                "2) Notable company news with sentiment analysis\n"
                "3) 3 actionable trade ideas with rationale\n\n"
                "Format as markdown with clear section headers.\n"
                "Include specific data points and sources when available."
            )
        })
        
        # Validate the output structure
        if isinstance(result, dict) and "output" in result:
            output = result["output"]
            if all(section in output for section in ["Macroeconomic", "Company News", "Trade Ideas"]):
                return result
            else:
                logger.warning("Incomplete brief generated")
                return {
                    "output": (
                        "⚠️ Partial Market Brief\n\n"
                        "We're experiencing partial data availability today:\n\n"
                        f"{output}\n\n"
                        "Our team is working to restore full service."
                    )
                }
        else:
            raise ValueError("Unexpected agent response format")
            
    except Exception as exc:
        logger.error("Agent execution failed: %s", str(exc))
        return {
            "output": (
                "🚨 We're unable to generate today's market brief due to a system error.\n"
                "Our engineering team has been alerted and is working on a solution.\n\n"
                "Please check back later or contact support for assistance."
            )
        }
