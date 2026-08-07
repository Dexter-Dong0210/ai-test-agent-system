"""
测试触发工具

职责：
1. 根据风险等级触发测试
2. 生成测试计划
3. 执行测试
"""

from langchain_core.tools import tool
from typing import List, Dict, Optional
import httpx
import json


@tool
async def trigger_tests(
    affected_endpoints: List[Dict],
    risk_level: str,
    test_scope: str,
    project_identifier: str = ""
) -> Dict:
    """
    触发测试执行
    
    Args:
        affected_endpoints: 受影响的端点列表
        risk_level: 风险等级
        test_scope: 测试范围 (none/unit/smoke/regression/full)
        project_identifier: 项目标识
    
    Returns:
        测试计划 ID、测试状态
    """
    try:
        if test_scope == "none":
            return {
                "status": "skipped",
                "reason": "风险等级低，无需执行测试",
                "test_plan_id": None
            }
        
        test_plan = await _create_test_plan(
            endpoints=affected_endpoints,
            test_scope=test_scope,
            project_identifier=project_identifier
        )
        
        if not test_plan.get("test_plan_id"):
            return {
                "status": "error",
                "reason": "创建测试计划失败",
                "test_plan_id": None
            }
        
        execution = await _execute_test_plan(
            test_plan_id=test_plan["test_plan_id"],
            test_scope=test_scope
        )
        
        return {
            "status": "triggered",
            "test_plan_id": test_plan["test_plan_id"],
            "test_scope": test_scope,
            "risk_level": risk_level,
            "endpoints_count": len(affected_endpoints),
            "execution_id": execution.get("execution_id")
        }
    
    except Exception as e:
        return {
            "status": "error",
            "reason": str(e),
            "test_plan_id": None
        }


async def _create_test_plan(
    endpoints: List[Dict],
    test_scope: str,
    project_identifier: str
) -> Dict:
    """创建测试计划"""
    try:
        endpoint_ids = [
            ep.get("endpoint_id")
            for ep in endpoints
            if ep.get("endpoint_id")
        ]
        
        plan_name = f"变更分析触发测试 - {test_scope}"
        
        plan_data = {
            "name": plan_name,
            "description": f"基于变更分析自动生成的测试计划\n测试范围：{test_scope}\n端点数量：{len(endpoint_ids)}",
            "test_scope": test_scope,
            "endpoint_ids": endpoint_ids,
            "project_identifier": project_identifier
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/api/v2/test-plans",
                json=plan_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "test_plan_id": result.get("id"),
                    "name": plan_name
                }
        
        return {"test_plan_id": None}
    
    except Exception:
        return {"test_plan_id": None}


async def _execute_test_plan(
    test_plan_id: str,
    test_scope: str
) -> Dict:
    """执行测试计划"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8001/api/v2/test-plans/{test_plan_id}/execute",
                json={"scope": test_scope},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
        
        return {"execution_id": None}
    
    except Exception:
        return {"execution_id": None}


@tool
async def get_test_results(
    test_plan_id: str
) -> Dict:
    """
    获取测试结果
    
    Args:
        test_plan_id: 测试计划 ID
    
    Returns:
        测试结果
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8001/api/v2/test-plans/{test_plan_id}/results",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
        
        return {"error": "获取测试结果失败"}
    
    except Exception as e:
        return {"error": str(e)}


@tool
async def generate_incremental_tests(
    affected_endpoints: List[Dict],
    risk_level: str,
    project_identifier: str
) -> Dict:
    """
    生成增量测试用例
    
    仅针对受影响的端点生成测试用例
    
    Args:
        affected_endpoints: 受影响的端点列表
        risk_level: 风险等级
        project_identifier: 项目标识
    
    Returns:
        生成的测试用例列表
    """
    try:
        test_cases = []
        
        for endpoint in affected_endpoints:
            endpoint_id = endpoint.get("endpoint_id")
            if not endpoint_id:
                continue
            
            test_case = await _generate_test_for_endpoint(
                endpoint=endpoint,
                risk_level=risk_level,
                project_identifier=project_identifier
            )
            
            if test_case:
                test_cases.append(test_case)
        
        return {
            "test_cases": test_cases,
            "total": len(test_cases),
            "status": "generated"
        }
    
    except Exception as e:
        return {
            "test_cases": [],
            "error": str(e)
        }


async def _generate_test_for_endpoint(
    endpoint: Dict,
    risk_level: str,
    project_identifier: str
) -> Optional[Dict]:
    """为单个端点生成测试"""
    try:
        endpoint_id = endpoint.get("endpoint_id")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/api/v2/api-tests/generate",
                json={
                    "endpoint_id": endpoint_id,
                    "project_identifier": project_identifier,
                    "test_types": _get_test_types_for_risk(risk_level)
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
        
        return None
    
    except Exception:
        return None


def _get_test_types_for_risk(risk_level: str) -> List[str]:
    """根据风险等级确定测试类型"""
    test_type_map = {
        "LOW": ["smoke"],
        "MEDIUM": ["smoke", "unit"],
        "HIGH": ["smoke", "functional", "negative"],
        "CRITICAL": ["smoke", "functional", "negative", "edge_case", "security"]
    }
    return test_type_map.get(risk_level, ["smoke"])
