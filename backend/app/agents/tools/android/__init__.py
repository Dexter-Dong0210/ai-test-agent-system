"""
Android Agent 工具模块

本目录包含所有 Android 测试智能体的工具定义，按功能分类组织。
"""

from typing import List
from langchain_core.tools import BaseTool

from app.agents.tools.android.artifacts_tools import (
    save_android_test_plan,
    save_android_test_cases,
    save_android_test_script,
    get_android_artifacts,
    get_android_artifact_content,
)
# pylint: disable  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2TVdFM1l3PT06NTYyZWQ0YTU=

from app.agents.tools.android.script_tools import (
    get_android_script_info,
    download_android_script,
    delete_android_script,
)

from app.agents.tools.android.execution_tools import (
    execute_android_script,
    get_android_execution_status,
    run_all_android_scripts,
)
# pylint: disable  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2TVdFM1l3PT06NTYyZWQ0YTU=

from app.agents.tools.android.env_tools import (
    check_android_env,
    init_android_project,
)

ARTIFACT_TOOLS = [
    save_android_test_plan,
    save_android_test_cases,
    save_android_test_script,
    get_android_artifacts,
    get_android_artifact_content,
]

SCRIPT_TOOLS = [
    get_android_script_info,
    download_android_script,
    delete_android_script,
]

EXECUTION_TOOLS = [
    execute_android_script,
    get_android_execution_status,
    run_all_android_scripts,
]

ENV_TOOLS = [
    check_android_env,
    init_android_project,
]

ALL_ANDROID_TOOLS = (
    ARTIFACT_TOOLS
    + SCRIPT_TOOLS
    + EXECUTION_TOOLS
    + ENV_TOOLS
)
# pragma: no cover  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2TVdFM1l3PT06NTYyZWQ0YTU=

# type: ignore  My80OmFIVnBZMlhva2FQbHNJL21tS1U2TVdFM1l3PT06NTYyZWQ0YTU=

def get_local_tools() -> List[BaseTool]:
    """
    获取所有 Android 本地工具列表。

    MCP 工具在 agent.py 中异步加载，此处只返回本地工具。
    """
    return list(ALL_ANDROID_TOOLS)


__all__ = [
    # 成果物
    "save_android_test_plan",
    "save_android_test_cases",
    "save_android_test_script",
    "get_android_artifacts",
    "get_android_artifact_content",
    # 脚本
    "get_android_script_info",
    "download_android_script",
    "delete_android_script",
    # 执行
    "execute_android_script",
    "get_android_execution_status",
    "run_all_android_scripts",
    # 环境
    "check_android_env",
    "init_android_project",
    # 分类列表
    "ARTIFACT_TOOLS",
    "SCRIPT_TOOLS",
    "EXECUTION_TOOLS",
    "ENV_TOOLS",
    "ALL_ANDROID_TOOLS",
    "get_local_tools",
]
