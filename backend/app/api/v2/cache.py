"""
缓存管理 API

提供缓存统计和手动清除功能
"""

from fastapi import APIRouter, HTTPException

from app.services.cache_service import cache
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/cache", tags=["缓存管理"])


@router.get(
    "/stats",
    summary="获取缓存统计信息",
    description="获取Redis缓存的统计信息，包括内存使用、命中率等"
)
async def get_cache_stats():
    """
    获取缓存统计信息
    
    Returns:
        dict: 缓存统计信息
    """
    try:
        stats = await cache.get_stats()
        
        hits = stats.get("keyspace_hits", 0)
        misses = stats.get("keyspace_misses", 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        return {
            "success": True,
            "data": {
                "used_memory": stats.get("used_memory", "0B"),
                "connected_clients": stats.get("connected_clients", 0),
                "total_commands_processed": stats.get("total_commands_processed", 0),
                "keyspace_hits": hits,
                "keyspace_misses": misses,
                "hit_rate": f"{hit_rate:.2f}%",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@router.delete(
    "/clear/{pattern}",
    summary="清除缓存",
    description="根据模式清除缓存，支持通配符（如 project:*、folders:*）"
)
async def clear_cache(pattern: str):
    """
    清除缓存
    
    Args:
        pattern: 缓存键模式（支持通配符）
    
    Returns:
        SuccessResponse: 清除结果
    """
    try:
        count = await cache.delete_pattern(f"{pattern}:*")
        return SuccessResponse(
            success=True,
            message=f"成功清除 {count} 个缓存项"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")


@router.get(
    "/health",
    summary="缓存健康检查",
    description="检查Redis连接状态"
)
async def cache_health():
    """
    缓存健康检查
    
    Returns:
        dict: 健康状态
    """
    try:
        await cache.client.ping()
        return {
            "status": "healthy",
            "message": "Redis连接正常"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Redis连接失败: {str(e)}"
        }
