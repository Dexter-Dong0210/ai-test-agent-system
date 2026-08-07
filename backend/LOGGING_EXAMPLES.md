"""
结构化日志使用示例

展示如何在应用中使用结构化日志
"""
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExampleService:
    """示例服务"""
    
    async def process_data(self, project_id: str, user_id: str):
        """处理数据示例"""
        
        # ✅ 推荐：结构化日志
        logger.info(
            "processing_data",
            project_id=project_id,
            user_id=user_id,
            action="process"
        )
        
        try:
            # 业务逻辑
            result = await self._do_work(project_id)
            
            # 成功日志
            logger.info(
                "data_processed_successfully",
                project_id=project_id,
                result_size=len(result)
            )
            
            return result
            
        except Exception as e:
            # 错误日志（包含堆栈跟踪）
            logger.error(
                "data_processing_failed",
                project_id=project_id,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def _do_work(self, project_id: str):
        # 模拟工作
        return {"status": "ok"}


# ============================================================
# 日志输出示例
# ============================================================

# 控制台彩色输出：
# 2026-06-10 14:23:45 [info     ] processing_data 
#     project_id=TEST-001 user_id=user-123 action=process

# JSON格式输出（生产环境）：
# {
#   "event": "processing_data",
#   "project_id": "TEST-001",
#   "user_id": "user-123",
#   "action": "process",
#   "level": "info",
#   "timestamp": "2026-06-10T14:23:45Z",
#   "app_name": "但问智能测试平台",
#   "app_version": "2.0.0",
#   "environment": "production"
# }


# ============================================================
# 常用日志模式
# ============================================================

# 1. 记录API请求
logger.info(
    "api_request",
    method="GET",
    path="/api/v2/projects",
    user_id=user_id,
    ip_address=client_ip
)

# 2. 记录数据库操作
logger.debug(
    "database_query",
    table="projects",
    operation="select",
    duration_ms=45
)

# 3. 记录缓存操作
logger.debug(
    "cache_operation",
    action="get",
    key="project:TEST-001",
    hit=True
)

# 4. 记录性能指标
logger.info(
    "performance_metric",
    endpoint="/api/v2/projects",
    response_time_ms=125,
    status_code=200
)

# 5. 记录业务事件
logger.info(
    "test_case_created",
    project_id=project_id,
    test_case_id=test_case_id,
    user_id=user_id
)

# 6. 记录错误和异常
logger.error(
    "database_connection_failed",
    error=str(e),
    retry_count=3,
    exc_info=True
)


# ============================================================
# 使用上下文
# ============================================================

import structlog

# 设置请求上下文
structlog.contextvars.bind_contextvars(
    request_id="req-123",
    user_id="user-456"
)

# 后续日志自动包含上下文
logger.info("processing_request")  
# 自动包含 request_id 和 user_id

# 清除上下文
structlog.contextvars.unbind_contextvars("request_id", "user_id")


# ============================================================
# 与传统日志对比
# ============================================================

# ❌ 传统日志（不推荐）
print(f"[INFO] Processing project {project_id} for user {user_id}")

# ✅ 结构化日志（推荐）
logger.info("processing_project", project_id=project_id, user_id=user_id)

# 优势：
# 1. 可搜索：可以用字段搜索日志
# 2. 可聚合：可以统计特定事件的频率
# 3. 可监控：可以设置告警规则
# 4. 可分析：可以导出到ELK/Splunk分析