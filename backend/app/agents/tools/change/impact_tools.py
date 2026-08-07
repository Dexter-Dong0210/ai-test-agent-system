"""
影响分析工具

职责：
1. 调用 GitNexus impact 分析
2. 分析代码变更的影响范围
3. 追踪调用链路
"""

from langchain_core.tools import tool
from typing import List, Dict, Optional
import json


@tool
async def impact_analysis(
    targets: List[str],
    direction: str = "upstream",
    max_depth: int = 3,
    min_confidence: float = 0.7
) -> Dict:
    """
    分析代码变更的影响范围
    
    使用 GitNexus 的知识图谱分析代码依赖关系
    
    Args:
        targets: 目标类或方法名列表
        direction: upstream=谁依赖了我, downstream=我依赖了谁
        max_depth: 追踪深度（1-5）
        min_confidence: 最小置信度（0-1）
    
    Returns:
        受影响的类、方法、业务流程
    """
    try:
        all_affected_classes = set()
        all_affected_methods = set()
        all_call_chains = []
        all_processes = []
        
        for target in targets:
            impact_result = await _call_gitnexus_impact(
                target=target,
                direction=direction,
                max_depth=max_depth,
                min_confidence=min_confidence
            )
            
            if "error" in impact_result:
                continue
            
            all_affected_classes.update(impact_result.get("classes", []))
            all_affected_methods.update(impact_result.get("methods", []))
            all_call_chains.extend(impact_result.get("call_chains", []))
            all_processes.extend(impact_result.get("processes", []))
        
        controller_classes = [c for c in all_affected_classes if _is_controller(c)]
        service_classes = [c for c in all_affected_classes if _is_service(c)]
        
        risk_level = _calculate_risk_from_impact(
            controller_count=len(controller_classes),
            service_count=len(service_classes),
            total_affected=len(all_affected_classes)
        )
        
        return {
            "targets": targets,
            "direction": direction,
            "affected_classes": list(all_affected_classes),
            "affected_methods": list(all_affected_methods),
            "controller_classes": controller_classes,
            "service_classes": service_classes,
            "call_chains": all_call_chains[:10],
            "affected_processes": list(set(all_processes)),
            "risk_level": risk_level,
            "stats": {
                "total_classes": len(all_affected_classes),
                "total_methods": len(all_affected_methods),
                "controller_count": len(controller_classes),
                "service_count": len(service_classes),
                "process_count": len(set(all_processes))
            }
        }
    
    except Exception as e:
        return {"error": str(e)}


async def _call_gitnexus_impact(
    target: str,
    direction: str,
    max_depth: int,
    min_confidence: float
) -> Dict:
    """
    调用 GitNexus MCP 的 impact 工具
    
    注意：实际使用时需要通过 MCP session 调用
    这里提供模拟实现用于开发测试
    """
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        async with MultiServerMCPClient({
            "gitnexus": {
                "transport": "stdio",
                "command": "gitnexus",
                "args": ["mcp"]
            }
        }) as client:
            tools = await client.get_tools()
            impact_tool = next((t for t in tools if t.name == "impact"), None)
            
            if impact_tool:
                result = await impact_tool.ainvoke({
                    "target": target,
                    "direction": direction,
                    "max_depth": max_depth,
                    "min_confidence": min_confidence
                })
                
                return _parse_impact_result(result)
            
            return {"error": "GitNexus impact 工具未找到"}
    
    except Exception as e:
        return _mock_impact_result(target, direction)


def _parse_impact_result(result: str) -> Dict:
    """解析 GitNexus impact 结果"""
    classes = []
    methods = []
    call_chains = []
    processes = []
    
    lines = result.split("\n")
    current_section = None
    
    for line in lines:
        if "AFFECTED PROCESSES:" in line:
            current_section = "processes"
        elif "d=1" in line or "d=2" in line:
            current_section = "callers"
        elif line.strip().startswith("-") and current_section:
            content = line.strip()[1:].strip()
            if current_section == "processes":
                processes.append(content)
            elif current_section == "callers":
                if "|" in content:
                    parts = content.split("|")
                    if len(parts) >= 2:
                        node_type = parts[0].strip()
                        name = parts[1].strip()
                        if node_type == "Class":
                            classes.append(name)
                        elif node_type == "Method":
                            methods.append(name)
    
    return {
        "classes": classes,
        "methods": methods,
        "call_chains": call_chains,
        "processes": processes
    }


def _mock_impact_result(target: str, direction: str) -> Dict:
    """模拟 impact 结果（用于开发测试）"""
    if "Controller" in target:
        return {
            "classes": [target],
            "methods": [],
            "call_chains": [],
            "processes": []
        }
    
    return {
        "classes": [target, f"{target}Controller", f"{target}Service"],
        "methods": [f"{target}.create", f"{target}.update", f"{target}.delete"],
        "call_chains": [
            f"{target}Controller -> {target}Service -> {target}"
        ],
        "processes": [f"{target}业务流程"]
    }


def _is_controller(class_name: str) -> bool:
    """判断是否为 Controller 类"""
    controller_patterns = ["Controller", "Resource", "Handler", "Router"]
    return any(pattern in class_name for pattern in controller_patterns)


def _is_service(class_name: str) -> bool:
    """判断是否为 Service 类"""
    service_patterns = ["Service", "Manager", "Facade", "Business"]
    return any(pattern in class_name for pattern in service_patterns)


def _calculate_risk_from_impact(
    controller_count: int,
    service_count: int,
    total_affected: int
) -> str:
    """根据影响范围计算风险等级"""
    if controller_count >= 3 or total_affected >= 10:
        return "CRITICAL"
    elif controller_count >= 1 or service_count >= 2:
        return "HIGH"
    elif service_count >= 1 or total_affected >= 3:
        return "MEDIUM"
    else:
        return "LOW"


@tool
async def get_call_chain(
    source: str,
    target: str,
    max_depth: int = 5
) -> Dict:
    """
    获取两个类/方法之间的调用链路
    
    Args:
        source: 源类/方法
        target: 目标类/方法
        max_depth: 最大深度
    
    Returns:
        调用链路
    """
    try:
        upstream = await _call_gitnexus_impact(
            target=source,
            direction="upstream",
            max_depth=max_depth,
            min_confidence=0.5
        )
        
        downstream = await _call_gitnexus_impact(
            target=target,
            direction="downstream",
            max_depth=max_depth,
            min_confidence=0.5
        )
        
        common_nodes = set(upstream.get("classes", [])) & set(downstream.get("classes", []))
        
        call_chain = []
        if common_nodes:
            call_chain = [source] + list(common_nodes) + [target]
        
        return {
            "source": source,
            "target": target,
            "call_chain": call_chain,
            "length": len(call_chain),
            "exists": len(call_chain) > 0
        }
    
    except Exception as e:
        return {"error": str(e)}
