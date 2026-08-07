"""
端点查询工具

职责：
1. 获取端点详细信息
2. 批量查询端点
"""

from langchain_core.tools import tool
from typing import List, Dict, Optional
import httpx


@tool
async def get_endpoint_details(
    endpoint_id: str
) -> Dict:
    """
    获取单个端点的详细信息
    
    Args:
        endpoint_id: 端点 ID
    
    Returns:
        端点详细信息（method, path, parameters, request_body, responses）
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8001/api/v2/api-endpoints/{endpoint_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
        
        return {"error": f"端点 {endpoint_id} 不存在"}
    
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_multiple_endpoints_details(
    endpoint_ids: List[str]
) -> Dict:
    """
    批量获取多个端点的详细信息
    
    Args:
        endpoint_ids: 端点 ID 列表
    
    Returns:
        端点详细信息列表
    """
    try:
        endpoints = []
        
        for endpoint_id in endpoint_ids:
            endpoint = await get_endpoint_details(endpoint_id)
            if "error" not in endpoint:
                endpoints.append(endpoint)
        
        return {
            "endpoints": endpoints,
            "total": len(endpoints),
            "requested": len(endpoint_ids)
        }
    
    except Exception as e:
        return {
            "endpoints": [],
            "error": str(e)
        }


@tool
async def search_endpoints(
    project_identifier: str,
    method: Optional[str] = None,
    path_pattern: Optional[str] = None,
    tag: Optional[str] = None
) -> Dict:
    """
    搜索端点
    
    Args:
        project_identifier: 项目标识
        method: HTTP 方法过滤
        path_pattern: 路径模式（支持通配符）
        tag: 标签过滤
    
    Returns:
        匹配的端点列表
    """
    try:
        params = {"project_identifier": project_identifier}
        if method:
            params["method"] = method
        if path_pattern:
            params["path_pattern"] = path_pattern
        if tag:
            params["tag"] = tag
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8001/api/v2/api-endpoints",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
        
        return {"endpoints": []}
    
    except Exception as e:
        return {"endpoints": [], "error": str(e)}
