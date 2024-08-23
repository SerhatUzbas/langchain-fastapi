import json
import os
import bs4

from langchain_community.chat_models import ChatOllama

import os

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper
from langchain_openai import OpenAI


class GitlabAgent:
    def __init__(self):
        self.llm = ChatOllama(model="llama3")
        self.gitlab = GitLabAPIWrapper()
        self.toolkit = GitLabToolkit.from_gitlab_api_wrapper(self.gitlab)

        self.agent = initialize_agent(
            self.toolkit.get_tools(),
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

    def execute(self):
        self.agent.run()
