"""
缓存服务 - 基于Redis的装饰器缓存

提供高性能缓存能力，减少数据库查询压力
"""
import json
import hashlib
from typing import Optional, Callable, Any
from functools import wraps

import redis.asyncio as redis
from pydantic import BaseModel

from app.config.settings import settings


class CacheService:
    """Redis缓存服务"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    @property
    def client(self) -> redis.Redis:
        """懒加载Redis客户端"""
        if self._client is None:
            self._client = redis.from_url(
                settings.redis_uri,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        try:
            return await self.client.get(key)
        except Exception as e:
            print(f"[Cache] GET error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """设置缓存"""
        try:
            await self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            print(f"[Cache] SET error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            print(f"[Cache] DELETE error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """批量删除缓存（支持通配符）"""
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"[Cache] DELETE_PATTERN error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            print(f"[Cache] EXISTS error: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        try:
            return await self.client.ttl(key)
        except Exception as e:
            print(f"[Cache] TTL error: {e}")
            return -1
    
    async def get_stats(self) -> dict:
        """获取缓存统计信息"""
        try:
            info = await self.client.info()
            return {
                "used_memory": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            print(f"[Cache] STATS error: {e}")
            return {}


cache = CacheService()


def cache_result(
    ttl: int = 300,
    key_prefix: str = "",
    skip_cache: bool = False,
):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒），默认5分钟
        key_prefix: 缓存键前缀，建议使用模块名
        skip_cache: 是否跳过缓存（用于测试）
    
    Example:
        @cache_result(ttl=600, key_prefix="project")
        async def get_project(project_id: str):
            return await repo.get(project_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if skip_cache:
                return await func(*args, **kwargs)
            
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)
            
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                if cached_value == "__NULL__":
                    return None
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    return cached_value
            
            try:
                result = await func(*args, **kwargs)
                
                if result is not None:
                    if isinstance(result, BaseModel):
                        value = result.model_dump_json()
                    elif isinstance(result, list) and result and isinstance(result[0], BaseModel):
                        value = json.dumps([item.model_dump() for item in result])
                    elif isinstance(result, dict):
                        value = json.dumps(result)
                    else:
                        value = json.dumps(result)
                    
                    await cache.set(cache_key, value, ttl)
                else:
                    await cache.set(cache_key, "__NULL__", ttl=60)
                
                return result
            except Exception:
                raise
        
        wrapper.cache = cache
        wrapper.clear_cache = lambda: cache.delete_pattern(f"{key_prefix}:{func.__name__}:*")
        
        return wrapper
    return decorator


def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """生成缓存键"""
    filtered_args = []
    skip_first = True
    
    for i, arg in enumerate(args):
        if skip_first and i == 0:
            continue
        
        if isinstance(arg, (str, int, float, bool, type(None))):
            filtered_args.append(arg)
        elif hasattr(arg, '__class__') and arg.__class__.__name__ in ['str', 'int', 'float', 'bool']:
            filtered_args.append(str(arg))
    
    params_str = json.dumps({
        "args": filtered_args,
        "kwargs": {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool, type(None)))}
    }, sort_keys=True)
    
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
    
    return f"{prefix}:{func_name}:{params_hash}"


def invalidate_cache(*patterns: str):
    """
    缓存失效装饰器
    
    用于更新/删除操作时自动清除相关缓存
    
    Args:
        patterns: 缓存键模式（支持通配符）
    
    Example:
        @invalidate_cache("project:*", "folders:*")
        async def update_project(project_id: str, data: dict):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            result = await func(*args, **kwargs)
            
            for pattern in patterns:
                await cache.delete_pattern(pattern)
            
            return result
        return wrapper
    return decorator
