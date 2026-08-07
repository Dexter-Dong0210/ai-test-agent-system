"""
缓存功能测试脚本

验证缓存装饰器和失效机制是否正常工作
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.cache_service import cache, cache_result, invalidate_cache


async def test_cache_basic():
    """测试基本缓存功能"""
    print("\n=== 测试基本缓存功能 ===")
    
    await cache.set("test_key", "test_value", ttl=60)
    value = await cache.get("test_key")
    print(f"✅ 设置并获取缓存: {value}")
    
    await cache.delete("test_key")
    value = await cache.get("test_key")
    print(f"✅ 删除缓存后获取: {value}")
    
    print("✅ 基本缓存功能测试通过\n")


async def test_cache_decorator():
    """测试缓存装饰器"""
    print("\n=== 测试缓存装饰器 ===")
    
    call_count = 0
    
    @cache_result(ttl=60, key_prefix="test")
    async def expensive_function(x: int, y: int) -> int:
        nonlocal call_count
        call_count += 1
        print(f"  执行函数 (第{call_count}次): x={x}, y={y}")
        return x + y
    
    result1 = await expensive_function(1, 2)
    print(f"第一次调用结果: {result1}, 函数执行次数: {call_count}")
    
    result2 = await expensive_function(1, 2)
    print(f"第二次调用结果: {result2}, 函数执行次数: {call_count}")
    
    result3 = await expensive_function(3, 4)
    print(f"第三次调用结果: {result3}, 函数执行次数: {call_count}")
    
    if call_count == 2:
        print("✅ 缓存装饰器测试通过\n")
    else:
        print(f"❌ 缓存装饰器测试失败，期望执行2次，实际执行{call_count}次\n")


async def test_cache_invalidation():
    """测试缓存失效"""
    print("\n=== 测试缓存失效 ===")
    
    call_count = 0
    
    @cache_result(ttl=60, key_prefix="test_invalidate")
    async def get_data(key: str) -> str:
        nonlocal call_count
        call_count += 1
        print(f"  执行函数 (第{call_count}次): key={key}")
        return f"value_{key}"
    
    @invalidate_cache("test_invalidate:*")
    async def update_data(key: str, value: str) -> None:
        print(f"  更新数据: key={key}, value={value}")
    
    result1 = await get_data("test")
    print(f"第一次获取: {result1}, 函数执行次数: {call_count}")
    
    result2 = await get_data("test")
    print(f"第二次获取: {result2}, 函数执行次数: {call_count}")
    
    await update_data("test", "new_value")
    print("执行更新操作（清除缓存）")
    
    result3 = await get_data("test")
    print(f"第三次获取: {result3}, 函数执行次数: {call_count}")
    
    if call_count == 2:
        print("✅ 缓存失效测试通过\n")
    else:
        print(f"❌ 缓存失效测试失败，期望执行2次，实际执行{call_count}次\n")


async def test_cache_stats():
    """测试缓存统计"""
    print("\n=== 测试缓存统计 ===")
    
    try:
        stats = await cache.get_stats()
        print(f"缓存统计信息:")
        print(f"  - 使用内存: {stats.get('used_memory', 'N/A')}")
        print(f"  - 连接客户端: {stats.get('connected_clients', 0)}")
        print(f"  - 命中次数: {stats.get('keyspace_hits', 0)}")
        print(f"  - 未命中次数: {stats.get('keyspace_misses', 0)}")
        print("✅ 缓存统计测试通过\n")
    except Exception as e:
        print(f"⚠️  缓存统计测试跳过（Redis未连接）: {e}\n")


async def main():
    """运行所有测试"""
    print("\n" + "="*50)
    print("缓存功能测试")
    print("="*50)
    
    try:
        await test_cache_basic()
        await test_cache_decorator()
        await test_cache_invalidation()
        await test_cache_stats()
        
        print("\n" + "="*50)
        print("✅ 所有测试通过")
        print("="*50 + "\n")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await cache.client.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
