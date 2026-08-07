"""
项目API集成测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestProjectAPI:
    """项目API测试"""
    
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_root_endpoint(self, client: AsyncClient):
        """测试根路径"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    async def test_list_projects(self, client: AsyncClient, auth_headers):
        """测试获取项目列表"""
        response = await client.get(
            "/api/v2/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    async def test_create_project(self, client: AsyncClient, auth_headers):
        """测试创建项目"""
        response = await client.post(
            "/api/v2/projects",
            json={
                "name": "测试项目",
                "description": "这是一个测试项目"
            },
            headers=auth_headers
        )
        
        assert response.status_code in [200, 201]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])