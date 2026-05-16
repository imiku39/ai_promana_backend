# AI Promana Backend

一个基于 FastAPI 的用户认证系统后端，包含完整的用户注册、登录功能。

## 技术栈

- **Web 框架**: FastAPI ≥0.104.1
- **Python 版本**: 3.10+
- **数据库**: MySQL 8.0+
- **数据验证**: Pydantic ≥2.5.2
- **认证**: python-jose (JWT)
- **密码加密**: passlib (bcrypt)
- **ASGI 服务器**: Uvicorn ≥0.24.0

## 项目结构

```
ai_promana_backend/
├── main.py                    # 应用入口
├── database_setup.py          # 数据库初始化脚本
├── pyproject.toml            # 项目配置
├── setup.py                  # 包配置
├── .env                      # 环境变量（需要配置）
├── .env.example             # 环境变量示例
├── .gitignore               # Git忽略文件
└── src/
    └── ai_promana_backend/  # 主包
        ├── __init__.py
        ├── config.py        # 配置管理
        ├── database.py      # 数据库连接
        ├── api/
        │   └── v1/
        │       ├── routes.py
        │       └── endpoints/
        │           └── users.py
        ├── core/
        │   └── security.py
        ├── schemas/
        │   └── user.py
        ├── models/
        ├── services/
        ├── tasks/
        ├── utils/
        └── middleware/
```

## 快速开始

### 1. 配置环境变量

复制 `.env.example` 为 `.env` 并编辑：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，填入你的数据库连接信息：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=ai_promana_db

SECRET_KEY=your_secret_key_here_must_be_32_characters_long_minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
```

**重要提示**：`SECRET_KEY` 必须至少32个字符，建议使用强随机字符串。

### 2. 安装依赖

```bash
pip install fastapi uvicorn pymysql pydantic pydantic-settings python-jose passlib python-multipart python-dotenv
```

### 3. 初始化数据库

```bash
python database_setup.py
```

### 4. 运行应用

```bash
# 开发模式（推荐）
python main.py

# 或者使用 uvicorn 直接启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

<br />

### 5. 访问 API 文档

启动应用后，访问以下地址查看 API 文档：

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## API 接口

### 1. 用户注册

**路径**: `POST /api/v1/users/register`

**请求体**:

```json
{
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "password": "password123",
    "full_name": "测试用户"
}
```

**响应**:

```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "phone": "13800138000",
    "full_name": "测试用户",
    "role": "user",
    "created_at": "2024-01-01 00:00:00",
    "updated_at": "2024-01-01 00:00:00"
}
```

### 2. 用户登录

**路径**: `POST /api/v1/users/login`

**请求体**:

```json
{
    "username": "testuser",
    "password": "password123"
}
```

**响应**:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "phone": "13800138000",
        "full_name": "测试用户",
        "role": "user",
        "created_at": "2024-01-01 00:00:00",
        "updated_at": "2024-01-01 00:00:00"
    }
}
```

### 3. 健康检查

**路径**: `GET /`

**响应**:

```json
{
    "status": "ok",
    "service": "ai-promana-backend"
}
```

## 数据库表结构

### users 表

| 字段          | 类型              | 说明             |
| ----------- | --------------- | -------------- |
| id          | BIGINT UNSIGNED | 主键，自增          |
| username    | VARCHAR(50)     | 用户名，唯一         |
| email       | VARCHAR(255)    | 邮箱，唯一，可空       |
| phone       | VARCHAR(20)     | 手机号，唯一，可空      |
| password    | VARCHAR(255)    | 密码哈希           |
| full\_name  | VARCHAR(100)    | 真实姓名，可空        |
| role        | VARCHAR(20)     | 用户角色，默认 'user' |
| created\_at | DATETIME        | 创建时间           |
| updated\_at | DATETIME        | 更新时间           |

## 开发说明

### 密码安全

密码使用 bcrypt 加密存储，哈希强度自动管理。

### JWT 认证

- 使用 HS256 算法签名
- 默认有效期 30 分钟
- Token 包含：用户 ID、用户名、角色信息
- `/api/*` 受保护接口统一使用 `Authorization: Bearer <access_token>` 认证
- Swagger UI 可在右上角点击 `Authorize`，直接粘贴登录返回的 `access_token`

## 常见问题

### 1. 数据库连接失败

检查 `.env` 文件中的数据库配置是否正确，确保 MySQL 服务已启动。

### 2. 端口被占用

修改 `.env` 文件中的 `APP_PORT` 为其他端口。

### 3. 权限被拒绝

确保 MySQL 用户有创建数据库和表的权限。

## 许可证

MIT License
