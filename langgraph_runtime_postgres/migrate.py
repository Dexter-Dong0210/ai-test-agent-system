"""Wrapper for migration execution (for testing the Go server)."""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import asyncio
from pathlib import Path

from langgraph_runtime_postgres import database
from langgraph_runtime_postgres.database import (
    create_pool,
    migrate,
    migrate_vector_index,
)

# pragma: no cover  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2V0VsRFZnPT06ZjhmNzliNTQ=

async def migrate_for_tests():
    database._pg_pool = create_pool()
    database.config.MIGRATIONS_PATH = Path(__file__).parent / ".." / "migrations"
    # confirm connectivity
    await database._pg_pool.open(wait=True)

    await migrate()
    await migrate_vector_index()


if __name__ == "__main__":
    asyncio.run(migrate_for_tests())
# type: ignore  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2V0VsRFZnPT06ZjhmNzliNTQ=
