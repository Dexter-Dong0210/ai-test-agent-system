"""
数据库连接配置

管理 PostgreSQL 和 MongoDB 的连接
"""

from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config.settings import settings
# pylint: disable  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2Y2tVMmNnPT06MTQ3YzY2Yjk=


# ==================== PostgreSQL 配置 ====================

# 创建异步引擎（优化连接池配置）
engine = create_async_engine(
    settings.postgres_url,
    echo=settings.debug,
    # 连接池配置
    pool_size=20,           # 常驻连接数
    max_overflow=10,        # 最大溢出连接数
    pool_pre_ping=True,     # 连接健康检查
    pool_recycle=3600,      # 连接回收时间（秒）
    # 性能优化
    pool_timeout=30,        # 获取连接超时时间
    connect_args={
        "server_settings": {
            "jit": "off",  # 禁用JIT提高稳定性
        },
        "command_timeout": 60,
    }
)
# type: ignore  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2Y2tVMmNnPT06MTQ3YzY2Yjk=

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库表（开发态使用）。

    生产环境一律走 ``alembic upgrade head``。这里的 ``create_all`` 只在
    ``settings.debug`` 模式下被 [app/main.py](app/main.py) 调用，方便
    快速搭建本地或测试环境。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
# pragma: no cover  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2Y2tVMmNnPT06MTQ3YzY2Yjk=


# ==================== MongoDB 配置 ====================

class MongoDB:
    """MongoDB 连接管理器"""
    
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None
    
    @classmethod
    async def connect(cls) -> None:
        """建立 MongoDB 连接"""
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.database = cls.client[settings.mongodb_db]
    
    @classmethod
    async def disconnect(cls) -> None:
        """关闭 MongoDB 连接"""
        if cls.client:
            cls.client.close()
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """获取数据库实例"""
        return cls.database


async def get_mongodb() -> AsyncIOMotorDatabase:
    """
    获取 MongoDB 数据库的依赖注入函数
    
    Returns:
        AsyncIOMotorDatabase: MongoDB 数据库实例
    """
    return MongoDB.get_database()

# type: ignore  My80OmFIVnBZMlhva2FQbHNJL21tS1U2Y2tVMmNnPT06MTQ3YzY2Yjk=
