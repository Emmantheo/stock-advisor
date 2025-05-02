import os
import re
from typing import List
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain_core.runnables import RunnableSequence
from langchain_community.llms import AzureOpenAI
from langchain.chains import LLMChain  # ← restore this
from langchain_core.prompts import StringPromptTemplate

from .tools import TOOLS
from .prompts import PROMPT_TEMPLATE, CustomPromptTemplate, CustomOutputParser

def _create_llm(temperature: float = 0.1) -> AzureOpenAI:
    """Instantiate an AzureOpenAI LLM using env vars for config."""
    return AzureOpenAI(
        temperature=temperature,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )

def create_agent(temperature: float = 0.1) -> AgentExecutor:
    llm = _create_llm(temperature)

    prompt = CustomPromptTemplate(
        template=PROMPT_TEMPLATE,
        tools=TOOLS,
        input_variables=["input", "agent_scratchpad"],  # ✅ intermediate_steps removed
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt)  # ← revert back

    agent = ZeroShotAgent(
        llm_chain=llm_chain,
        allowed_tools=[t.name for t in TOOLS],
        output_parser=CustomOutputParser(),
    )


    return AgentExecutor(agent=agent, tools=TOOLS, verbose=False)
