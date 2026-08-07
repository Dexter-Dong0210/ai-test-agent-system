"""
Git 操作工具

职责：
1. 检测代码变更
2. 获取变更文件列表
3. 获取变更方法列表
"""

from langchain_core.tools import tool
from typing import List, Dict, Optional
import subprocess
import os
import re


@tool
async def detect_changes(
    base_branch: str,
    compare_branch: str,
    repo_url: Optional[str] = None,
    repo_path: str = "."
) -> Dict:
    """
    检测两个分支之间的代码变更
    
    Args:
        base_branch: 基准分支（如 develop, main）
        compare_branch: 对比分支（如 feature-xxx）
        repo_url: 仓库 URL（可选，用于克隆）
        repo_path: 本地仓库路径
    
    Returns:
        变更文件列表、变更方法列表、变更类型统计
    """
    try:
        if repo_url and not os.path.exists(repo_path):
            result = subprocess.run(
                ["git", "clone", repo_url, repo_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                return {"error": f"克隆仓库失败: {result.stderr}"}

        result = subprocess.run(
            ["git", "fetch", "origin", base_branch, compare_branch],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        result = subprocess.run(
            ["git", "diff", "--name-status", f"origin/{base_branch}..origin/{compare_branch}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        changed_files = []
        for line in result.stdout.strip().split("\n"):
            if line and "\t" in line:
                parts = line.split("\t")
                status = parts[0]
                file_path = parts[1] if len(parts) > 1 else ""
                
                if file_path:
                    changed_files.append({
                        "path": file_path,
                        "status": _parse_status(status),
                        "language": _get_language(file_path),
                        "is_code": _is_code_file(file_path)
                    })

        diff_result = subprocess.run(
            ["git", "diff", f"origin/{base_branch}..origin/{compare_branch}", "--unified=0"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        changed_methods = _extract_changed_methods(diff_result.stdout, changed_files)

        stats = {
            "total_files": len(changed_files),
            "added": len([f for f in changed_files if f["status"] == "added"]),
            "modified": len([f for f in changed_files if f["status"] == "modified"]),
            "deleted": len([f for f in changed_files if f["status"] == "deleted"]),
            "code_files": len([f for f in changed_files if f["is_code"]]),
            "total_methods": len(changed_methods)
        }

        return {
            "changed_files": changed_files,
            "changed_methods": changed_methods,
            "stats": stats,
            "base_branch": base_branch,
            "compare_branch": compare_branch
        }

    except subprocess.TimeoutExpired:
        return {"error": "Git 操作超时"}
    except Exception as e:
        return {"error": str(e)}


def _parse_status(status: str) -> str:
    """解析 Git 状态码"""
    status_map = {
        "A": "added",
        "M": "modified",
        "D": "deleted",
        "R": "renamed",
        "C": "copied",
        "T": "type_changed"
    }
    return status_map.get(status[0], "unknown")


def _get_language(file_path: str) -> str:
    """根据文件扩展名判断语言"""
    ext_map = {
        ".java": "java",
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".kt": "kotlin",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp"
    }
    ext = os.path.splitext(file_path)[1].lower()
    return ext_map.get(ext, "unknown")


def _is_code_file(file_path: str) -> bool:
    """判断是否为代码文件"""
    code_extensions = {
        ".java", ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs",
        ".kt", ".cs", ".php", ".rb", ".swift", ".c", ".cpp", ".h", ".hpp"
    }
    ext = os.path.splitext(file_path)[1].lower()
    return ext in code_extensions


def _extract_changed_methods(diff_content: str, changed_files: List[Dict]) -> List[Dict]:
    """从 diff 内容中提取变更的方法"""
    changed_methods = []
    
    java_method_pattern = r'^[\+\-]\s*(?:public|private|protected|static)?\s*\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
    python_method_pattern = r'^[\+\-]\s*def\s+(\w+)\s*\([^)]*\):'
    js_method_pattern = r'^[\+\-]\s*(?:async\s+)?(?:static\s+)?(\w+)\s*\([^)]*\)\s*(?:=>|\{)'
    
    current_file = None
    for line in diff_content.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split()
            if len(parts) >= 3:
                current_file = parts[2].replace("a/", "")
        
        if current_file and _is_code_file(current_file):
            language = _get_language(current_file)
            
            if language == "java":
                match = re.match(java_method_pattern, line)
                if match:
                    changed_methods.append({
                        "name": match.group(1),
                        "file": current_file,
                        "language": "java"
                    })
            elif language == "python":
                match = re.match(python_method_pattern, line)
                if match:
                    changed_methods.append({
                        "name": match.group(1),
                        "file": current_file,
                        "language": "python"
                    })
            elif language in ["javascript", "typescript"]:
                match = re.match(js_method_pattern, line)
                if match:
                    changed_methods.append({
                        "name": match.group(1),
                        "file": current_file,
                        "language": language
                    })
    
    return changed_methods


@tool
async def get_file_content(
    file_path: str,
    branch: str = "HEAD",
    repo_path: str = "."
) -> Dict:
    """
    获取指定分支的文件内容
    
    Args:
        file_path: 文件路径
        branch: 分支名
        repo_path: 仓库路径
    
    Returns:
        文件内容
    """
    try:
        result = subprocess.run(
            ["git", "show", f"{branch}:{file_path}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {"error": f"获取文件内容失败: {result.stderr}"}
        
        return {
            "file_path": file_path,
            "branch": branch,
            "content": result.stdout
        }
    
    except Exception as e:
        return {"error": str(e)}
