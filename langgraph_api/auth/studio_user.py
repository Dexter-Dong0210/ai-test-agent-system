"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from langgraph_sdk.auth.types import StudioUser as StudioUserBase
from starlette.authentication import BaseUser
# type: ignore  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2VDNGc05nPT06ODBiNmI2MzA=


class StudioUser(StudioUserBase, BaseUser):
    """StudioUser class."""
# type: ignore  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2VDNGc05nPT06ODBiNmI2MzA=

    def dict(self):
        return {
            "kind": "StudioUser",
            "is_authenticated": self.is_authenticated,
            "display_name": self.display_name,
            "identity": self.identity,
            "permissions": self.permissions,
        }
