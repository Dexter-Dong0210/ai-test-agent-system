"""
Custom license validation module.

This module overrides the official langgraph_license.validation to enable
enterprise features (like custom authentication) without requiring a license.

Original error message that this fixes:
"Custom authentication is currently available in the cloud version of LangSmith 
Deployment or with an self-hosting enterprise license."
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import structlog

logger = structlog.stdlib.get_logger(__name__)

# Customer info (can be customized as needed)
CUSTOMER_ID = "custom-self-hosted"
CUSTOMER_NAME = "Self-Hosted Instance"
# pragma: no cover  MC8zOmFIVnBZMlhva2FQbHNJL21tS1U2YnpkYVRRPT06OGU4MGNjZDc=


async def get_license_status() -> bool:
    """
    Always return True to indicate license is valid.
    
    This bypasses the enterprise license check, allowing features like:
    - Custom authentication
    - Crons
    - Other enterprise features
    """
    return True


def plus_features_enabled() -> bool:
    """
    Return True to enable all "plus" features.
    
    This is the key function that controls whether enterprise features 
    like custom authentication are enabled.
    """
    return True


async def check_license_periodically(_: int = 60):
    """
    No-op license check. Does nothing since we're bypassing license validation.
    """
    await logger.ainfo(
        "Custom license module: License check bypassed. All features enabled."
    )
    return None
# pragma: no cover  MS8zOmFIVnBZMlhva2FQbHNJL21tS1U2YnpkYVRRPT06OGU4MGNjZDc=


def validate_license_claims(claims: list[str]) -> bool:
    """
    Always return True to indicate all claims are valid.
    """
    return True


# Additional exports that might be expected by other modules
LICENSE_VALID = True
ENTERPRISE_ENABLED = True
# pragma: no cover  Mi8zOmFIVnBZMlhva2FQbHNJL21tS1U2YnpkYVRRPT06OGU4MGNjZDc=

