"""
结构化日志配置

使用 structlog 提供结构化、可搜索的日志输出
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app.config.settings import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """添加应用上下文信息"""
    event_dict["app_name"] = settings.app_name
    event_dict["app_version"] = settings.app_version
    event_dict["environment"] = "development" if settings.debug else "production"
    return event_dict


def drop_color_message_key(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """移除颜色消息键（用于文件输出）"""
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging() -> None:
    """配置结构化日志"""
    
    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.debug else logging.INFO,
    )
    
    # 配置structlog处理器
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        add_app_context,
    ]
    
    # 控制台输出使用彩色格式
    if sys.stdout.isatty():
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        # 非TTY环境使用JSON格式
        processors.extend([
            drop_color_message_key,
            structlog.processor.format_exc_info,
            structlog.processors.JSONRenderer(),
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.debug else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # 配置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.BoundLogger:
    """获取结构化日志器"""
    return structlog.get_logger(name)


# 初始化日志配置
setup_logging()

# 全局日志器
logger = get_logger(__name__)