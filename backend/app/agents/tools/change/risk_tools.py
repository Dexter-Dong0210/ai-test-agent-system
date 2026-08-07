"""
风险评估工具

职责：
1. 根据变更内容评估风险等级
2. 确定测试范围
3. 生成测试建议
"""

from langchain_core.tools import tool
from typing import List, Dict, Optional
import re


@tool
async def assess_risk(
    changed_files: List[Dict],
    affected_endpoints: List[Dict],
    impact_result: Dict
) -> Dict:
    """
    评估变更风险等级
    
    Args:
        changed_files: 变更文件列表
        affected_endpoints: 受影响的端点列表
        impact_result: 影响分析结果
    
    Returns:
        风险等级、测试范围、测试建议
    """
    try:
        file_risk = _assess_file_risk(changed_files)
        endpoint_risk = _assess_endpoint_risk(affected_endpoints)
        impact_risk = impact_result.get("risk_level", "LOW")
        
        risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        risk_level = max(
            [file_risk, endpoint_risk, impact_risk],
            key=lambda r: risk_levels.index(r) if r in risk_levels else 0
        )
        
        test_scope = _determine_test_scope(risk_level, affected_endpoints)
        
        recommendation = _generate_recommendation(
            risk_level=risk_level,
            test_scope=test_scope,
            changed_files=changed_files,
            affected_endpoints=affected_endpoints
        )
        
        return {
            "risk_level": risk_level,
            "test_scope": test_scope,
            "recommendation": recommendation,
            "file_risk": file_risk,
            "endpoint_risk": endpoint_risk,
            "impact_risk": impact_risk,
            "risk_factors": _identify_risk_factors(
                changed_files, affected_endpoints, impact_result
            )
        }
    
    except Exception as e:
        return {"error": str(e)}


def _assess_file_risk(changed_files: List[Dict]) -> str:
    """评估文件变更风险"""
    if not changed_files:
        return "LOW"
    
    for file_info in changed_files:
        path = file_info.get("path", "")
        
        if _is_critical_file(path):
            return "CRITICAL"
        
        if _is_high_risk_file(path):
            return "HIGH"
        
        if _is_medium_risk_file(path):
            return "MEDIUM"
    
    return "LOW"


def _assess_endpoint_risk(affected_endpoints: List[Dict]) -> str:
    """评估端点影响风险"""
    if not affected_endpoints:
        return "LOW"
    
    endpoint_count = len(affected_endpoints)
    
    if endpoint_count >= 10:
        return "CRITICAL"
    elif endpoint_count >= 5:
        return "HIGH"
    elif endpoint_count >= 1:
        return "MEDIUM"
    
    return "LOW"


def _is_critical_file(path: str) -> bool:
    """判断是否为严重风险文件"""
    critical_patterns = [
        r'.*dto/.*\.java$',
        r'.*entity/.*\.java$',
        r'.*model/.*\.java$',
        r'.*domain/.*\.java$',
        r'.*schema\.py$',
        r'.*migration/.*',
        r'.*sql$',
    ]
    
    return any(re.match(pattern, path, re.IGNORECASE) for pattern in critical_patterns)


def _is_high_risk_file(path: str) -> bool:
    """判断是否为高风险文件"""
    high_patterns = [
        r'.*controller/.*\.java$',
        r'.*service/.*\.java$',
        r'.*api/.*\.py$',
        r'.*router/.*\.py$',
        r'.*route/.*\.js$',
    ]
    
    return any(re.match(pattern, path, re.IGNORECASE) for pattern in high_patterns)


def _is_medium_risk_file(path: str) -> bool:
    """判断是否为中风险文件"""
    medium_patterns = [
        r'.*config/.*',
        r'.*\.yml$',
        r'.*\.yaml$',
        r'.*\.json$',
        r'.*util/.*',
        r'.*helper/.*',
    ]
    
    return any(re.match(pattern, path, re.IGNORECASE) for pattern in medium_patterns)


def _determine_test_scope(
    risk_level: str,
    affected_endpoints: List[Dict]
) -> str:
    """确定测试范围"""
    if risk_level == "LOW":
        return "none"
    
    if risk_level == "MEDIUM":
        return "unit"
    
    if risk_level == "HIGH":
        if len(affected_endpoints) <= 3:
            return "smoke"
        else:
            return "regression"
    
    if risk_level == "CRITICAL":
        return "full"
    
    return "none"


def _generate_recommendation(
    risk_level: str,
    test_scope: str,
    changed_files: List[Dict],
    affected_endpoints: List[Dict]
) -> str:
    """生成测试建议"""
    recommendations = {
        "LOW": "风险等级低，建议执行代码审查即可。",
        "MEDIUM": f"风险等级中等，建议执行变更文件的单元测试。涉及 {len(changed_files)} 个文件变更。",
        "HIGH": f"风险等级高，建议执行冒烟测试 + 相关接口回归测试。受影响端点：{len(affected_endpoints)} 个。",
        "CRITICAL": "风险等级严重，建议执行全量回归测试 + 数据兼容性测试。"
    }
    
    base_recommendation = recommendations.get(risk_level, "")
    
    additional_tips = []
    
    if affected_endpoints:
        endpoint_list = [f"{ep['method']} {ep['path']}" for ep in affected_endpoints[:5]]
        additional_tips.append(f"\n\n**受影响端点：**\n" + "\n".join(f"- {e}" for e in endpoint_list))
        if len(affected_endpoints) > 5:
            additional_tips.append(f"\n- ... 还有 {len(affected_endpoints) - 5} 个端点")
    
    return base_recommendation + "".join(additional_tips)


def _identify_risk_factors(
    changed_files: List[Dict],
    affected_endpoints: List[Dict],
    impact_result: Dict
) -> List[str]:
    """识别风险因素"""
    factors = []
    
    for file_info in changed_files:
        path = file_info.get("path", "")
        if _is_critical_file(path):
            factors.append(f"数据模型变更：{path}")
        if _is_high_risk_file(path):
            factors.append(f"核心业务变更：{path}")
    
    if len(affected_endpoints) >= 5:
        factors.append(f"影响范围广：{len(affected_endpoints)} 个端点受影响")
    
    processes = impact_result.get("affected_processes", [])
    if processes:
        factors.append(f"业务流程影响：{', '.join(processes[:3])}")
    
    return factors[:10]
