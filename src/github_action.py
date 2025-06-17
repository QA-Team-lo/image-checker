from dataclasses import dataclass
from typing import Optional, List

from github import Github


@dataclass
class Issue:
    title: str
    body: str
    labels: list[str] = None


class GithubRepoManager:
    """
    A class to manage GitHub repositories
    """

    def __init__(self, github_manager: 'GithubManager', repo_name: str):
        """
        Initialize the GitHub repository manager with a GitHub manager and a repository name
        """
        self.github_manager = github_manager
        self.repo_name = repo_name
        self.repo = self.github_manager.g.get_repo(repo_name)

    def create_issue(self, issue: Issue) -> Optional[str]:
        """
        Create an issue in the repository
        """
        try:
            created = self.repo.create_issue(
                title=issue.title,
                body=issue.body,
                labels=issue.labels if issue.labels else []
            )
            return created.html_url
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None

    def get_all_issues(self) -> List[Issue]:
        """
        Get all issues in the repository
        """
        issues = []
        for issue in self.repo.get_issues(state='all'):
            issues.append(Issue(title=issue.title, body=issue.body, labels=[
                          label.name for label in issue.labels]))
        return issues


class GithubManager:
    """
    A class to manage GitHub
    """

    def __init__(self, token: str):
        """
        Initialize the GitHub manager with a token
        """
        self.token = token
        self.g = Github(token)
