# TODO: /api/auth/* 当前为首版契约接口，后续需要与旧 /api/v1/users/* 统一认证模型、token 刷新和权限依赖。
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
import pymysql
from datetime import timedelta
from ai_promana_backend.database import get_db
from ai_promana_backend.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from ai_promana_backend.schemas.user import (
    UserLogin,
    UserOut,
    LoginResponse,
)
from ai_promana_backend.schemas.request_bodies import (
    RefreshSessionRequest,
    body_to_dict,
)
from ai_promana_backend.api.v1.endpoints import _mock

router = APIRouter()

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
    current_user["accountStatus"] = current_user.get("accountStatus", "active")
    return current_user


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
def refresh_session(payload: RefreshSessionRequest | None = None):
    body = body_to_dict(payload)
    token = body.get("refreshToken")
    decoded = decode_access_token(token) if token else None
    current_user = _mock_current_user((decoded or {}).get("username"))
    if decoded and decoded.get("sub"):
        current_user["id"] = decoded["sub"]
    return _mock.api_response(_issue_tokens(current_user))
