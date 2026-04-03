"""
测试用例 Excel 导出工具集

为测试用例生成智能体提供实时存储与导出能力，
支持边生成边存储、最后统一导出为格式化 Excel。
存储持久化到 JSON 文件，服务重启后数据不丢失。
"""

import json
import threading
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.tools import tool

from utils.testcase_excel_exporter import export_testcases_to_excel

# JSON 持久化存储路径
_STORAGE_PATH = Path("./exports/testcase_storage.json")
_lock = threading.Lock()


def _load_storage() -> List[Dict[str, Any]]:
    """从 JSON 文件加载存储的用例"""
    if not _STORAGE_PATH.exists():
        return []
    try:
        with _STORAGE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save_storage(data: List[Dict[str, Any]]) -> None:
    """将用例保存到 JSON 文件"""
    _STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _STORAGE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@tool
def clear_testcase_storage() -> str:
    """
    清空已存储的测试用例缓存（同时清空 JSON 文件）。

    在开启新一轮测试用例生成前调用，避免旧数据混入。
    """
    with _lock:
        _save_storage([])
    return "测试用例存储已清空"


@tool
def save_testcase_to_storage(case: Dict[str, Any]) -> str:
    """
    将单条测试用例保存到存储中（持久化到 JSON 文件）。

    Args:
        case: 测试用例字典，建议包含以下字段:
              id, title, module, type, priority,
              preconditions, steps, test_data,
              expected_results, remarks
    """
    with _lock:
        data = _load_storage()
        data.append(case)
        _save_storage(data)
        case_id = case.get("id", "未知ID")
        return f"已保存用例 {case_id}，当前存储总数: {len(data)}"


@tool
def save_testcases_batch(cases: List[Dict[str, Any]]) -> str:
    """
    批量保存测试用例到存储中（持久化到 JSON 文件）。

    Args:
        cases: 测试用例字典列表
    """
    with _lock:
        data = _load_storage()
        data.extend(cases)
        _save_storage(data)
        return f"已批量保存 {len(cases)} 条用例，当前存储总数: {len(data)}"


@tool
def export_testcases_from_storage(output_path: str) -> str:
    """
    将存储中的所有测试用例导出为 Excel 文件。

    Args:
        output_path: Excel 文件保存路径，
                     建议格式: ./exports/测试用例_YYYYMMDD.xlsx
    """
    with _lock:
        data = _load_storage()
        if not data:
            return "错误：存储中没有测试用例，请先调用 save_testcase_to_storage 或 save_testcases_batch 保存用例"
        return export_testcases_to_excel(data, output_path)
