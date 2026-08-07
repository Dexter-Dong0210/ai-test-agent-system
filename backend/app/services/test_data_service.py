"""
测试数据管理服务

核心功能：数据池管理、Mock数据、数据生成、数据脱敏
"""
import re
import hashlib
import random
import string
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID
import json

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_data import (
    TestDataPool,
    MockDataConfig,
    DataGenerationTemplate,
    DataMaskingRule,
    DataType,
    DataSource,
    DataStatus
)
from app.repositories.base import BaseRepository
from app.utils.exceptions import NotFoundException, BadRequestException


class TestDataRepository(BaseRepository[TestDataPool]):
    """测试数据Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(TestDataPool, session)
    
    async def get_by_project(
        self,
        project_id: UUID,
        data_type: Optional[DataType] = None,
        status: Optional[DataStatus] = None,
        skip: int = 0,
        limit: int = 30
    ) -> List[TestDataPool]:
        """获取项目的测试数据列表"""
        
        query = select(TestDataPool).where(TestDataPool.project_id == project_id)
        
        if data_type:
            query = query.where(TestDataPool.data_type == data_type)
        
        if status:
            query = query.where(TestDataPool.status == status)
        
        query = query.order_by(TestDataPool.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()


class TestDataService:
    """测试数据管理服务"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TestDataRepository(session)
    
    async def create_data(
        self,
        project_id: UUID,
        name: str,
        code: str,
        data_type: DataType,
        data_content: dict,
        **kwargs
    ) -> TestDataPool:
        """创建测试数据"""
        
        # 检查code是否重复
        existing = await self.session.execute(
            select(TestDataPool).where(TestDataPool.code == code)
        )
        if existing.scalar_one_or_none():
            raise BadRequestException(f"数据代码 '{code}' 已存在")
        
        # 创建数据
        data = TestDataPool(
            project_id=project_id,
            name=name,
            code=code,
            data_type=data_type,
            data_content=data_content,
            data_source=kwargs.get("data_source", DataSource.MANUAL),
            description=kwargs.get("description"),
            tags=kwargs.get("tags", []),
            category=kwargs.get("category"),
            is_sensitive=kwargs.get("is_sensitive", False),
            sensitive_fields=kwargs.get("sensitive_fields", []),
            valid_from=kwargs.get("valid_from"),
            valid_until=kwargs.get("valid_until"),
            created_by=kwargs.get("created_by")
        )
        
        self.session.add(data)
        await self.session.commit()
        
        return data
    
    async def get_data(self, data_id: UUID) -> TestDataPool:
        """获取测试数据详情"""
        
        data = await self.repo.get(data_id)
        if not data:
            raise NotFoundException(f"测试数据 {data_id} 不存在")
        
        return data
    
    async def update_data(
        self,
        data_id: UUID,
        **kwargs
    ) -> TestDataPool:
        """更新测试数据"""
        
        data = await self.get_data(data_id)
        
        for key, value in kwargs.items():
            if hasattr(data, key) and value is not None:
                setattr(data, key, value)
        
        await self.session.commit()
        
        return data
    
    async def search_data(
        self,
        project_id: UUID,
        query_text: str,
        data_type: Optional[DataType] = None,
        skip: int = 0,
        limit: int = 30
    ) -> List[TestDataPool]:
        """搜索测试数据（按名称、描述、标签搜索）"""
        
        query = select(TestDataPool).where(TestDataPool.project_id == project_id)
        
        # 全文搜索
        query = query.where(
            TestDataPool.name.ilike(f"%{query_text}%") |
            TestDataPool.description.ilike(f"%{query_text}%") |
            TestDataPool.tags.contains([query_text])
        )
        
        if data_type:
            query = query.where(TestDataPool.data_type == data_type)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def mask_sensitive_data(
        self,
        data: TestDataPool
    ) -> dict:
        """数据脱敏"""
        
        content = data.data_content.copy()
        
        if not data.is_sensitive or not data.sensitive_fields:
            return content
        
        # 获取脱敏规则
        rules = await self.session.execute(
            select(DataMaskingRule).where(
                and_(
                    DataMaskingRule.project_id == data.project_id,
                    DataMaskingRule.is_enabled == True
                )
            )
        )
        rules = rules.scalars().all()
        
        # 应用脱敏
        for field in data.sensitive_fields:
            if field in content:
                for rule in rules:
                    if re.match(rule.field_pattern, field):
                        content[field] = self._apply_masking(
                            content[field],
                            rule
                        )
                        break
        
        return content
    
    def _apply_masking(self, value: str, rule: DataMaskingRule) -> str:
        """应用脱敏规则"""
        
        masking_type = rule.masking_type
        config = rule.masking_config
        
        if masking_type == "phone":
            # 手机号脱敏：138****8000
            if len(value) == 11:
                return value[:3] + "****" + value[-4:]
        
        elif masking_type == "email":
            # 邮箱脱敏：t***@example.com
            if "@" in value:
                username, domain = value.split("@", 1)
                return username[0] + "***@" + domain
        
        elif masking_type == "id_card":
            # 身份证脱敏：310***********1234
            if len(value) >= 15:
                return value[:3] + "***********" + value[-4:]
        
        elif masking_type == "hash":
            # 哈希脱敏
            return hashlib.sha256(value.encode()).hexdigest()[:16]
        
        elif masking_type == "random":
            # 随机替换
            return ''.join(random.choices(string.ascii_letters + string.digits, k=len(value)))
        
        return "***"
    
    async def generate_data_batch(
        self,
        template_id: UUID,
        count: int = 10
    ) -> List[TestDataPool]:
        """批量生成测试数据"""
        
        # 获取模板
        template = await self.session.execute(
            select(DataGenerationTemplate).where(DataGenerationTemplate.id == template_id)
        )
        template = template.scalar_one_or_none()
        
        if not template:
            raise NotFoundException(f"数据生成模板 {template_id} 不存在")
        
        generated_data = []
        
        # 生成数据
        for i in range(count):
            data_content = await self._generate_single_data(template)
            
            data = TestDataPool(
                project_id=template.project_id,
                name=f"{template.name}_{i+1}",
                code=f"{template.name.lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                data_type=template.data_type,
                data_source=DataSource.AI_GENERATED,
                data_content=data_content
            )
            
            self.session.add(data)
            generated_data.append(data)
        
        await self.session.commit()
        
        return generated_data
    
    async def _generate_single_data(self, template: DataGenerationTemplate) -> dict:
        """生成单条数据"""
        
        data = {}
        
        for field_config in template.template_config.get("fields", []):
            field_name = field_config["name"]
            generator = field_config.get("generator")
            
            if generator == "uuid":
                data[field_name] = str(UUID(int=random.randint(0, 2**128)))
            
            elif generator == "username":
                data[field_name] = f"user_{random.randint(1000, 9999)}"
            
            elif generator == "email":
                data[field_name] = f"test{random.randint(1000, 9999)}@example.com"
            
            elif generator == "phone":
                data[field_name] = f"138{random.randint(10000000, 99999999)}"
            
            elif generator == "number":
                min_val = field_config.get("min", 0)
                max_val = field_config.get("max", 100)
                data[field_name] = random.randint(min_val, max_val)
            
            elif generator == "string":
                length = field_config.get("length", 10)
                data[field_name] = ''.join(random.choices(string.ascii_letters, k=length))
            
            else:
                data[field_name] = None
        
        # 应用默认值
        for key, value in template.default_values.items():
            if key not in data:
                data[key] = value
        
        return data
    
    async def create_mock_config(
        self,
        project_id: UUID,
        name: str,
        api_endpoint: str,
        http_method: str,
        mock_data: dict,
        **kwargs
    ) -> MockDataConfig:
        """创建Mock数据配置"""
        
        mock = MockDataConfig(
            project_id=project_id,
            name=name,
            api_endpoint=api_endpoint,
            http_method=http_method,
            mock_strategy=kwargs.get("mock_strategy", "static"),
            mock_data=mock_data,
            mock_script=kwargs.get("mock_script"),
            response_delay=kwargs.get("response_delay", 0),
            status_code=kwargs.get("status_code", 200),
            response_headers=kwargs.get("response_headers", {}),
            match_rules=kwargs.get("match_rules", [])
        )
        
        self.session.add(mock)
        await self.session.commit()
        
        return mock
    
    async def get_mock_response(
        self,
        project_id: UUID,
        api_endpoint: str,
        http_method: str,
        request_data: Optional[dict] = None
    ) -> Optional[dict]:
        """获取Mock响应"""
        
        # 查找匹配的Mock配置
        result = await self.session.execute(
            select(MockDataConfig).where(
                and_(
                    MockDataConfig.project_id == project_id,
                    MockDataConfig.api_endpoint == api_endpoint,
                    MockDataConfig.http_method == http_method,
                    MockDataConfig.is_enabled == True
                )
            )
        )
        mock_config = result.scalar_one_or_none()
        
        if not mock_config:
            return None
        
        # 更新命中统计
        mock_config.hit_count += 1
        mock_config.last_hit_at = datetime.now()
        await self.session.commit()
        
        # 根据策略返回数据
        if mock_config.mock_strategy == "static":
            return mock_config.mock_data
        
        elif mock_config.mock_strategy == "random":
            # 从列表中随机选择
            if isinstance(mock_config.mock_data, list):
                return random.choice(mock_config.mock_data)
        
        elif mock_config.mock_strategy == "script":
            # 执行脚本（需要安全沙箱）
            # TODO: 实现安全的脚本执行环境
            return mock_config.mock_data
        
        return mock_config.mock_data
    
    async def link_test_case(
        self,
        data_id: UUID,
        test_case_id: UUID
    ) -> TestDataPool:
        """关联测试用例"""
        
        data = await self.get_data(data_id)
        
        if test_case_id not in data.linked_test_cases:
            data.linked_test_cases.append(test_case_id)
            await self.session.commit()
        
        return data
    
    async def get_usage_statistics(self, project_id: UUID) -> Dict:
        """获取使用统计"""
        
        # 按类型统计
        type_counts = {}
        for data_type in DataType:
            result = await self.session.execute(
                select(TestDataPool).where(
                    and_(
                        TestDataPool.project_id == project_id,
                        TestDataPool.data_type == data_type
                    )
                )
            )
            type_counts[data_type.value] = len(result.scalars().all())
        
        # 按状态统计
        status_counts = {}
        for status in DataStatus:
            result = await self.session.execute(
                select(TestDataPool).where(
                    and_(
                        TestDataPool.project_id == project_id,
                        TestDataPool.status == status
                    )
                )
            )
            status_counts[status.value] = len(result.scalars().all())
        
        return {
            "total": sum(type_counts.values()),
            "by_type": type_counts,
            "by_status": status_counts
        }