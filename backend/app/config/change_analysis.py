"""
变更分析配置
"""

from pydantic_settings import BaseSettings
from typing import List, Dict


class ChangeAnalysisSettings(BaseSettings):
    """变更分析配置"""
    
    enabled: bool = True
    
    trigger_branches: List[str] = [
        "feature/*",
        "hotfix/*",
        "bugfix/*",
        "release/*"
    ]
    
    skip_branches: List[str] = [
        "main",
        "master",
        "develop",
        "staging"
    ]
    
    gitnexus_enabled: bool = True
    gitnexus_mcp_command: str = "gitnexus"
    gitnexus_mcp_args: List[str] = ["mcp"]
    
    impact_max_depth: int = 3
    impact_min_confidence: float = 0.7
    
    risk_rules: Dict = {
        "LOW": {
            "min_pass_rate": 80,
            "min_coverage": 0,
            "action": "allow"
        },
        "MEDIUM": {
            "min_pass_rate": 90,
            "min_coverage": 50,
            "action": "warn"
        },
        "HIGH": {
            "min_pass_rate": 100,
            "min_coverage": 70,
            "action": "block"
        },
        "CRITICAL": {
            "min_pass_rate": 100,
            "min_coverage": 80,
            "action": "block",
            "require_approval": True
        }
    }
    
    gate_enabled: bool = True
    gate_timeout: int = 3600
    
    notification_enabled: bool = True
    notification_channels: List[str] = ["dingtalk", "email"]
    
    GITLAB_URL: str = ""
    GITLAB_TOKEN: str = ""
    DINGTALK_WEBHOOK: str = ""
    FEISHU_WEBHOOK: str = ""
    
    class Config:
        env_prefix = "CHANGE_ANALYSIS_"


change_analysis_settings = ChangeAnalysisSettings()
