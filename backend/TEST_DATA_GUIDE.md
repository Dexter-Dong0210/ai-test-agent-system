# 测试数据管理使用指南

## 📖 概述

测试数据管理功能提供**数据池、Mock数据、数据生成、数据脱敏**一站式解决方案，解决测试数据混乱问题。

---

## 🎯 核心功能

### 1. 测试数据池
- ✅ 多类型数据管理（用户/订单/商品等）
- ✅ 数据版本控制
- ✅ 有效期管理
- ✅ 使用统计追踪

### 2. Mock数据服务
- ✅ 多种Mock策略（静态/随机/脚本/AI）
- ✅ API级别Mock配置
- ✅ 条件匹配规则
- ✅ 响应延迟模拟

### 3. 数据生成
- ✅ AI辅助数据生成
- ✅ 批量生成（1-100条）
- ✅ 自定义生成规则
- ✅ 唯一性保证

### 4. 数据脱敏
- ✅ 自动脱敏敏感字段
- ✅ 多种脱敏算法（手机号/邮箱/身份证/哈希）
- ✅ 自定义脱敏规则
- ✅ 合规性支持

---

## 🚀 快速开始

### 1. 创建测试数据

```bash
POST /api/v2/projects/{project_id}/test-data

{
  "name": "测试用户数据",
  "code": "USER_001",
  "data_type": "user",
  "data_content": {
    "user_id": "001",
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000"
  },
  "is_sensitive": true,
  "sensitive_fields": ["phone"]
}
```

### 2. 查看数据（自动脱敏）

```bash
GET /api/v2/projects/{project_id}/test-data/{data_id}

# 响应（自动脱敏）
{
  "id": "uuid",
  "name": "测试用户数据",
  "data_content": {
    "user_id": "001",
    "username": "testuser",
    "email": "test@example.com",
    "phone": "138****8000"  # 已脱敏
  }
}
```

### 3. 创建Mock配置

```bash
POST /api/v2/projects/{project_id}/test-data/mock

{
  "name": "用户信息Mock",
  "api_endpoint": "/api/v1/users/{user_id}",
  "http_method": "GET",
  "mock_strategy": "static",
  "mock_data": {
    "code": 200,
    "data": {
      "user_id": "001",
      "name": "Test User"
    }
  },
  "response_delay": 100
}
```

### 4. 执行Mock请求

```bash
POST /api/v2/projects/{project_id}/test-data/mock/execute?api_endpoint=/api/v1/users/001&http_method=GET

# 响应
{
  "code": 200,
  "data": {
    "user_id": "001",
    "name": "Test User"
  }
}
```

---

## 📊 数据类型分类

| 数据类型 | 说明 | 典型字段 |
|---------|------|----------|
| **USER** | 用户数据 | user_id, username, email, phone |
| **ORDER** | 订单数据 | order_id, user_id, amount, status |
| **PRODUCT** | 商品数据 | product_id, name, price, inventory |
| **PAYMENT** | 支付数据 | payment_id, order_id, method, amount |
| **INVENTORY** | 库存数据 | sku_id, quantity, location |
| **CUSTOM** | 自定义数据 | 根据业务定义 |

---

## 💡 使用场景

### 场景1：用户注册测试

```python
# 1. 创建用户数据池
service.create_data(
    name="注册用户池",
    code="REG_POOL",
    data_type=DataType.USER,
    data_content={
        "username": "testuser001",
        "password": "encrypted_password",
        "email": "test001@example.com"
    }
)

# 2. 关联测试用例
service.link_test_case(data_id, test_case_id)

# 3. 测试时自动获取
user_data = await service.get_data(data_id)
```

### 场景2：API Mock测试

```python
# 1. 配置Mock
mock_config = await service.create_mock_config(
    name="订单查询Mock",
    api_endpoint="/api/v1/orders/{order_id}",
    http_method="GET",
    mock_strategy="random",
    mock_data=[
        {"status": "pending"},
        {"status": "shipped"},
        {"status": "delivered"}
    ]
)

# 2. 测试时调用Mock
response = await service.get_mock_response(
    project_id,
    "/api/v1/orders/001",
    "GET"
)
```

### 场景3：批量生成测试数据

```python
# 1. 创建数据生成模板
template = DataGenerationTemplate(
    name="用户数据模板",
    data_type=DataType.USER,
    template_config={
        "fields": [
            {"name": "user_id", "generator": "uuid"},
            {"name": "username", "generator": "username"},
            {"name": "email", "generator": "email"},
            {"name": "age", "generator": "number", "min": 18, "max": 65}
        ]
    },
    default_values={"status": "active"}
)

# 2. 批量生成100条数据
generated = await service.generate_data_batch(template.id, count=100)
```

---

## 🔒 数据脱敏规则

### 内置脱敏算法

| 算法 | 说明 | 示例 |
|------|------|------|
| **phone** | 手机号脱敏 | 138****8000 |
| **email** | 邮箱脱敏 | t***@example.com |
| **id_card** | 身份证脱敏 | 310***********1234 |
| **hash** | 哈希脱敏 | a1b2c3d4e5f6... |
| **random** | 随机替换 | xK9mL2pQ... |

### 自定义脱敏规则

```python
# 创建自定义规则
rule = DataMaskingRule(
    name="自定义密码脱敏",
    field_pattern="*password*",
    masking_type="hash",
    masking_config={
        "algorithm": "sha256",
        "length": 16
    }
)
```

---

## 🎯 最佳实践

### 1. 数据命名规范
```
{项目}_{数据类型}_{序号}
示例：ORDER_USER_001
```

### 2. 敏感字段标记
```python
is_sensitive = True
sensitive_fields = ["password", "id_card", "phone"]
```

### 3. 有效期管理
```python
valid_from = datetime.now()
valid_until = datetime.now() + timedelta(days=30)  # 30天有效期
```

### 4. 数据复用
```python
# 关联到多个测试用例
await service.link_test_case(data_id, test_case_id_1)
await service.link_test_case(data_id, test_case_id_2)
```

---

## 📈 使用统计

### 查看统计信息

```bash
GET /api/v2/projects/{project_id}/test-data/statistics

# 响应
{
  "total": 150,
  "by_type": {
    "user": 50,
    "order": 40,
    "product": 60
  },
  "by_status": {
    "active": 120,
    "inactive": 20,
    "expired": 10
  }
}
```

---

## 🔄 Mock策略选择

| 策略 | 适用场景 | 特点 |
|------|----------|------|
| **static** | 固定返回值 | 简单稳定 |
| **random** | 随机返回 | 模拟真实场景 |
| **script** | 动态生成 | 灵活可控 |
| **ai** | AI生成 | 智能推荐 |

---

## 📝 数据生成器

### 内置生成器

| 生成器 | 说明 | 示例输出 |
|--------|------|----------|
| **uuid** | UUID | "550e8400-e29b-41d4-a716-446655440000" |
| **username** | 用户名 | "user_1234" |
| **email** | 邮箱 | "test1234@example.com" |
| **phone** | 手机号 | "13800138000" |
| **number** | 数字 | 42 |
| **string** | 字符串 | "abcdefghij" |

---

## 🎊 典型工作流

### 测试准备阶段
```
1. 创建数据池（手动/AI生成）
2. 配置Mock数据（如果需要）
3. 关联测试用例
4. 设置有效期
```

### 测试执行阶段
```
1. 获取测试数据（自动脱敏）
2. 使用数据执行测试
3. 记录使用情况
```

### 测试维护阶段
```
1. 更新数据内容
2. 检查数据有效性
3. 清理过期数据
```

---

**更新时间**: 2026-06-10  
**维护者**: AI测试平台团队