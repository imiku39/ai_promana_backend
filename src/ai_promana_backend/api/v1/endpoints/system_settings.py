# TODO: 个人/系统设置接口当前为首版联调实现，后续接入 PyMySQL 配置存储、安全策略和会话管理。
from typing import Any

from fastapi import APIRouter, Body, File, HTTPException, Query, UploadFile

from ai_promana_backend.api.v1.endpoints import _mock


settings_router = APIRouter()
user_router = APIRouter()
auth_router = APIRouter()
admin_router = APIRouter()
ai_router = APIRouter()


DEFAULT_PROFILE: dict[str, Any] = {
    "name": "Zhang Gong",
    "department": "R&D Center",
    "departmentId": "dept_rd",
    "email": "zhang@example.com",
    "phone": "138****7788",
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
    "emailSubscription": False,
    "auditTrail": True,
    "maskSensitiveData": True,
}


@settings_router.get("/me", summary="设置页首屏数据")
def get_my_settings():
    return _mock.api_response(_user_settings_payload())


@settings_router.put("/me", summary="保存个人设置")
def update_my_settings(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(_save_user_settings_payload(payload))


@settings_router.post("/reset", summary="恢复默认设置")
def reset_my_settings(payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response(_reset_user_settings_payload(payload or {}))


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
def change_password(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(_change_password_payload(payload))


@settings_router.get("/sessions", summary="设备会话列表")
def list_sessions():
    return _mock.api_response(_sessions())


@settings_router.get("/sessions/summary", summary="设备会话摘要")
def get_sessions_summary():
    return _mock.api_response(_sessions_summary())


@settings_router.delete("/sessions/{sessionId}", summary="下线某设备")
def revoke_session(sessionId: str):
    return _mock.api_response(_revoke_session_payload(sessionId))


@user_router.get("/settings", summary="获取用户设置")
def get_user_settings():
    return get_my_settings()


@user_router.put("/settings", summary="保存用户设置")
def update_user_settings(payload: dict[str, Any] = Body(...)):
    return update_my_settings(payload)


@user_router.post("/settings/reset", summary="恢复默认设置")
def reset_user_settings(payload: dict[str, Any] | None = Body(default=None)):
    return reset_my_settings(payload)


@user_router.get("/settings/defaults", summary="获取设置默认值")
def get_user_settings_defaults():
    return get_my_settings_defaults()


@user_router.get("/settings/search", summary="搜索设置项")
def search_user_settings(
    keyword: str | None = Query(default=None),
    tab: str | None = Query(default="all"),
):
    return search_my_settings(keyword, tab)


@auth_router.post("/password/change", summary="修改密码")
def change_auth_password(payload: dict[str, Any] = Body(...)):
    return change_password(payload)


@auth_router.get("/sessions", summary="获取设备会话列表")
def list_auth_sessions():
    return list_sessions()


@auth_router.get("/sessions/summary", summary="获取设备会话摘要")
def get_auth_sessions_summary():
    return get_sessions_summary()


@auth_router.delete("/sessions/{sessionId}", summary="下线设备会话")
def revoke_auth_session(sessionId: str):
    return revoke_session(sessionId)


@admin_router.get("/system-config", summary="系统配置读取")
def get_system_config(
    keyword: str | None = Query(default=None),
    sectionKey: str | None = Query(default=None),
):
    return _mock.api_response(_system_config_payload(keyword, sectionKey))


@admin_router.put("/system-config", summary="系统配置保存")
def update_system_config(payload: dict[str, Any] = Body(...)):
    config = _extract_system_config(payload)
    version = int(payload.get("version", 3)) + 1
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
def reset_system_config(payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
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


@admin_router.get("/system/config", summary="系统配置读取兼容")
def get_system_config_v2(
    keyword: str | None = Query(default=None),
    sectionKey: str | None = Query(default=None),
):
    return _mock.api_response(_system_config_payload(keyword, sectionKey))


@admin_router.put("/system/config", summary="系统配置保存兼容")
def update_system_config_v2(payload: dict[str, Any] = Body(...)):
    return update_system_config(payload)


@admin_router.get("/system/config/defaults", summary="系统默认配置")
def get_system_config_defaults():
    return _mock.api_response(
        {
            "config": DEFAULT_SETTINGS,
            "settings": DEFAULT_SETTINGS,
            "sections": _system_sections(DEFAULT_SETTINGS),
            "version": 1,
        }
    )


@admin_router.post("/system/config/reset", summary="恢复默认配置兼容")
def reset_system_config_v2(payload: dict[str, Any] | None = Body(default=None)):
    return reset_system_config(payload)


@admin_router.get("/system/config/history", summary="系统配置历史")
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
            "changedKeys": ["emailSubscription"],
            "occurredAt": _mock.now_iso(),
            "version": 5,
        },
        {
            "historyId": "cfg_hist_002",
            "operator": "Zhang Gong",
            "action": "恢复默认配置",
            "changedKeys": ["wecomPush", "maskSensitiveData"],
            "occurredAt": "2026-05-11T16:25:00+08:00",
            "version": 4,
        },
    ]
    data = _mock.paged(items, int(page), int(page_size))
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    return _mock.api_response(data)


@admin_router.get("/system/config/export", summary="导出系统配置")
def export_system_config():
    return _mock.api_response(
        {
            **_mock.export_task("system_config_export"),
            "fileName": f"system-config-{_mock.today()}.json",
            "config": DEFAULT_SETTINGS,
        }
    )


@admin_router.post("/system/config/import", summary="导入系统配置")
def import_system_config(file: UploadFile = File(...)):
    return _mock.api_response(
        {
            "fileName": file.filename,
            "importTaskId": _mock.make_id("system_config_import"),
            "valid": True,
            "preview": _system_config_payload(),
        }
    )


@admin_router.get("/system/config/history/export", summary="导出系统配置历史")
def export_system_config_history():
    return _mock.api_response(
        {
            **_mock.export_task("system_config_history_export"),
            "fileName": f"system-config-history-{_mock.today()}.xlsx",
        }
    )


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
                "channel": "email",
                "name": "邮件通知",
                "enabled": True,
                "status": "healthy",
                "description": "用于报表订阅和重要安全提醒。",
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
def update_notification_channels(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "channels": payload.get("channels", payload),
            "updatedAt": _mock.now_iso(),
            "version": int(payload.get("version", 1)) + 1 if isinstance(payload, dict) else 2,
        }
    )


@ai_router.get("/settings-suggestions", summary="AI 偏好建议")
def get_ai_settings_suggestions(context: str | None = Query(default="settings")):
    return _mock.api_response(
        {
            "context": _plain_query_value(context, "settings") or "settings",
            "suggestionId": "sug_settings_001",
            "title": "偏好建议",
            "content": "你当前同时开启了任务和日志通知，建议保留站内提醒并关闭邮件提醒，减少高频干扰。",
            "actions": [
                {"key": "reduce_email_notifications", "label": "采纳建议"},
                {"key": "keep_current", "label": "保持当前设置"},
            ],
            "previewSettings": {
                "notifications": {
                    "taskStatus": True,
                    "logFeedback": True,
                    "reportSubscription": False,
                },
                "aiPrefs": {
                    "autoSummary": True,
                    "scheduling": True,
                    "riskAlert": True,
                },
            },
            "items": _settings_suggestion_items(),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/settings-suggestions/{suggestionId}/apply", summary="采纳 AI 偏好建议")
def apply_ai_settings_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    settings = _user_settings_payload()
    settings["notifications"]["reportSubscription"] = False
    settings["aiPrefs"]["riskAlert"] = True
    settings["version"] = int(body.get("version", settings["version"])) + 1
    settings["updatedAt"] = _mock.now_iso()
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "actionKey": body.get("actionKey", "reduce_email_notifications"),
            "applied": True,
            "settings": settings,
            "version": settings["version"],
            "appliedAt": _mock.now_iso(),
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
            "caption": "站内 / 邮件 / 企微",
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
                {
                    "key": "emailSubscription",
                    "label": "邮件订阅",
                    "description": "周报、导出完成和审计告警可通过邮件发送。",
                    "value": bool(config.get("emailSubscription", False)),
                    "disabled": False,
                    "requiresRestart": False,
                },
            ],
        },
        {
            "key": "security",
            "title": "安全策略",
            "caption": "审计 / 脱敏",
            "items": [
                {
                    "key": "auditTrail",
                    "label": "敏感操作审计",
                    "description": "删除、归档、角色变更和配置保存必须记录审计日志。",
                    "value": bool(config.get("auditTrail", True)),
                    "disabled": False,
                    "requiresRestart": False,
                },
                {
                    "key": "maskSensitiveData",
                    "label": "敏感数据脱敏",
                    "description": "邮箱、手机号、IP 和 Token 等敏感字段默认脱敏展示。",
                    "value": bool(config.get("maskSensitiveData", True)),
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
    sessions = _sessions()
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
        "aiSuggestions": _settings_suggestion_items(),
        "defaults": _settings_defaults(),
        "updatedAt": "2026-05-11T13:20:00+08:00",
        "version": 3,
    }


def _save_user_settings_payload(payload: dict[str, Any]) -> dict[str, Any]:
    profile = payload.get("profile", {})
    email = profile.get("email")
    phone = profile.get("phone")
    if email and "@" not in email:
        raise HTTPException(status_code=400, detail={"code": "USER_EMAIL_INVALID", "message": "请输入有效邮箱"})
    if phone and not _is_phone_like(phone):
        raise HTTPException(status_code=400, detail={"code": "USER_PHONE_INVALID", "message": "请输入有效手机号"})
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


def _sessions() -> list[dict[str, Any]]:
    return [
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


def _sessions_summary() -> dict[str, Any]:
    sessions = _sessions()
    return {
        "activeSessionCount": len(sessions),
        "currentSessionId": next((item["sessionId"] for item in sessions if item["current"]), None),
        "lastPasswordChangedAt": "2026-03-12T09:00:00+08:00",
        "abnormalSessionCount": 0,
    }


def _revoke_session_payload(session_id: str) -> dict[str, Any]:
    current_session = next((item for item in _sessions() if item["sessionId"] == session_id and item["current"]), None)
    if current_session:
        raise HTTPException(status_code=400, detail={"code": "CURRENT_SESSION_REVOKE_DENIED", "message": "当前设备不可直接下线"})
    return {"sessionId": session_id, "revoked": True, "revokedAt": _mock.now_iso()}


def _search_settings_items(keyword: str | None) -> list[dict[str, Any]]:
    items = [
        {"tab": "profile", "label": "个人资料", "description": "姓名、部门、邮箱和手机号"},
        {"tab": "notification", "label": "任务状态变更", "description": "任务完成、阻塞和评审提醒"},
        {"tab": "notification", "label": "报表订阅", "description": "项目周报和全局报表订阅通知"},
        {"tab": "security", "label": "修改密码", "description": "账户密码和设备会话管理"},
        {"tab": "ai", "label": "AI 自动总结", "description": "日报、任务和风险的智能总结偏好"},
    ]
    if not keyword:
        return items
    lowered = str(keyword).lower()
    return [item for item in items if lowered in item["label"].lower() or lowered in item["description"].lower()]


def _settings_suggestion_items() -> list[dict[str, Any]]:
    return [
        {
            "id": "sug_settings_001",
            "title": "降低邮件干扰",
            "content": "保留任务和日志站内提醒，关闭普通报表邮件提醒。",
            "confidence": 0.86,
            "action": "reduce_email_notifications",
        },
        {
            "id": "sug_settings_002",
            "title": "开启风险预警",
            "content": "你参与的项目存在阻塞任务，建议开启 AI 风险预警。",
            "confidence": 0.82,
            "action": "enable_risk_alert",
        },
    ]


def _is_phone_like(value: str) -> bool:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return len(digits) >= 7


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
