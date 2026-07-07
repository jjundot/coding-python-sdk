# Coding Python SDK

基于 CODING.net OpenAPI 规范的 Python SDK，支持 Python 3.14+。

## 功能特性

- ✨ 完全自动生成的 SDK（基于 OpenAPI 3.0 规范）
- 🔐 支持多种认证方式：OAuth 2.0、个人访问令牌、项目令牌
- ⚡ 基于 `httpx` 的异步/同步 HTTP 客户端
- 📦 使用 `Pydantic` 进行强类型数据验证
- 🛠️ 使用 `uv` 管理依赖
- 🐍 Python 3.14+ 支持

## 安装

### 使用 uv（推荐）

```bash
uv pip install -e .
```

### 使用 pip

```bash
pip install -e .
```

## 快速开始

### 1. 设置认证

#### OAuth 2.0 认证

```python
from coding_sdk import CodingClient
from coding_sdk.auth import OAuth2Auth

auth = OAuth2Auth(
    team="your-team",
    client_id="your-client-id",
    client_secret="your-client-secret",
    access_token="your-access-token"
)

client = CodingClient(auth=auth)
```

#### 个人访问令牌认证

```python
from coding_sdk import CodingClient
from coding_sdk.auth import TokenAuth

auth = TokenAuth(
    team="your-team",
    token="your-personal-access-token"
)

client = CodingClient(auth=auth)
```

#### 项目令牌认证（Basic Auth）

```python
from coding_sdk import CodingClient
from coding_sdk.auth import BasicAuth

auth = BasicAuth(
    team="your-team",
    username="project-token-username",
    password="project-token-password"
)

client = CodingClient(auth=auth)
```

### 2. 使用 API

```python
import asyncio
from coding_sdk import CodingClient
from coding_sdk.auth import TokenAuth

async def main():
    auth = TokenAuth(team="your-team", token="your-token")
    client = CodingClient(auth=auth)
    
    try:
        # 获取当前用户信息
        user = await client.describe_coding_current_user()
        print(f"User: {user}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
```

## 支持的 API 模块

### 团队管理
- 团队相关接口
- 组织和成员相关接口

### 项目管理
- 项目相关接口
- 项目集相关接口
- 项目成员管理

### 代码管理
- 代码托管相关接口
- 代码扫描相关接口
- 合并请求（MR）管理

### 持续集成/部署
- 持续集成相关接口
- 持续部署相关接口
- 构建计划管理

### 制品管理
- 制品仓库相关接口
- 制品版本管理
- 制品属性配置

### 文档与知识
- Wiki 相关接口
- 文件网盘相关接口
- API 文档相关接口

### 其他功能
- 权限相关接口
- Service Hook 管理
- 测试管理相关接口
- 资产管理相关接口

## 认证权限范围（Scopes）

### OAuth 2.0 权限

- `user:profile:ro` - 用户信息只读
- `user:profile:rw` - 用户信息读写
- `project:profile:ro` - 项目信息只读
- `project:profile:rw` - 项目信息读写
- `team:member:rw` - 团队成员读写
- `vcs:repository:rw` - 代码仓库读写
- `cd:host-server:rw` - 持续部署主机组读写

详见 CODING OpenAPI 文档：https://coding.net/help/openapi

## API 限制

- 单团队单接口请求频率限制：每秒最多 30 次请求

## 开发指南

### 运行测试

```bash
uv run pytest
```

### 代码格式化

```bash
uv run black src/
```

### 类型检查

```bash
uv run mypy src/
```

### Lint 检查

```bash
uv run ruff check src/
```

## 项目结构

```
coding-python-sdk/
├── src/
│   └── coding_sdk/
│       ├── __init__.py
│       ├── client.py              # 主客户端
│       ├── auth.py                # 认证模块
│       ├── models/                # 数据模型
│       ├── api/                   # API 端点
│       └── exceptions.py          # 异常定义
├── tests/
│   ├── test_auth.py
│   └── test_client.py
├── docs/
│   └── openapi_ref/
│       └── document.yaml          # OpenAPI 规范
├── pyproject.toml
├── .python-version
└── README.md
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [CODING 官网](https://coding.net/)
- [CODING OpenAPI 文档](https://coding.net/help/openapi)
- [OpenAPI 规范](https://swagger.io/specification/)
