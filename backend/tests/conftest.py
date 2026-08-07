"""
测试配置文件

提供测试用的fixtures和通用配置
"""
import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.settings import settings
from app.config.database import Base
from app.main import create_app


# 测试数据库URL（使用SQLite内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_id():
    """测试用户ID"""
    return uuid4()


@pytest.fixture
def test_project_identifier():
    """测试项目标识符"""
    return "TEST-001"


@pytest.fixture
def auth_headers(test_user_id):
    """认证头"""
    from jose import jwt
    from datetime import datetime, timedelta
    
    token_data = {
        "sub": str(test_user_id),
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    
    token = jwt.encode(token_data, "test-secret", algorithm="HS256")
    
    return {"Authorization": f"Bearer {token}"}