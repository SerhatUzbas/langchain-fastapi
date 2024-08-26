import os
from langchain_community.chat_models import ChatOllama
import os

from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper
from langchain_openai import ChatOpenAI, OpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from langchain_experimental.llms.ollama_functions import OllamaFunctions

GITLAB_URL = os.environ["GITLAB_URL"]
GITLAB_PERSONAL_ACCESS_TOKEN = os.environ["GITLAB_PERSONAL_ACCESS_TOKEN"]
GITLAB_REPOSITORY = os.environ["GITLAB_REPOSITORY"]
GITLAB_BRANCH = os.environ["GITLAB_BRANCH"]
GITLAB_BASE_BRANCH = os.environ["GITLAB_BASE_BRANCH"]

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class GitlabAgent:
    def __init__(self):
        self._system_message = SystemMessage(
            content="""
            You have the software engineering capabilities of a Google Principle engineer. 
            You are tasked with get request from users about repository and solve the problems based on request. 
            You MUST find the what the problem is, locate the error (or code which must be changed) and fix (or refactor it) through user request.
            At last, you must open merge request which contains your changes to merge base branch.
            """
        )
        self.gitlab = GitLabAPIWrapper(
            gitlab=GITLAB_URL,
            gitlab_base_branch=GITLAB_BASE_BRANCH,
            gitlab_branch=GITLAB_BRANCH,
            gitlab_repository=GITLAB_REPOSITORY,
            gitlab_personal_access_token=GITLAB_PERSONAL_ACCESS_TOKEN,
        )
        self.toolkit = GitLabToolkit.from_gitlab_api_wrapper(self.gitlab)

        for tool in self.toolkit.get_tools():
            tool.name = tool.name.replace(" ", "_").replace("-", "_")

        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

        self.agent = create_react_agent(
            tools=self.toolkit.get_tools(),
            model=self.llm,
            state_modifier=self._system_message,
        )

    def execute(self, question):
        print(question, "not stream")
        print(GITLAB_BASE_BRANCH, "gitlab")
        print(GITLAB_URL, "gitlab")
        # result = self.agent.invoke({"messages": question})
        for chunk in self.agent.stream({"messages": question}):
            print(chunk, "chunk")

    async def stream(self, question):
        print(question, "questionquestionquestionquestionquestion")

        async for chunk in self.agent.astream({"messages": question}):
            if "answer" in chunk:
                yield chunk["answer"]
