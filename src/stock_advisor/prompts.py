import re
from typing import List, Union
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.agents import Tool


class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]

    def format(self, **kwargs):  # type: ignore[override]
        steps = kwargs.pop("intermediate_steps", [])
        scratch = ""
        for action, obs in steps:
            scratch += action.log + f"\nObservation: {obs}\nThought: "
        kwargs.update(
            {
                "agent_scratchpad": scratch,
                "tools": "\n".join(f"{t.name}: {t.description}" for t in self.tools),
                "tool_names": ", ".join(t.name for t in self.tools),
            }
        )
        return self.template.format(**kwargs)


from langchain.agents.agent import AgentOutputParser

class CustomOutputParser(AgentOutputParser):
    """Parse LLM output into AgentAction or AgentFinish (ReAct style)."""

    def parse(self, text: str):           # type: ignore[override]
        if "Final Answer:" in text:
            return AgentFinish(
                return_values={"output": text.split("Final Answer:")[-1].strip()},
                log=text,
            )

        m = re.search(r"Action: (.*?)\s*Action Input: (.*)", text, re.DOTALL)
        print("---- LLM OUTPUT ----")
        print(text)
        print("--------------------")

        if not m:
            raise ValueError(f"Cannot parse LLM output: {text}")

        return AgentAction(
            tool=m.group(1).strip(),
            tool_input=m.group(2).strip().strip('"'),
            log=text,
        )

    # Required by AgentOutputParser
    @property
    def _type(self) -> str:
        return "stock_advisor_custom"



PROMPT_TEMPLATE = PROMPT_TEMPLATE = """You are StockSage, an AI market research assistant.
Goal: produce a concise daily brief with:
  1. Top macro stories (3‑5 bullets)
  2. Notable company news & sentiment
  3. 3‑5 trade ideas (ticker, entry, thesis, risk, timeframe)
  
Rules:
- Call each tool only ONCE per information category
- After gathering data, synthesize it into a final answer
- Never repeat the same tool call with identical inputs
- Finish with: "This is educational, not investment advice."

Available tools:
{tools}

Format:
Question: {input}
Thought: ...
Action: one of [{tool_names}]
Action Input: ...
Observation: ...
... (repeat as needed)
When ready to answer:
Thought: I now know the final answer  
Final Answer: <markdown format>

Question: {input}
{agent_scratchpad}"""
