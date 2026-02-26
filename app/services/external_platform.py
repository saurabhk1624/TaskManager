from abc import ABC, abstractmethod
from typing import Optional

from github import Github
from pydantic import BaseModel
import anyio

from app.core.config import Settings
from app.models.task import Task
from app.repository.task_repository import TaskRepository


class ExternalPlatformService(ABC):
    @abstractmethod
    async def handle_task_created(self, task: Task) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class GitHubIssuePayload(BaseModel):
    title: str
    body: str


class GitHubExternalPlatformService(ExternalPlatformService):
    """
    Concrete implementation that integrates with GitHub via PyGithub.

    - Creates an issue whenever a task is created.
    - Stores the GitHub issue number in `external_reference_id`.
    - Failures are swallowed so the core API keeps working.
    """

    def __init__(self, settings: Settings, repository: TaskRepository) -> None:
        self._settings = settings
        self._repository = repository

    def _build_payload(self, task: Task) -> GitHubIssuePayload:
        body_lines = [
            f"Task ID: {task.id}",
            f"Title: {task.title}",
            f"Priority: {task.priority}",
            f"Completed: {task.is_completed}",
        ]
        if task.description:
            body_lines.append("")
            body_lines.append(task.description)
        return GitHubIssuePayload(title=task.title, body="\n".join(body_lines))

    async def _create_issue_sync(self, payload: GitHubIssuePayload) -> Optional[int]:
        """
        Runs the synchronous PyGithub client in a thread to avoid
        blocking the event loop.
        """
        def _create() -> Optional[int]:
            gh = Github(self._settings.github_token)
            repo = gh.get_repo(self._settings.github_repo)
            issue = repo.create_issue(title=payload.title, body=payload.body)
            return issue.number

        return await anyio.to_thread.run_sync(_create)

    async def handle_task_created(self, task: Task) -> None:
        print("🔥 Background triggered for task:", task.id)

        payload = self._build_payload(task)
        try:
            issue_number = await self._create_issue_sync(payload)
            print("✅ Issue created:", issue_number)
            if issue_number is not None:
                updated = await self._repository.set_external_reference(
                    task_id=task.id, reference_id=str(issue_number)
                )
                print("📌 Update result:", updated)
        except Exception as e:
            print("GitHub issue creation failed:", e)
            return

