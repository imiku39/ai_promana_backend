# TODO: /api/auth/* 当前已切到真实 JWT 登录主链路，后续继续补齐注册审核、会话撤销和第三方登录落库。
from datetime import date, datetime, timedelta
from typing import Any

import pymysql
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from ai_promana_backend.api.v1.endpoints import _mock
from ai_promana_backend.config import settings
from ai_promana_backend.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_password_hash,
    require_access_token,
    verify_password,
)
from ai_promana_backend.database import get_db
from ai_promana_backend.schemas.user import AuthLoginRequest, RefreshTokenRequest, UserCreate

auth_router = APIRouter()
protected_auth_router = APIRouter()

ROLE_LABELS = {
    "super_admin": "超级管理员",
    "admin": "管理员",
    "pm": "项目负责人",
    "developer": "研发",
    "qa": "测试",
    "product": "产品",
    "collaborator": "协作者",
    "member": "成员",
    "user": "普通用户",
}

ROLE_PERMISSIONS = {
    "super_admin": [
        "admin:access",
        "project:create",
        "project:read",
        "project:update",
        "task:create",
        "task:update",
        "report:export",
        "system:settings:read",
        "system:settings:update",
    ],
    "admin": [
        "admin:access",
        "project:create",
        "project:read",
        "project:update",
        "task:create",
        "task:update",
        "report:export",
        "system:settings:read",
    ],
    "pm": ["project:read", "project:update", "task:create", "task:update", "report:export"],
    "developer": ["project:read", "task:create", "task:update"],
    "qa": ["project:read", "task:update", "report:export"],
    "product": ["project:read", "task:create"],
    "collaborator": ["project:read"],
    "member": ["project:read", "task:update"],
    "user": ["project:read"],
}

USER_COLUMNS = """
id, username, nickname, password_hash, real_name, email, phone, avatar_url,
role, department, position, status, join_date, last_login_time, created_at, updated_at
"""


def _role_label(role: str | None) -> str:
    safe_role = role or "user"
    return ROLE_LABELS.get(safe_role, safe_role)


def _role_permissions(role: str | None) -> list[str]:
    safe_role = role or "user"
    return ROLE_PERMISSIONS.get(safe_role, ROLE_PERMISSIONS["user"])


def _redirect_path_for_role(role: str | None) -> str:
    return "/dashboard"


def _format_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return str(value)


def _format_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _build_auth_user(user: dict[str, Any]) -> dict[str, Any]:
    display_name = user.get("real_name") or user.get("nickname") or user["username"]
    return {
        "id": str(user["id"]),
        "username": user["username"],
        "name": display_name,
        "nickname": user.get("nickname") or display_name,
        "avatar": user.get("avatar_url"),
        "department": user.get("department"),
        "position": user.get("position"),
        "role": user.get("role", "user"),
        "roleName": _role_label(user.get("role")),
        "accountStatus": user.get("status", "active"),
        "joinDate": _format_date(user.get("join_date")),
        "lastLoginAt": _format_datetime(user.get("last_login_time")),
    }


def _build_auth_payload(user: dict[str, Any], remember_me: bool = False) -> dict[str, Any]:
    access_expires = timedelta(days=7) if remember_me else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(days=30) if remember_me else timedelta(days=7)
    claims = {
        "sub": user["id"],
        "username": user["username"],
        "role": user.get("role", "user"),
        "remember_me": remember_me,
    }
    auth_user = _build_auth_user(user)
    return {
        "accessToken": create_access_token(data=claims, expires_delta=access_expires),
        "refreshToken": create_refresh_token(data=claims, expires_delta=refresh_expires),
        "expiresIn": int(access_expires.total_seconds()),
        "tokenType": "Bearer",
        "user": auth_user,
        "currentUser": auth_user,
        "permissions": _role_permissions(user.get("role")),
        "redirectPath": _redirect_path_for_role(user.get("role")),
    }


def _raise_auth_error(status_code: int, code: str, message: str) -> None:
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _ensure_user_can_login(user: dict[str, Any] | None) -> dict[str, Any]:
    if user is None:
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "AUTH_BAD_CREDENTIALS", "账号或密码错误")

    account_status = user.get("status") or "active"
    if account_status == "disabled":
        _raise_auth_error(status.HTTP_403_FORBIDDEN, "AUTH_ACCOUNT_DISABLED", "账号已禁用，请联系管理员")
    if account_status == "pending":
        _raise_auth_error(status.HTTP_403_FORBIDDEN, "AUTH_ACCOUNT_PENDING", "账号待审核，暂时无法登录")
    return user


def _fetch_user_by_id(cursor: Any, user_id: int) -> dict[str, Any] | None:
    cursor.execute(f"SELECT {USER_COLUMNS} FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()


def _fetch_user_by_login(cursor: Any, login_name: str) -> dict[str, Any] | None:
    cursor.execute(
        f"SELECT {USER_COLUMNS} FROM users WHERE username = %s OR email = %s OR phone = %s LIMIT 1",
        (login_name, login_name, login_name),
    )
    return cursor.fetchone()


def _touch_last_login(cursor: Any, user_id: int) -> None:
    cursor.execute("UPDATE users SET last_login_time = %s WHERE id = %s", (datetime.now(), user_id))


def _create_user_record(payload: UserCreate, cursor: Any, db: pymysql.connections.Connection) -> dict[str, Any]:
    if not payload.email:
        raise HTTPException(status_code=400, detail="邮箱不能为空")

    cursor.execute("SELECT id FROM users WHERE username = %s", (payload.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="用户名已存在")

    cursor.execute("SELECT id FROM users WHERE email = %s", (payload.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    if payload.phone:
        cursor.execute("SELECT id FROM users WHERE phone = %s", (payload.phone,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="手机号已被注册")

    now = datetime.now()
    hashed_password = get_password_hash(payload.password)
    display_name = payload.full_name or payload.username

    cursor.execute(
        """
        INSERT INTO users (
            username, nickname, password_hash, real_name, email, phone, avatar_url,
            role, department, position, status, join_date, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            payload.username,
            display_name,
            hashed_password,
            payload.full_name,
            payload.email,
            payload.phone,
            None,
            "user",
            None,
            None,
            "active",
            now.date(),
            now,
            now,
        ),
    )
    user_id = cursor.lastrowid
    db.commit()
    user = _fetch_user_by_id(cursor, user_id)
    if user is None:
        raise HTTPException(status_code=500, detail="用户创建成功但读取失败")
    return user


def _login_request_from_parameters(
    username: str = Query(..., description="用户名/邮箱/手机号"),
    password: str = Query(..., description="密码"),
    rememberMe: bool = Query(False, description="是否记住我"),
    loginType: str = Query("password", description="登录方式"),
    deviceId: str | None = Query(None, description="设备标识"),
    clientType: str | None = Query("web", description="客户端类型"),
) -> AuthLoginRequest:
    return AuthLoginRequest(
        username=username,
        password=password,
        rememberMe=rememberMe,
        loginType=loginType,
        deviceId=deviceId,
        clientType=clientType,
    )


@auth_router.post("/login", summary="账号密码登录")
def auth_login(
    payload: AuthLoginRequest = Depends(_login_request_from_parameters),
    db: pymysql.connections.Connection = Depends(get_db),
):
    cursor = None
    try:
        cursor = db.cursor()
        user = _ensure_user_can_login(_fetch_user_by_login(cursor, payload.username))
        if not verify_password(payload.password, user["password_hash"]):
            _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "AUTH_BAD_CREDENTIALS", "账号或密码错误")

        _touch_last_login(cursor, user["id"])
        db.commit()
        return _mock.api_response(_build_auth_payload(user, remember_me=payload.rememberMe))
    except pymysql.MySQLError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={"code": "COMMON_SERVER_ERROR", "message": f"数据库操作失败：{str(e)}"})
    finally:
        if cursor:
            cursor.close()


# TODO: 注册页契约确认后，补充 confirmPassword、邀请注册和审核流，并区分 active/pending 两种注册结果。
@auth_router.post("/register", summary="注册")
def auth_register(
    payload: UserCreate,
    db: pymysql.connections.Connection = Depends(get_db),
):
    cursor = None
    try:
        cursor = db.cursor()
        user = _create_user_record(payload, cursor, db)
        auth_user = _build_auth_user(user)
        return _mock.api_response(
            {
                "userId": auth_user["id"],
                "status": auth_user["accountStatus"],
                "profile": {
                    "name": auth_user["name"],
                    "department": auth_user["department"],
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                },
            }
        )
    except pymysql.MySQLError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={"code": "COMMON_SERVER_ERROR", "message": f"数据库操作失败：{str(e)}"})
    finally:
        if cursor:
            cursor.close()


@protected_auth_router.get("/me", summary="获取当前用户")
def get_current_user(
    token_payload: dict[str, Any] = Depends(require_access_token),
    db: pymysql.connections.Connection = Depends(get_db),
):
    cursor = None
    try:
        cursor = db.cursor()
        user = _fetch_user_by_id(cursor, int(token_payload["sub"]))
        if user is None:
            _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "AUTH_TOKEN_INVALID", "登录状态已失效")
        _ensure_user_can_login(user)
        auth_user = _build_auth_user(user)
        return _mock.api_response(
            {
                "id": auth_user["id"],
                "username": auth_user["username"],
                "name": auth_user["name"],
                "avatar": auth_user["avatar"],
                "department": auth_user["department"],
                "role": auth_user["role"],
                "roleName": auth_user["roleName"],
                "nickname": auth_user["nickname"],
                "position": auth_user["position"],
                "accountStatus": auth_user["accountStatus"],
                "permissions": _role_permissions(user.get("role")),
            }
        )
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail={"code": "COMMON_SERVER_ERROR", "message": f"数据库操作失败：{str(e)}"})
    finally:
        if cursor:
            cursor.close()


@auth_router.post("/refresh", summary="刷新会话")
def refresh_session(
    payload: RefreshTokenRequest,
    db: pymysql.connections.Connection = Depends(get_db),
):
    token_payload = decode_access_token(payload.refreshToken)
    if token_payload is None:
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "AUTH_TOKEN_INVALID", "refreshToken 无效或已过期")
    if token_payload.get("token_type") != "refresh":
        _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "AUTH_TOKEN_INVALID", "refreshToken 类型错误")

    cursor = None
    try:
        cursor = db.cursor()
        user = _fetch_user_by_id(cursor, int(token_payload["sub"]))
        if user is None:
            _raise_auth_error(status.HTTP_401_UNAUTHORIZED, "AUTH_TOKEN_INVALID", "登录状态已失效")
        _ensure_user_can_login(user)
        remember_me = bool(token_payload.get("remember_me", False))
        auth_payload = _build_auth_payload(user, remember_me=remember_me)
        return _mock.api_response(
            {
                "accessToken": auth_payload["accessToken"],
                "refreshToken": auth_payload["refreshToken"],
                "expiresIn": auth_payload["expiresIn"],
                "tokenType": auth_payload["tokenType"],
            }
        )
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail={"code": "COMMON_SERVER_ERROR", "message": f"数据库操作失败：{str(e)}"})
    finally:
        if cursor:
            cursor.close()


@protected_auth_router.post("/logout", summary="退出登录")
def logout(
    token_payload: dict[str, Any] = Depends(require_access_token),
    payload: dict[str, Any] | None = Body(default=None),
):
    return _mock.api_response(True)


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
