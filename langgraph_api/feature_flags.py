"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import os
# fmt: off  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2WkZCa05nPT06Mjc4M2VjMTU=

from langgraph.version import __version__

# Only gate features on the major.minor version; Lets you ignore the rc/alpha/etc. releases anyway
LANGGRAPH_PY_MINOR = tuple(map(int, __version__.split(".")[:2]))
# pragma: no cover  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2WkZCa05nPT06Mjc4M2VjMTU=

OMIT_PENDING_SENDS = LANGGRAPH_PY_MINOR >= (0, 5)
USE_RUNTIME_CONTEXT_API = LANGGRAPH_PY_MINOR >= (0, 6)
USE_NEW_INTERRUPTS = LANGGRAPH_PY_MINOR >= (0, 6)
USE_DURABILITY = LANGGRAPH_PY_MINOR >= (0, 6)

# Feature flag for new gRPC-based persistence layer
FF_USE_CORE_API = os.getenv("FF_USE_CORE_API", "false").lower() in (
    "true",
    "1",
    "yes",
)
# Feature flag for using the JS native API
FF_USE_JS_API = os.getenv("FF_USE_JS_API", "false").lower() in (
    "true",
    "1",
    "yes",
)
