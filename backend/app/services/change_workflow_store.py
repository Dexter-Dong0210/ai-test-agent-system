"""
工作流存储模块

职责：
1. 存储工作流状态和结果
2. 查询工作流历史
"""

from typing import Dict, Optional, List
from datetime import datetime
import json

_workflow_store: Dict[str, Dict] = {}


async def save_workflow_result(workflow_id: str, result: Dict):
    """保存工作流结果"""
    _workflow_store[workflow_id] = {
        **result,
        "updated_at": datetime.now().isoformat()
    }


async def get_workflow_result(workflow_id: str) -> Optional[Dict]:
    """获取工作流结果"""
    return _workflow_store.get(workflow_id)


async def get_workflow_logs(workflow_id: str) -> List[str]:
    """获取工作流日志"""
    result = _workflow_store.get(workflow_id)
    if not result:
        return []
    
    logs = []
    for step in result.get("steps", []):
        step_name = step.get("step", "unknown")
        status = step.get("status", "unknown")
        logs.append(f"[{step_name}] {status}")
        
        if step.get("error"):
            logs.append(f"  Error: {step['error']}")
    
    return logs


async def cancel_workflow(workflow_id: str):
    """取消工作流"""
    result = _workflow_store.get(workflow_id)
    if result:
        result["status"] = "cancelled"
        result["updated_at"] = datetime.now().isoformat()


async def list_workflows(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """列出工作流"""
    workflows = list(_workflow_store.values())
    
    if project_id:
        workflows = [
            w for w in workflows
            if w.get("analysis_result", {}).get("project_id") == project_id
        ]
    
    if status:
        workflows = [w for w in workflows if w.get("status") == status]
    
    workflows.sort(
        key=lambda w: w.get("updated_at", ""),
        reverse=True
    )
    
    return workflows[offset:offset + limit]
