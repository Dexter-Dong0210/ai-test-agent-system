"""
变更分析 API 接口

职责：
1. 提供变更分析 REST API
2. 提供工作流状态查询
3. 提供门禁评估接口
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import structlog

router = APIRouter(prefix="/change", tags=["Change Analysis"])
logger = structlog.get_logger()


class AnalyzeRequest(BaseModel):
    """变更分析请求"""
    base_branch: str = Field(..., description="基准分支")
    compare_branch: str = Field(..., description="对比分支")
    repo_url: str = Field(..., description="仓库 URL")
    project_id: str = Field(..., description="项目 ID")
    mr_iid: Optional[int] = Field(None, description="MR IID")
    commits: Optional[List[str]] = Field(None, description="Commit 列表")


class AnalyzeResponse(BaseModel):
    """变更分析响应"""
    workflow_id: str
    status: str
    message: str


class WorkflowStatusResponse(BaseModel):
    """工作流状态响应"""
    workflow_id: str
    status: str
    steps: List[Dict]
    analysis_result: Optional[Dict] = None
    test_result: Optional[Dict] = None
    gate_result: Optional[Dict] = None
    error: Optional[str] = None


class GateEvaluateRequest(BaseModel):
    """门禁评估请求"""
    test_results: Dict = Field(..., description="测试结果")
    analysis_result: Dict = Field(..., description="分析结果")


class GateEvaluateResponse(BaseModel):
    """门禁评估响应"""
    status: str
    action: str
    block_reason: Optional[str] = None
    violations: List[str] = []


@router.post("/analyze", response_model=AnalyzeResponse)
async def trigger_analysis(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    触发变更分析
    
    由 Git Hook 或 CI/CD 调用，后台执行变更分析工作流
    """
    from app.services.change_workflow import trigger_change_analysis
    
    try:
        workflow_id = await trigger_change_analysis(
            background_tasks=background_tasks,
            project_id=request.project_id,
            base_branch=request.base_branch,
            compare_branch=request.compare_branch,
            repo_url=request.repo_url,
            mr_iid=request.mr_iid,
            commits=request.commits
        )
        
        logger.info(
            "analysis_triggered",
            workflow_id=workflow_id,
            project_id=request.project_id,
            compare_branch=request.compare_branch
        )
        
        return AnalyzeResponse(
            workflow_id=workflow_id,
            status="triggered",
            message="变更分析已触发，正在后台执行"
        )
    
    except Exception as e:
        logger.exception("analysis_trigger_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    获取工作流状态
    
    查询变更分析工作流的执行状态和结果
    """
    from app.services.change_workflow_store import get_workflow_result
    
    try:
        result = await get_workflow_result(workflow_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="工作流不存在")
        
        return WorkflowStatusResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("get_workflow_failed", workflow_id=workflow_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gate/evaluate", response_model=GateEvaluateResponse)
async def evaluate_gate(request: GateEvaluateRequest):
    """
    评估质量门禁
    
    根据测试结果和分析结果评估是否通过门禁
    """
    from app.integrations.gate import QualityGate
    
    try:
        gate = QualityGate(config={})
        result = await gate.evaluate(
            test_results=request.test_results,
            analysis_result=request.analysis_result
        )
        
        return GateEvaluateResponse(
            status=result.status,
            action=result.action,
            block_reason=result.block_reason,
            violations=result.violations or []
        )
    
    except Exception as e:
        logger.exception("gate_evaluate_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}/logs")
async def get_workflow_logs(workflow_id: str):
    """获取工作流执行日志"""
    from app.services.change_workflow_store import get_workflow_logs
    
    try:
        logs = await get_workflow_logs(workflow_id)
        return {"workflow_id": workflow_id, "logs": logs}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    """取消工作流"""
    from app.services.change_workflow_store import cancel_workflow
    
    try:
        await cancel_workflow(workflow_id)
        return {"workflow_id": workflow_id, "status": "cancelled"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_workflows(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """列出工作流"""
    from app.services.change_workflow_store import list_workflows
    
    try:
        workflows = await list_workflows(
            project_id=project_id,
            status=status,
            limit=limit,
            offset=offset
        )
        return {"workflows": workflows, "total": len(workflows)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
