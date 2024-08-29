import os
from langchain_core.tools import tool, BaseTool
from langchain_community.utilities import SQLDatabase
from pydantic import BaseModel
import gitlab
from langchain_community.utilities.gitlab import GitLabAPIWrapper

GITLAB_URL = os.environ["GITLAB_URL"]
GITLAB_PERSONAL_ACCESS_TOKEN = os.environ["GITLAB_PERSONAL_ACCESS_TOKEN"]
GITLAB_REPOSITORY = os.environ["GITLAB_REPOSITORY"]
GITLAB_BRANCH = os.environ["GITLAB_BRANCH"]
GITLAB_BASE_BRANCH = os.environ["GITLAB_BASE_BRANCH"]
GITLAB_PROJECT_ID = os.environ["GITLAB_PROJECT_ID"]


class GitlabTools:
    def __init__(self):
        self.gitlab_url = GITLAB_URL
        self.gitlab = gitlab.Gitlab(
            GITLAB_URL, private_token=GITLAB_PERSONAL_ACCESS_TOKEN
        )
        self.project = self.gitlab.projects.get(GITLAB_PROJECT_ID)
        self.gitlab_api_wrapper = GitLabAPIWrapper(
            gitlab=GITLAB_URL,
            gitlab_base_branch=GITLAB_BASE_BRANCH,
            gitlab_branch=GITLAB_BRANCH,
            gitlab_repository=GITLAB_REPOSITORY,
            gitlab_personal_access_token=GITLAB_PERSONAL_ACCESS_TOKEN,
        )

    def print_repo_tree(self, path="", prefix=""):
        # Fetch the repository tree at the given path
        items = self.project.repository_tree(path=path, recursive=False)

        # Separate directories and files
        directories = [item for item in items if item["type"] == "tree"]
        files = [item for item in items if item["type"] == "blob"]

        # Print directories first
        for directory in directories:
            print(directory)
            # print(f"{prefix}{directory['name']}/")

            self.print_repo_tree(path=directory["path"], prefix=prefix + "    ")

        # Print files
        for file in files:
            print(f"{prefix}{file['name']}")
