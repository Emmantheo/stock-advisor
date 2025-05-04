import re
from datetime import datetime
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.agents import Tool
from typing import List, Union
from langchain.agents.agent import AgentOutputParser


class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]

    def format(self, **kwargs):
        steps = kwargs.pop("intermediate_steps", [])
        scratch = ""
        for action, obs in steps:
            scratch += action.log + f"\nObservation: {obs}\nThought: "
        kwargs.update({
            "agent_scratchpad": scratch,
            "tools": "\n".join(f"{t.name}: {t.description}" for t in self.tools),
            "tool_names": ", ".join(t.name for t in self.tools),
            "current_date": datetime.now().strftime("%Y-%m-%d")
        })
        return self.template.format(**kwargs)

class CustomOutputParser(AgentOutputParser):
    def parse(self, text: str):
        # Clean and normalize the text
        text = text.strip()
        text = re.sub(r'\n+', '\n', text)  # Remove extra newlines
        
        # Check for final answer pattern
        final_markers = [
            "Final Answer:",
            "Here's the market brief:",
            "Market Brief:"
        ]
        
        for marker in final_markers:
            if marker in text:
                content = text.split(marker)[-1].strip()
                return AgentFinish(
                    return_values={"output": self._format_output(content)},
                    log=text
                )
        
        # Check if this looks like a complete brief anyway
        if all(section in text for section in ["Macroeconomic", "Company News", "Trade Ideas"]):
            return AgentFinish(
                return_values={"output": self._format_output(text)},
                log=text
            )
        
        # Handle action parsing
        action_match = re.search(
            r"Action:\s*(.*?)\s*\nAction Input:\s*[\"']?(.*?)[\"']?\s*(?:\n|$)", 
            text, 
            re.DOTALL
        )
        if action_match:
            return AgentAction(
                tool=action_match.group(1).strip(),
                tool_input=action_match.group(2).strip(),
                log=text
            )
        
        # Fallback for unexpected formats
        return AgentFinish(
            return_values={"output": self._format_output(text)},
            log=text
        )

    def _format_output(self, text: str) -> str:
        """Ensure consistent output formatting"""
        # Remove any remaining action/observation artifacts
        text = re.sub(r'^(Thought|Action|Observation):.*$', '', text, flags=re.MULTILINE)
        text = text.strip()
        
        # Add header if missing
        if not text.startswith("# Market Brief"):
            text = f"# Market Brief - {datetime.now().strftime('%Y-%m-%d')}\n\n{text}"
            
        # Ensure proper closing
        if "This is educational" not in text:
            text += "\n\n*This is educational, not investment advice.*"
            
        return text


PROMPT_TEMPLATE = """You are StockSage, an AI market research assistant.
Current Date: {current_date}

Task: Create a daily US market brief with:
1) 3-5 key macroeconomic developments
2) Notable company news with sentiment analysis
3) 3 actionable trade ideas

Rules:
- Call market_news ONCE for macro news using: 'macro|economic indicators'
- Call market_news ONCE for company news using: 'company|<ticker>'
- Analyze sentiment for important company news
- Never repeat the same tool call
- Final answer must be in markdown format

Tools:
{tools}

Begin!

Question: {input}
{agent_scratchpad}"""
