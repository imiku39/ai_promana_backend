# TODO: 个人/系统设置接口当前为首版联调实现，后续接入配置存储、安全策略和会话管理。
from typing import Any

from fastapi import APIRouter, Body

from ai_promana_backend.api.v1.endpoints import _mock


settings_router = APIRouter()
admin_router = APIRouter()
ai_router = APIRouter()


DEFAULT_SETTINGS: dict[str, Any] = {
    "siteNotice": True,
    "wecomPush": True,
    "emailSubscription": False,
    "auditTrail": True,
    "maskSensitiveData": True,
}


# TODO: 查询个人资料、通知偏好、活跃会话和安全提示，敏感字段需脱敏。
@settings_router.get("/me", summary="设置页首屏数据")
def get_my_settings():
    return _mock.api_response(
        {
            "profile": {
                "name": _mock.current_user()["name"],
                "department": _mock.current_user()["department"],
                "email": "zhang@example.com",
                "phone": "13800000000",
            },
            "notifications": {
                "taskStatus": True,
                "logFeedback": True,
                "reportSubscription": "weekly",
            },
            "sessions": [
                {
                    "id": "session_001",
                    "device": "Windows Edge",
                    "ip": "127.0.0.1",
                    "lastActiveAt": _mock.now_iso(),
                    "current": True,
                }
            ],
            "securityHints": [
                {"id": "hint_001", "level": "info", "message": "Password was updated recently."}
            ],
            "aiSuggestions": _mock.ai_suggestions("settings"),
        }
    )


# TODO: 保存个人资料和偏好设置，校验邮箱/手机号格式并同步用户基础信息表。
@settings_router.put("/me", summary="保存个人设置")
def update_my_settings(payload: dict[str, Any] = Body(...)):
    payload["updatedAt"] = _mock.now_iso()
    return _mock.api_response(payload)


# TODO: 恢复当前用户设置为系统默认值，但保留用户身份、邮箱和安全会话信息。
@settings_router.post("/reset", summary="恢复默认设置")
def reset_my_settings():
    return _mock.api_response({"profile": {}, "notifications": DEFAULT_SETTINGS, "resetAt": _mock.now_iso()})


# TODO: 校验旧密码、密码强度和确认密码，更新密码哈希并可选择踢出其他会话。
@settings_router.post("/change-password", summary="修改密码")
def change_password(payload: dict[str, Any] = Body(...)):
    return _mock.api_response({"changed": True, "changedAt": _mock.now_iso(), "needRelogin": True})


# TODO: 从会话/refresh token 表查询当前用户设备列表，标记当前会话和异常登录提示。
@settings_router.get("/sessions", summary="设备会话列表")
def list_sessions():
    return _mock.api_response(
        [
            {
                "id": "session_001",
                "device": "Windows Edge",
                "ip": "127.0.0.1",
                "lastActiveAt": _mock.now_iso(),
                "current": True,
            },
            {
                "id": "session_002",
                "device": "Mobile Safari",
                "ip": "10.0.0.8",
                "lastActiveAt": "2026-05-12T18:30:00+08:00",
                "current": False,
            },
        ]
    )


# TODO: 下线指定设备会话，禁止删除当前会话或按产品规则要求二次确认。
@settings_router.delete("/sessions/{sessionId}", summary="下线某设备")
def revoke_session(sessionId: str):
    return _mock.api_response({"sessionId": sessionId, "revoked": True, "revokedAt": _mock.now_iso()})


# TODO: 读取系统配置、分组元数据和默认值，敏感配置只返回脱敏或布尔状态。
@admin_router.get("/system-config", summary="系统配置读取")
def get_system_config():
    return _mock.api_response(
        {
            "currentUser": _mock.current_user(),
            "settings": DEFAULT_SETTINGS,
            "groups": [
                {
                    "key": "notification",
                    "title": "Notification",
                    "fields": ["siteNotice", "wecomPush", "emailSubscription"],
                },
                {
                    "key": "security",
                    "title": "Security",
                    "fields": ["auditTrail", "maskSensitiveData"],
                },
            ],
            "defaults": DEFAULT_SETTINGS,
        }
    )


# TODO: 校验系统配置字段，保存配置版本，触发缓存刷新并写入配置变更审计。
@admin_router.put("/system-config", summary="系统配置保存")
def update_system_config(payload: dict[str, Any] = Body(...)):
    payload["updatedAt"] = _mock.now_iso()
    return _mock.api_response(payload)


# TODO: 将系统配置恢复为默认值，生成新配置版本并记录重置原因和操作者。
@admin_router.post("/system-config/reset", summary="恢复默认配置")
def reset_system_config():
    return _mock.api_response({"settings": DEFAULT_SETTINGS, "resetAt": _mock.now_iso()})


# TODO: 根据用户设置、通知习惯和安全提示生成 AI 偏好优化建议。
@ai_router.get("/settings-suggestions", summary="AI 偏好建议")
def get_ai_settings_suggestions():
    return _mock.api_response({"suggestions": _mock.ai_suggestions("settings")})


# TODO: 采纳设置建议时更新对应偏好字段，并保存 suggestionId 与变更前后值。
@ai_router.post("/settings-suggestions/{suggestionId}/apply", summary="采纳 AI 偏好建议")
def apply_ai_settings_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"suggestionId": suggestionId, "applied": True, "payload": payload or {}})
