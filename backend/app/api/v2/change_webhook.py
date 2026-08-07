"""
Git Webhook 接收器

职责：
1. 接收 GitLab/GitHub Webhook 事件
2. 过滤触发条件
3. 触发变更分析工作流
"""

from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import structlog

router = APIRouter(prefix="/webhook", tags=["Git Webhook"])
logger = structlog.get_logger()


class GitLabPushEvent(BaseModel):
    """GitLab Push Event"""
    ref: str
    before: str
    after: str
    project_id: int
    project: Dict[str, Any]
    commits: List[Dict[str, Any]]
    repository: Dict[str, Any]
    user_name: Optional[str] = None


class GitLabMergeRequestEvent(BaseModel):
    """GitLab Merge Request Event"""
    object_kind: str
    object_attributes: Dict[str, Any]
    merge_request: Optional[Dict[str, Any]] = None
    project: Dict[str, Any]
    changes: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None


class GitHubPushEvent(BaseModel):
    """GitHub Push Event"""
    ref: str
    before: str
    after: str
    repository: Dict[str, Any]
    commits: List[Dict[str, Any]]
    pusher: Optional[Dict[str, Any]] = None
    sender: Optional[Dict[str, Any]] = None


class GitHubPullRequestEvent(BaseModel):
    """GitHub Pull Request Event"""
    action: str
    number: int
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]
    sender: Optional[Dict[str, Any]] = None


class WebhookResponse(BaseModel):
    """Webhook 响应"""
    status: str
    message: str
    workflow_id: Optional[str] = None


@router.post("/gitlab/push", response_model=WebhookResponse)
async def handle_gitlab_push(
    event: GitLabPushEvent,
    background_tasks: BackgroundTasks
):
    """
    处理 GitLab Push 事件
    
    触发条件：
    1. 分支为 feature/* 或 hotfix/*
    2. 有实际代码变更（非新分支）
    """
    branch = event.ref.replace("refs/heads/", "")
    
    if not _should_trigger(branch):
        return WebhookResponse(
            status="skipped",
            message=f"分支 {branch} 不满足触发条件"
        )
    
    if event.before == "0000000000000000000000000000000000000000":
        return WebhookResponse(
            status="skipped",
            message="新分支，无变更"
        )
    
    from app.services.change_workflow import trigger_change_analysis
    
    workflow_id = await trigger_change_analysis(
        background_tasks=background_tasks,
        project_id=str(event.project_id),
        base_branch="develop",
        compare_branch=branch,
        repo_url=event.project.get("git_http_url", ""),
        commits=[c.get("id") for c in event.commits]
    )
    
    logger.info(
        "gitlab_push_triggered",
        branch=branch,
        project_id=event.project_id,
        workflow_id=workflow_id
    )
    
    return WebhookResponse(
        status="triggered",
        message=f"变更分析已触发，分支：{branch}",
        workflow_id=workflow_id
    )


@router.post("/gitlab/merge_request", response_model=WebhookResponse)
async def handle_gitlab_mr(
    event: GitLabMergeRequestEvent,
    background_tasks: BackgroundTasks
):
    """
    处理 GitLab Merge Request 事件
    
    触发时机：MR 创建或更新时
    门禁：测试通过后才能合并
    """
    attrs = event.object_attributes
    
    state = attrs.get("state", "")
    if state != "opened":
        return WebhookResponse(
            status="skipped",
            message=f"MR 状态为 {state}，不触发分析"
        )
    
    action = attrs.get("action", "")
    if action not in ["open", "update", "reopen"]:
        return WebhookResponse(
            status="skipped",
            message=f"MR 动作为 {action}，不触发分析"
        )
    
    source_branch = attrs.get("source_branch", "")
    target_branch = attrs.get("target_branch", "develop")
    mr_iid = attrs.get("iid")
    
    from app.services.change_workflow import trigger_change_analysis
    
    workflow_id = await trigger_change_analysis(
        background_tasks=background_tasks,
        project_id=str(event.project.get("id", "")),
        base_branch=target_branch,
        compare_branch=source_branch,
        repo_url=event.project.get("git_http_url", ""),
        mr_iid=mr_iid
    )
    
    logger.info(
        "gitlab_mr_triggered",
        mr_iid=mr_iid,
        source_branch=source_branch,
        target_branch=target_branch,
        workflow_id=workflow_id
    )
    
    return WebhookResponse(
        status="triggered",
        message=f"MR !{mr_iid} 变更分析已触发",
        workflow_id=workflow_id
    )


@router.post("/github/push", response_model=WebhookResponse)
async def handle_github_push(
    event: GitHubPushEvent,
    background_tasks: BackgroundTasks
):
    """
    处理 GitHub Push 事件
    """
    branch = event.ref.replace("refs/heads/", "")
    
    if not _should_trigger(branch):
        return WebhookResponse(
            status="skipped",
            message=f"分支 {branch} 不满足触发条件"
        )
    
    if event.before == "0000000000000000000000000000000000000000":
        return WebhookResponse(
            status="skipped",
            message="新分支，无变更"
        )
    
    from app.services.change_workflow import trigger_change_analysis
    
    workflow_id = await trigger_change_analysis(
        background_tasks=background_tasks,
        project_id=str(event.repository.get("id", "")),
        base_branch="main",
        compare_branch=branch,
        repo_url=event.repository.get("clone_url", ""),
        commits=[c.get("id") for c in event.commits]
    )
    
    return WebhookResponse(
        status="triggered",
        message=f"变更分析已触发，分支：{branch}",
        workflow_id=workflow_id
    )


@router.post("/github/pull_request", response_model=WebhookResponse)
async def handle_github_pr(
    event: GitHubPullRequestEvent,
    background_tasks: BackgroundTasks
):
    """
    处理 GitHub Pull Request 事件
    """
    if event.action not in ["opened", "synchronize", "reopened"]:
        return WebhookResponse(
            status="skipped",
            message=f"PR 动作为 {event.action}，不触发分析"
        )
    
    pr = event.pull_request
    source_branch = pr.get("head", {}).get("ref", "")
    target_branch = pr.get("base", {}).get("ref", "main")
    
    from app.services.change_workflow import trigger_change_analysis
    
    workflow_id = await trigger_change_analysis(
        background_tasks=background_tasks,
        project_id=str(event.repository.get("id", "")),
        base_branch=target_branch,
        compare_branch=source_branch,
        repo_url=event.repository.get("clone_url", ""),
        mr_iid=event.number
    )
    
    return WebhookResponse(
        status="triggered",
        message=f"PR #{event.number} 变更分析已触发",
        workflow_id=workflow_id
    )


def _should_trigger(branch: str) -> bool:
    """判断是否触发分析"""
    trigger_branches = ["feature/", "hotfix/", "bugfix/", "release/"]
    return any(branch.startswith(pattern) for pattern in trigger_branches)
