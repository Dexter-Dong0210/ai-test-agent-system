"""
代码到接口映射工具

职责：
1. 解析 Controller/Router 代码
2. 提取 API 端点信息
3. 映射受影响的类到 API 端点
"""

from langchain_core.tools import tool
from typing import List, Dict, Optional
import re
import os


@tool
async def map_to_endpoints(
    affected_classes: List[str],
    project_identifier: str = "",
    repo_path: str = "."
) -> Dict:
    """
    将受影响的类映射到 API 端点
    
    支持的框架：
    - Spring Boot (@RequestMapping, @GetMapping, @PostMapping, etc.)
    - FastAPI (@router.get, @router.post)
    - Express (app.get, app.post)
    
    Args:
        affected_classes: 受影响的类名列表
        project_identifier: 项目标识
        repo_path: 仓库路径
    
    Returns:
        受影响的 API 端点列表
    """
    try:
        endpoints = []
        class_to_endpoints = {}
        
        for class_name in affected_classes:
            file_path = _find_class_file(class_name, repo_path)
            
            if not file_path:
                continue
            
            language = _get_language(file_path)
            class_endpoints = []
            
            if language == "java":
                class_endpoints = _parse_spring_controller(file_path)
            elif language == "python":
                class_endpoints = _parse_fastapi_router(file_path)
            elif language in ["javascript", "typescript"]:
                class_endpoints = _parse_express_router(file_path)
            
            class_to_endpoints[class_name] = class_endpoints
            endpoints.extend(class_endpoints)
        
        unique_endpoints = _deduplicate_endpoints(endpoints)
        
        return {
            "affected_classes": affected_classes,
            "class_to_endpoints": class_to_endpoints,
            "endpoints": unique_endpoints,
            "stats": {
                "total_classes": len(affected_classes),
                "classes_with_endpoints": len(class_to_endpoints),
                "total_endpoints": len(unique_endpoints)
            }
        }
    
    except Exception as e:
        return {"error": str(e)}


@tool
async def enrich_endpoint_info(
    endpoints: List[Dict],
    project_identifier: str
) -> Dict:
    """
    丰富端点信息（从数据库获取详细信息）
    
    Args:
        endpoints: 端点列表
        project_identifier: 项目标识
    
    Returns:
        包含完整信息的端点列表
    """
    try:
        from app.repositories.api_endpoint_repo import get_endpoint_by_method_path
        
        enriched_endpoints = []
        matched_count = 0
        
        for ep in endpoints:
            method = ep.get("method", "")
            path = ep.get("path", "")
            
            db_endpoint = await get_endpoint_by_method_path(
                project_identifier=project_identifier,
                method=method,
                path=path
            )
            
            if db_endpoint:
                enriched_endpoints.append({
                    **ep,
                    "endpoint_id": db_endpoint.id,
                    "summary": db_endpoint.summary,
                    "description": db_endpoint.description,
                    "parameters": db_endpoint.parameters,
                    "request_body": db_endpoint.request_body,
                    "responses": db_endpoint.responses,
                    "tags": db_endpoint.tags,
                    "has_test": True,
                    "matched": True
                })
                matched_count += 1
            else:
                enriched_endpoints.append({
                    **ep,
                    "endpoint_id": None,
                    "has_test": False,
                    "matched": False
                })
        
        return {
            "endpoints": enriched_endpoints,
            "stats": {
                "total": len(endpoints),
                "matched": matched_count,
                "unmatched": len(endpoints) - matched_count
            }
        }
    
    except Exception as e:
        return {
            "endpoints": endpoints,
            "error": str(e)
        }


def _find_class_file(class_name: str, repo_path: str) -> Optional[str]:
    """查找类对应的文件"""
    simple_name = class_name.split(".")[-1]
    
    search_patterns = [
        f"**/{simple_name}.java",
        f"**/{simple_name}.py",
        f"**/{simple_name}.ts",
        f"**/{simple_name}.js",
    ]
    
    for pattern in search_patterns:
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file == f"{simple_name}{os.path.splitext(pattern)[1]}":
                    return os.path.join(root, file)
    
    return None


def _get_language(file_path: str) -> str:
    """获取文件语言"""
    ext_map = {
        ".java": "java",
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript"
    }
    ext = os.path.splitext(file_path)[1].lower()
    return ext_map.get(ext, "unknown")


def _parse_spring_controller(file_path: str) -> List[Dict]:
    """解析 Spring Boot Controller"""
    endpoints = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []
    
    class_mapping = ""
    class_match = re.search(r'@RequestMapping\(["\']([^"\']+)["\']', content)
    if class_match:
        class_mapping = class_match.group(1)
    
    class_name_match = re.search(r'public\s+class\s+(\w+)', content)
    class_name = class_name_match.group(1) if class_name_match else os.path.basename(file_path).replace(".java", "")
    
    method_patterns = [
        (r'@GetMapping\(["\']([^"\']+)["\']', 'GET'),
        (r'@PostMapping\(["\']([^"\']+)["\']', 'POST'),
        (r'@PutMapping\(["\']([^"\']+)["\']', 'PUT'),
        (r'@DeleteMapping\(["\']([^"\']+)["\']', 'DELETE'),
        (r'@PatchMapping\(["\']([^"\']+)["\']', 'PATCH'),
    ]
    
    for pattern, method in method_patterns:
        for match in re.finditer(pattern, content):
            path = match.group(1)
            full_path = class_mapping + path if class_mapping else path
            
            method_name = _extract_method_name(content, match.end())
            
            endpoints.append({
                "method": method,
                "path": full_path,
                "controller": class_name,
                "handler_method": method_name,
                "file": file_path,
                "framework": "spring"
            })
    
    return endpoints


def _parse_fastapi_router(file_path: str) -> List[Dict]:
    """解析 FastAPI Router"""
    endpoints = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []
    
    router_name = os.path.basename(file_path).replace(".py", "")
    
    pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
    
    for match in re.finditer(pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        
        func_name = _extract_function_name(content, match.end())
        
        endpoints.append({
            "method": method,
            "path": path,
            "router": router_name,
            "handler_function": func_name,
            "file": file_path,
            "framework": "fastapi"
        })
    
    return endpoints


def _parse_express_router(file_path: str) -> List[Dict]:
    """解析 Express Router"""
    endpoints = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []
    
    pattern = r'(?:router|app)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
    
    for match in re.finditer(pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        
        endpoints.append({
            "method": method,
            "path": path,
            "file": file_path,
            "framework": "express"
        })
    
    return endpoints


def _extract_method_name(content: str, position: int) -> str:
    """从 Java 代码中提取方法名"""
    remaining = content[position:]
    match = re.search(r'public\s+\w+\s+(\w+)\s*\(', remaining)
    if match:
        return match.group(1)
    return ""


def _extract_function_name(content: str, position: int) -> str:
    """从 Python 代码中提取函数名"""
    remaining = content[position:]
    match = re.search(r'async\s+def\s+(\w+)|def\s+(\w+)', remaining)
    if match:
        return match.group(1) or match.group(2)
    return ""


def _deduplicate_endpoints(endpoints: List[Dict]) -> List[Dict]:
    """去重端点"""
    seen = set()
    unique = []
    
    for ep in endpoints:
        key = f"{ep.get('method', '')}:{ep.get('path', '')}"
        if key not in seen:
            seen.add(key)
            unique.append(ep)
    
    return unique
