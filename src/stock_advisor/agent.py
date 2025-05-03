import os
import re
from typing import List
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain_core.runnables import RunnableSequence
from langchain_community.llms import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from langchain.chains import LLMChain  # ← restore this
from langchain_core.prompts import StringPromptTemplate

from .tools import TOOLS
from .prompts import PROMPT_TEMPLATE, CustomPromptTemplate, CustomOutputParser

import os
import re
from typing import List
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain_core.runnables import RunnableSequence
from langchain_community.llms import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from langchain.chains import LLMChain  # ← restore this
from langchain_core.prompts import StringPromptTemplate

from .tools import TOOLS
from .prompts import PROMPT_TEMPLATE, CustomPromptTemplate, CustomOutputParser

def _create_llm(temperature: float = 0.1) -> AzureOpenAI:
    """Instantiate an AzureOpenAI LLM using env vars for config."""
    return AzureChatOpenAI(
        temperature=temperature,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_COMPLETION_MODEL_NAME"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )

def create_agent(temperature: float = 0.1) -> AgentExecutor:
    llm = _create_llm(temperature)

    prompt = CustomPromptTemplate(
        template=PROMPT_TEMPLATE,
        tools=TOOLS,
        input_variables=["input", "agent_scratchpad"],
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt)

    agent = ZeroShotAgent(
        llm_chain=llm_chain,
        allowed_tools=[t.name for t in TOOLS],
        output_parser=CustomOutputParser(),
        stop=["\nObservation:"],  # Add stop sequence
        max_iterations=3,  # Limit iterations per tool
    )

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=5,  # Reduced from 15
        early_stopping_method="generate",  # Add early stopping
    )

