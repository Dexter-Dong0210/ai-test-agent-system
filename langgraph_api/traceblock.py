"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import os
from urllib.parse import urlparse
# pylint: disable  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2VG1RMGVRPT06MzdkY2Y4ZDQ=

from requests.sessions import Session

_HOST = "api.smith.langchain.com"
_PATH_PREFIX = "/runs"


def patch_requests():
    if os.getenv("LANGSMITH_DISABLE_SAAS_RUNS") != "true":
        return
    _orig = Session.request

    def _guard(self, method, url, *a, **kw):
        if method.upper() == "POST":
            u = urlparse(url)
            if u.hostname == _HOST and _PATH_PREFIX in u.path:
                raise RuntimeError(f"POST to {url} blocked by policy")
        return _orig(self, method, url, *a, **kw)
# fmt: off  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2VG1RMGVRPT06MzdkY2Y4ZDQ=

    Session.request = _guard  # type: ignore[invalid-assignment]
