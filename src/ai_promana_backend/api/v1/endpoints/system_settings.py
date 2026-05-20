# TODO: 个人/系统设置接口当前为首版联调实现，后续接入 PyMySQL 配置存储、安全策略和会话管理。
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ai_promana_backend.api.v1.endpoints import _mock
from ai_promana_backend.schemas.request_bodies import (
    ChangePasswordRequest,
    NotificationChannelsUpdateRequest,
    SettingsResetRequest,
    SystemConfigResetRequest,
    SystemConfigUpdateRequest,
    UserSettingsUpdateRequest,
    body_to_dict,
)


settings_router = APIRouter()
admin_router = APIRouter()


DEFAULT_PROFILE: dict[str, Any] = {
    "name": "Zhang Gong",
    "department": "R&D Center",
    "departmentId": "dept_rd",
}

DEFAULT_NOTIFICATIONS: dict[str, Any] = {
    "taskStatus": True,
    "logFeedback": True,
    "reportSubscription": False,
}

DEFAULT_AI_PREFS: dict[str, Any] = {
    "autoSummary": True,
    "scheduling": True,
    "riskAlert": False,
}

DEFAULT_SETTINGS: dict[str, Any] = {
    "siteNotice": True,
    "wecomPush": True,
    "auditTrail": True,
}


@settings_router.get("/me", summary="设置页首屏数据")
def get_my_settings():
    return _mock.api_response(_user_settings_payload())


@settings_router.put("/me", summary="保存个人设置")
def update_my_settings(payload: UserSettingsUpdateRequest):
    return _mock.api_response(_save_user_settings_payload(body_to_dict(payload)))


@settings_router.post("/reset", summary="恢复默认设置")
def reset_my_settings(payload: SettingsResetRequest | None = None):
    return _mock.api_response(_reset_user_settings_payload(body_to_dict(payload)))


@settings_router.get("/defaults", summary="个人设置默认值")
def get_my_settings_defaults():
    return _mock.api_response(_settings_defaults())


@settings_router.get("/search", summary="搜索设置项")
def search_my_settings(
    keyword: str | None = Query(default=None),
    tab: str | None = Query(default="all"),
):
    return _mock.api_response(
        {
            "keyword": _plain_query_value(keyword, "") or "",
            "tab": _plain_query_value(tab, "all") or "all",
            "results": _search_settings_items(_plain_query_value(keyword, "")),
        }
    )


@settings_router.post("/change-password", summary="修改密码")
def change_password(payload: ChangePasswordRequest):
    return _mock.api_response(_change_password_payload(body_to_dict(payload)))


@admin_router.get("/system-config", summary="系统配置读取")
def get_system_config(
    keyword: str | None = Query(default=None),
    sectionKey: str | None = Query(default=None),
):
    return _mock.api_response(_system_config_payload(keyword, sectionKey))


@admin_router.put("/system-config", summary="系统配置保存")
def update_system_config(payload: SystemConfigUpdateRequest):
    body = body_to_dict(payload)
    config = _extract_system_config(body)
    version = int(body.get("version", 3)) + 1
    return _mock.api_response(
        {
            "config": config,
            "settings": config,
            "sections": _system_sections(config),
            "changedKeys": _changed_system_config_keys(config),
            "version": version,
            "updatedAt": _mock.now_iso(),
        }
    )


@admin_router.post("/system-config/reset", summary="恢复默认配置")
def reset_system_config(payload: SystemConfigResetRequest | None = None):
    body = body_to_dict(payload)
    keys = body.get("keys") or []
    config = DEFAULT_SETTINGS.copy()
    if keys:
        current = _extract_system_config(body)
        config = {**current, **{key: DEFAULT_SETTINGS[key] for key in keys if key in DEFAULT_SETTINGS}}
    version = int(body.get("version", 3)) + 1
    return _mock.api_response(
        {
            "config": config,
            "settings": config,
            "sections": _system_sections(config),
            "version": version,
            "resetAt": _mock.now_iso(),
            "updatedAt": _mock.now_iso(),
        }
    )


@admin_router.get("/system-config/defaults", summary="系统默认配置")
def get_system_config_defaults():
    return _mock.api_response(
        {
            "config": DEFAULT_SETTINGS,
            "settings": DEFAULT_SETTINGS,
            "sections": _system_sections(DEFAULT_SETTINGS),
            "version": 1,
        }
    )


@admin_router.get("/system-config/history", summary="系统配置历史")
def list_system_config_history(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    page = _plain_query_value(page, 1) or 1
    page_size = _plain_query_value(pageSize, 20) or 20
    items = [
        {
            "historyId": "cfg_hist_001",
            "operator": "Zhang Gong",
            "action": "保存系统配置",
            "changedKeys": ["siteNotice"],
            "occurredAt": _mock.now_iso(),
            "version": 5,
        },
        {
            "historyId": "cfg_hist_002",
            "operator": "Zhang Gong",
            "action": "恢复默认配置",
            "changedKeys": ["wecomPush", "auditTrail"],
            "occurredAt": "2026-05-11T16:25:00+08:00",
            "version": 4,
        },
    ]
    data = _mock.paged(items, int(page), int(page_size))
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    return _mock.api_response(data)


@admin_router.get("/notification-channels", summary="通知通道配置")
def get_notification_channels():
    return _mock.api_response(
        [
            {
                "channel": "in_app",
                "name": "站内通知",
                "enabled": True,
                "status": "healthy",
                "description": "用于系统消息、任务提醒和 AI 建议。",
            },
            {
                "channel": "enterprise_wechat",
                "name": "企业微信",
                "enabled": False,
                "status": "not_configured",
                "description": "待配置机器人或企业应用凭证。",
            },
        ]
    )


@admin_router.put("/notification-channels", summary="保存通知通道配置")
def update_notification_channels(payload: NotificationChannelsUpdateRequest):
    body = body_to_dict(payload)
    channels = body.get("channels") or []
    if isinstance(channels, dict):
        channels = list(channels.values())
    channels = [channel for channel in channels if channel.get("channel") != "email"]
    return _mock.api_response(
        {
            "channels": channels,
            "updatedAt": _mock.now_iso(),
            "version": int(body.get("version", 1)) + 1 if isinstance(body, dict) else 2,
        }
    )


def _system_config_payload(keyword: Any = None, section_key: Any = None) -> dict[str, Any]:
    config = DEFAULT_SETTINGS.copy()
    sections = _system_sections(config)
    keyword = _plain_query_value(keyword)
    section_key = _plain_query_value(section_key)
    if section_key and section_key != "all":
        sections = [section for section in sections if section["key"] == section_key]
    if keyword:
        lowered = str(keyword).lower()
        filtered_sections = []
        for section in sections:
            items = [
                item
                for item in section["items"]
                if lowered in item["label"].lower()
                or lowered in item.get("description", "").lower()
                or lowered in section["title"].lower()
            ]
            if items:
                filtered_sections.append({**section, "items": items})
        sections = filtered_sections
    return {
        "currentUser": _mock.current_user(),
        "sections": sections,
        "config": config,
        "settings": config,
        "groups": [
            {
                "key": section["key"],
                "title": section["title"],
                "fields": [item["key"] for item in section["items"]],
            }
            for section in sections
        ],
        "defaults": DEFAULT_SETTINGS,
        "version": 4,
        "enabledCount": len([value for value in config.values() if value]),
        "updatedAt": _mock.now_iso(),
    }


def _system_sections(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "key": "notice",
            "title": "通知通道",
            "caption": "站内 / 企微",
            "items": [
                {
                    "key": "siteNotice",
                    "label": "站内通知",
                    "description": "系统消息、任务提醒和 AI 建议默认通过站内通知触达。",
                    "value": bool(config.get("siteNotice", True)),
                    "disabled": False,
                    "requiresRestart": False,
                },
                {
                    "key": "wecomPush",
                    "label": "企业微信推送",
                    "description": "任务阻塞、评论、报表订阅可同步推送到企业微信。",
                    "value": bool(config.get("wecomPush", True)),
                    "disabled": False,
                    "requiresRestart": False,
                },
            ],
        },
        {
            "key": "security",
            "title": "安全策略",
            "caption": "审计",
            "items": [
                {
                    "key": "auditTrail",
                    "label": "敏感操作审计",
                    "description": "删除、归档、角色变更和配置保存必须记录审计日志。",
                    "value": bool(config.get("auditTrail", True)),
                    "disabled": False,
                    "requiresRestart": False,
                },
            ],
        },
    ]


def _extract_system_config(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("config") or payload.get("settings") or payload
    return {
        key: bool(raw.get(key, default))
        for key, default in DEFAULT_SETTINGS.items()
    }


def _changed_system_config_keys(config: dict[str, Any]) -> list[str]:
    return [key for key, default in DEFAULT_SETTINGS.items() if bool(config.get(key)) != bool(default)]


def _user_settings_payload() -> dict[str, Any]:
    current_user = _mock.current_user()
    profile = {
        **DEFAULT_PROFILE,
        "name": current_user.get("name") or DEFAULT_PROFILE["name"],
        "department": current_user.get("department") or DEFAULT_PROFILE["department"],
    }
    sessions = [
        {
            "sessionId": "sess_001",
            "id": "sess_001",
            "deviceName": "Chrome / Windows",
            "device": "Chrome / Windows",
            "ip": "192.168.*.*",
            "location": "上海",
            "lastActiveAt": _mock.now_iso(),
            "current": True,
        },
        {
            "sessionId": "sess_002",
            "id": "sess_002",
            "deviceName": "Edge / Windows",
            "device": "Edge / Windows",
            "ip": "10.0.*.*",
            "location": "杭州",
            "lastActiveAt": "2026-05-12T18:30:00+08:00",
            "current": False,
        },
        {
            "sessionId": "sess_003",
            "id": "sess_003",
            "deviceName": "Mobile Safari / iOS",
            "device": "Mobile Safari / iOS",
            "ip": "172.16.*.*",
            "location": "广州",
            "lastActiveAt": "2026-05-10T09:20:00+08:00",
            "current": False,
        },
    ]
    notifications = DEFAULT_NOTIFICATIONS.copy()
    ai_prefs = DEFAULT_AI_PREFS.copy()
    return {
        "userId": current_user["id"],
        "profile": profile,
        "notifications": notifications,
        "aiPrefs": ai_prefs,
        "security": {
            "lastPasswordChangedAt": "2026-03-12T09:00:00+08:00",
            "activeSessionCount": len(sessions),
            "currentSessionId": next((item["sessionId"] for item in sessions if item["current"]), None),
        },
        "sessions": sessions,
        "securityHints": [
            {"id": "hint_001", "level": "info", "message": "最近一次密码修改时间为 2026-03-12。"},
            {"id": "hint_002", "level": "warning", "message": "建议定期检查非当前设备会话。"},
        ],
        "defaults": _settings_defaults(),
        "updatedAt": "2026-05-11T13:20:00+08:00",
        "version": 3,
    }


def _save_user_settings_payload(payload: dict[str, Any]) -> dict[str, Any]:
    profile = payload.get("profile", {}) or {}
    if not isinstance(profile, dict):
        profile = {}
    profile = {key: value for key, value in profile.items() if key not in {"email", "phone"}}
    return {
        "userId": _mock.current_user()["id"],
        "profile": {**DEFAULT_PROFILE, **profile},
        "notifications": {**DEFAULT_NOTIFICATIONS, **payload.get("notifications", {})},
        "aiPrefs": {**DEFAULT_AI_PREFS, **payload.get("aiPrefs", {})},
        "updatedAt": _mock.now_iso(),
        "version": int(payload.get("version", 1)) + 1,
    }


def _reset_user_settings_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sections = payload.get("sections") or ["notifications", "aiPrefs"]
    current = _user_settings_payload()
    if "notifications" in sections:
        current["notifications"] = {key: False for key in DEFAULT_NOTIFICATIONS}
    if "aiPrefs" in sections:
        current["aiPrefs"] = {key: False for key in DEFAULT_AI_PREFS}
    current["version"] += 1
    current["resetAt"] = _mock.now_iso()
    return current


def _settings_defaults() -> dict[str, Any]:
    return {
        "profile": DEFAULT_PROFILE,
        "notifications": DEFAULT_NOTIFICATIONS,
        "aiPrefs": DEFAULT_AI_PREFS,
        "security": {"revokeOtherSessions": True},
    }


def _change_password_payload(payload: dict[str, Any]) -> dict[str, Any]:
    new_password = payload.get("newPassword")
    confirm_password = payload.get("confirmPassword")
    if not payload.get("oldPassword"):
        raise HTTPException(status_code=400, detail={"code": "OLD_PASSWORD_REQUIRED", "message": "请输入原密码"})
    if not new_password or len(str(new_password)) < 8:
        raise HTTPException(status_code=400, detail={"code": "PASSWORD_POLICY_INVALID", "message": "新密码至少 8 位"})
    if confirm_password is not None and new_password != confirm_password:
        raise HTTPException(status_code=400, detail={"code": "PASSWORD_CONFIRM_MISMATCH", "message": "两次密码不一致"})
    revoked_count = 2 if payload.get("revokeOtherSessions", True) else 0
    return {
        "changed": True,
        "changedAt": _mock.now_iso(),
        "revokedSessionCount": revoked_count,
        "needRelogin": bool(payload.get("revokeOtherSessions", True)),
    }


def _search_settings_items(keyword: str | None) -> list[dict[str, Any]]:
    items = [
        {"tab": "profile", "label": "个人资料", "description": "姓名、部门和头像"},
        {"tab": "notification", "label": "任务状态变更", "description": "任务完成、阻塞和评审提醒"},
        {"tab": "notification", "label": "报表订阅", "description": "项目周报和全局报表订阅通知"},
        {"tab": "security", "label": "修改密码", "description": "账户密码和设备会话管理"},
        {"tab": "ai", "label": "AI 自动总结", "description": "日报、任务和风险的智能总结偏好"},
    ]
    if not keyword:
        return items
    lowered = str(keyword).lower()
    return [item for item in items if lowered in item["label"].lower() or lowered in item["description"].lower()]


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
