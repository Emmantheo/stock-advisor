import re
from datetime import datetime
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.agents import Tool

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
        text = text.strip()
        if "Final Answer:" in text:
            final = text.split("Final Answer:")[-1].strip()
            return AgentFinish(
                return_values={"output": self._format_output(final)},
                log=text,
            )
        
        match = re.search(r"Action: (.*?)\s*Action Input: (.*)", text, re.DOTALL)
        if not match:
            raise ValueError(f"Cannot parse: {text}")
            
        return AgentAction(
            tool=match.group(1).strip(),
            tool_input=match.group(2).strip().strip('"'),
            log=text,
        )

    def _format_output(self, text: str) -> str:
        text = re.sub(r'(Thought:|Action:|Observation:).*?$', '', text, flags=re.MULTILINE)
        return f":chart_with_upwards_trend: *Market Brief - {datetime.now().strftime('%Y-%m-%d')}*\n\n{text.strip()}\n\n_This is educational, not investment advice._"

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
