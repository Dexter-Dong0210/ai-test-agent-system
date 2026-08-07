"""变更分析工具模块"""

from app.agents.tools.change.git_tools import detect_changes_tool
from app.agents.tools.change.impact_tools import impact_analysis_tool
from app.agents.tools.change.mapping_tools import map_to_endpoints_tool, enrich_endpoint_info_tool
from app.agents.tools.change.risk_tools import assess_risk_tool
from app.agents.tools.change.test_tools import trigger_tests_tool
from app.agents.tools.change.endpoint_tools import get_endpoint_details_tool, get_multiple_endpoints_details_tool

__all__ = [
    "detect_changes_tool",
    "impact_analysis_tool",
    "map_to_endpoints_tool",
    "enrich_endpoint_info_tool",
    "assess_risk_tool",
    "trigger_tests_tool",
    "get_endpoint_details_tool",
    "get_multiple_endpoints_details_tool",
    "get_change_tools"
]


async def get_change_tools(mcp_session=None):
    """获取所有变更分析工具"""
    tools = [
        detect_changes_tool,
        impact_analysis_tool,
        map_to_endpoints_tool,
        enrich_endpoint_info_tool,
        assess_risk_tool,
        trigger_tests_tool,
        get_endpoint_details_tool,
        get_multiple_endpoints_details_tool,
    ]
    return tools
