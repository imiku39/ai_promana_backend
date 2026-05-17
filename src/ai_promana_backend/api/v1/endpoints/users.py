# TODO: /api/auth/* 当前为首版契约接口，后续需要与旧 /api/v1/users/* 统一认证模型、token 刷新和权限依赖。
from typing import Any

from fastapi import APIRouter, Body, Depends, Header, HTTPException
import pymysql
from datetime import datetime, timedelta
from ai_promana_backend.database import get_connection, get_db
from ai_promana_backend.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from ai_promana_backend.schemas.user import UserCreate, UserLogin, UserOut, LoginResponse
from ai_promana_backend.api.v1.endpoints import _mock

router = APIRouter()

@router.post("/register", response_model=UserOut, summary="用户注册", description="创建新用户账户")
def register_user(
    payload: UserCreate,
    db: pymysql.connections.Connection = Depends(get_db)
):
    cursor = None
    try:
        cursor = db.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = %s", (payload.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        if payload.email:
            cursor.execute("SELECT id FROM users WHERE email = %s", (payload.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 检查手机号是否已存在
        if payload.phone:
            cursor.execute("SELECT id FROM users WHERE phone = %s", (payload.phone,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="手机号已被注册")
        
        # 哈希密码
        hashed_password = get_password_hash(payload.password)
        
        # 插入用户记录
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email = payload.email or f"{payload.username}@example.local"
        insert_sql = """
        INSERT INTO users (username, email, phone, password_hash, real_name, role, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_sql,
            (
                payload.username,
                email,
                payload.phone,
                hashed_password,
                payload.full_name or payload.username,
                "user",
                now,
                now
            )
        )
        user_id = cursor.lastrowid
        db.commit()
        
        # 查询新创建的用户
        cursor.execute(
            "SELECT id, username, email, phone, real_name AS full_name, role, created_at, updated_at FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        return UserOut(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            phone=user["phone"],
            full_name=user["full_name"],
            role=user["role"],
            created_at=user["created_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(user["created_at"], "strftime") else user["created_at"],
            updated_at=user["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(user["updated_at"], "strftime") else user["updated_at"]
        )
    
    except pymysql.MySQLError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库操作失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()

@router.post("/login", response_model=LoginResponse, summary="用户登录", description="用户登录获取访问令牌")
def login_user(
    payload: UserLogin,
    db: pymysql.connections.Connection = Depends(get_db)
):
    cursor = None
    try:
        cursor = db.cursor()
        
        # 查询用户
        cursor.execute(
            "SELECT id, username, email, phone, real_name AS full_name, role, password_hash AS password, created_at, updated_at FROM users WHERE username = %s",
            (payload.username,)
        )
        user = cursor.fetchone()
        
        # 验证用户是否存在且密码正确
        if not user or not verify_password(payload.password, user["password"]):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": user["id"], "username": user["username"], "role": user["role"]})
        
        return LoginResponse(
            access_token=access_token,
            user=UserOut(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                phone=user["phone"],
                full_name=user["full_name"],
                role=user["role"],
                created_at=user["created_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(user["created_at"], "strftime") else user["created_at"],
                updated_at=user["updated_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(user["updated_at"], "strftime") else user["updated_at"]
            )
        )
    
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"数据库操作失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()


auth_router = APIRouter()


ACCESS_EXPIRES_SECONDS = 7200
REFRESH_EXPIRES_DAYS = 30


def _issue_tokens(current_user: dict[str, Any]) -> dict[str, Any]:
    token_payload = {
        "sub": str(current_user["id"]),
        "username": current_user["username"],
        "role": current_user.get("platformRole", "user"),
    }
    return {
        "accessToken": create_access_token(
            data=token_payload,
            expires_delta=timedelta(seconds=ACCESS_EXPIRES_SECONDS),
        ),
        "refreshToken": create_access_token(
            data={**token_payload, "tokenType": "refresh"},
            expires_delta=timedelta(days=REFRESH_EXPIRES_DAYS),
        ),
        "expiresIn": ACCESS_EXPIRES_SECONDS,
    }


def _mock_current_user(username: str | None = None) -> dict[str, Any]:
    current_user = _mock.current_user()
    if username:
        current_user["username"] = username
        current_user["name"] = current_user.get("name") or username
    return current_user


def _db_user_to_current_user(user: dict[str, Any]) -> dict[str, Any]:
    user_id = str(user.get("user_code") or f"u_{user['id']}")
    role = user.get("role") or "user"
    return {
        "id": user_id,
        "username": user.get("username") or user_id,
        "name": user.get("real_name") or user.get("username") or user_id,
        "nickname": user.get("nickname") or user.get("real_name") or user.get("username") or user_id,
        "avatar": user.get("avatar_url"),
        "platformRole": role,
        "department": user.get("department"),
        "position": user.get("position"),
        "permissions": _permissions_for_role(role),
    }


def _permissions_for_role(role: str) -> list[str]:
    if role in {"admin", "super_admin"}:
        return _mock.current_user()["permissions"]
    return ["project:read", "task:create", "task:update"]


def _find_login_user(account: str, password: str) -> dict[str, Any] | None:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                id, username, nickname, real_name, email, phone, avatar_url,
                role, department, position, status, password_hash
            FROM users
            WHERE username = %s OR email = %s
            LIMIT 1
            """,
            (account, account),
        )
        user = cursor.fetchone()
        if not user or not verify_password(password, user["password_hash"]):
            return None
        return user
    except pymysql.MySQLError:
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def _register_db_user(payload: dict[str, Any]) -> str | None:
    username = payload.get("username") or payload.get("account")
    password = payload.get("password")
    if not username or not password:
        return None

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s LIMIT 1", (username, payload.get("email")))
        existing = cursor.fetchone()
        if existing:
            return str(existing["id"])

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO users
                (username, nickname, password_hash, real_name, email, phone, role, department, status, created_at, updated_at)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                username,
                payload.get("nickname") or payload.get("name") or username,
                get_password_hash(password),
                payload.get("name") or payload.get("realName") or username,
                payload.get("email") or f"{username}@example.local",
                payload.get("phone"),
                "user",
                payload.get("department"),
                "pending",
                now,
                now,
            ),
        )
        user_id = str(cursor.lastrowid)
        conn.commit()
        return user_id
    except pymysql.MySQLError:
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# TODO: 接入真实会话表后，记录登录设备、refresh token 哈希和最后活跃时间。
@auth_router.post("/login", summary="账号密码登录")
def auth_login(payload: dict[str, Any] = Body(...)):
    username = payload.get("username") or payload.get("account") or "zhanggong"
    password = payload.get("password") or ""
    db_user = _find_login_user(username, password)
    current_user = _db_user_to_current_user(db_user) if db_user else _mock_current_user(username)
    return _mock.api_response({**_issue_tokens(current_user), "currentUser": current_user})


# TODO: 映射 RegisterRequest 到 users 表，校验邮箱唯一和 confirmPassword，并返回 pending/active 注册结果。
@auth_router.post("/register", summary="注册")
def auth_register(payload: dict[str, Any] = Body(...)):
    password = payload.get("password")
    confirm_password = payload.get("confirmPassword")
    if confirm_password is not None and password != confirm_password:
        raise HTTPException(status_code=400, detail={"code": "PASSWORD_CONFIRM_MISMATCH", "message": "两次输入密码不一致"})

    db_user_id = _register_db_user(payload)
    return _mock.api_response(
        {
            "userId": f"u_{db_user_id}" if db_user_id else _mock.make_id("u"),
            "status": "pending",
            "profile": {
                "account": payload.get("account") or payload.get("username"),
                "name": payload.get("name"),
                "email": payload.get("email"),
                "department": payload.get("department"),
            },
        }
    )


# TODO: 从 token 解析当前用户，查询最新资料、角色和权限，不再返回静态 CurrentUser。
@auth_router.get("/me", summary="获取当前用户")
def get_current_user(authorization: str | None = Header(default=None)):
    if authorization and authorization.lower().startswith("bearer "):
        payload = decode_access_token(authorization.split(" ", 1)[1])
        if payload:
            current_user = _mock_current_user(payload.get("username"))
            current_user["id"] = payload.get("sub", current_user["id"])
            current_user["platformRole"] = payload.get("role", current_user["platformRole"])
            return _mock.api_response(current_user)
    return _mock.api_response(_mock.current_user())


# TODO: 校验 refreshToken 有效期和撤销状态，签发新 accessToken 并按策略轮换 refreshToken。
@auth_router.post("/refresh", summary="刷新会话")
def refresh_session(payload: dict[str, Any] | None = Body(default=None)):
    token = (payload or {}).get("refreshToken")
    decoded = decode_access_token(token) if token else None
    current_user = _mock_current_user((decoded or {}).get("username"))
    if decoded and decoded.get("sub"):
        current_user["id"] = decoded["sub"]
    return _mock.api_response(_issue_tokens(current_user))


# TODO: 撤销当前 refreshToken/会话，记录退出时间，保证重复调用幂等。
@auth_router.post("/logout", summary="退出登录")
def logout(payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"success": True, "revoked": bool((payload or {}).get("refreshToken")), "loggedOutAt": _mock.now_iso()})


# TODO: 从系统配置读取启用的第三方登录提供商，返回授权方式、图标和是否可用。
@auth_router.get("/providers", summary="第三方登录方式")
def list_auth_providers():
    return _mock.api_response(
        [
            {"id": "wecom", "name": "WeCom", "enabled": True},
            {"id": "dingtalk", "name": "DingTalk", "enabled": False},
        ]
    )


# TODO: 根据 provider 创建第三方登录 state，生成二维码/跳转地址并保存短期登录会话。
@auth_router.post("/social/start", summary="发起扫码/外部登录")
def start_social_login(payload: dict[str, Any] = Body(default_factory=dict)):
    provider = payload.get("provider", "wecom")
    return _mock.api_response(
        {
            "provider": provider,
            "state": _mock.make_id("social"),
            "qrCodeUrl": f"https://example.com/auth/{provider}/qr",
            "expiresIn": 300,
        }
    )


# TODO: 校验第三方回调 state/code，绑定或创建本地用户，并签发系统 token。
@auth_router.post("/social/confirm", summary="第三方登录确认")
def confirm_social_login(payload: dict[str, Any] = Body(default_factory=dict)):
    return _mock.api_response(
        {
            "accessToken": "mock_social_access_token",
            "refreshToken": "mock_social_refresh_token",
            "expiresIn": 7200,
            "currentUser": _mock.current_user(),
            "state": payload.get("state"),
        }
    )
