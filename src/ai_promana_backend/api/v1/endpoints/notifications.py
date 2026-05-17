# TODO: 通知接口当前为首版联调实现，后续接入 PyMySQL 通知表、偏好设置、消息推送和真实处理流。
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
preferences_router = APIRouter()
ai_router = APIRouter()

CATEGORY_LABELS = {
    "pending": "待处理",
    "system": "系统更新",
    "ai": "AI 提醒",
    "collaboration": "协作反馈",
    "other": "其他",
}

STATUS_LABELS = {
    "pending": "待处理",
    "high_priority": "高优先级",
    "completed": "已完成",
    "ai_reminder": "AI 提醒",
    "collaboration_feedback": "协作反馈",
}


@router.get("/unread-count", summary="顶部未读角标")
def get_unread_count():
    items = _notification_items()
    return _mock.api_response({"count": len([item for item in items if item["unread"]]), "generatedAt": _mock.now_iso()})


@router.get("/summary", summary="通知统计")
def get_notifications_summary(
    scope: str | None = Query(default="mine"),
    date: str | None = Query(default=None),
):
    items = _notification_items()
    summary = _notification_summary(items)
    summary["scope"] = _plain_query_value(scope, "mine") or "mine"
    summary["date"] = _plain_query_value(date, _mock.today()) or _mock.today()
    return _mock.api_response(summary)


@router.get("/categories", summary="通知分类统计")
def get_notification_categories():
    counts = _category_counts(_notification_items())
    return _mock.api_response(
        [
            {"category": key, "label": "全部" if key == "all" else CATEGORY_LABELS.get(key, key), "count": value}
            for key, value in counts.items()
        ]
    )


@router.get("", summary="通知列表")
def list_notifications(
    keyword: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    readStatus: str | None = Query(default="all"),
    priority: str | None = Query(default=None),
    unreadOnly: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    sort: str | None = Query(default="createdAt:desc"),
):
    items = _notification_items()
    keyword_value = _plain_query_value(keyword)
    category_value = _plain_query_value(category)
    status_value = _plain_query_value(status)
    read_status_value = _plain_query_value(readStatus, "all") or "all"
    priority_value = _plain_query_value(priority)
    unread_only_value = bool(_plain_query_value(unreadOnly, False))

    if keyword_value:
        lowered = str(keyword_value).lower()
        items = [
            item
            for item in items
            if lowered in item["title"].lower()
            or lowered in item["description"].lower()
            or lowered in item.get("sourceName", "").lower()
            or lowered in item.get("actionLabel", "").lower()
        ]
    if category_value and category_value != "all":
        items = [item for item in items if item["category"] == category_value]
    if status_value and status_value != "all":
        items = [item for item in items if item["statusCode"] == status_value or item["status"] == status_value]
    if read_status_value == "unread" or unread_only_value:
        items = [item for item in items if item["unread"]]
    if read_status_value == "read":
        items = [item for item in items if not item["unread"]]
    if priority_value:
        items = [item for item in items if item["priority"] == priority_value]
    reverse = str(_plain_query_value(sort, "createdAt:desc")).endswith(":desc")
    items.sort(key=lambda item: item["createdAt"], reverse=reverse)
    page_value = int(_plain_query_value(page, 1) or 1)
    page_size_value = int(_plain_query_value(pageSize, 20) or 20)
    data = _mock.paged(items, page_value, page_size_value)
    return _mock.api_response(
        {
            "list": data["list"],
            "pagination": {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]},
            "categoryCounts": _category_counts(_notification_items()),
            "summary": _notification_summary(items),
            "filters": {
                "keyword": keyword_value,
                "category": category_value or "all",
                "status": status_value or "all",
                "readStatus": read_status_value,
                "priority": priority_value,
            },
        }
    )


@router.post("/read-batch", summary="批量已读")
def mark_notifications_read_batch(payload: dict[str, Any] = Body(...)):
    ids = payload.get("notificationIds", [])
    if not ids and payload.get("scope") not in {"all", "current_filter"}:
        ids = [item["id"] for item in _notification_items() if item["unread"]]
    return _mock.api_response(
        {
            "notificationIds": ids,
            "updatedCount": len(ids) if ids else len([item for item in _notification_items() if item["unread"]]),
            "read": True,
            "readAt": _mock.now_iso(),
        }
    )


@router.get("/process-advice", summary="处理建议面板")
def get_notification_process_advice():
    return _mock.api_response(_process_advice_items())


@router.get("/entry-guide", summary="通知入口说明")
def get_notification_entry_guide():
    return _mock.api_response(
        [
            {
                "title": "通知偏好",
                "description": "可在系统设置中调整任务、日志、报表和 AI 提醒。",
                "targetPath": "/settings",
                "actionLabel": "前往设置",
            },
            {
                "title": "通道配置",
                "description": "管理员可在后台系统配置站内、邮件和企业微信通知。",
                "targetPath": "/admin/system",
                "actionLabel": "查看通道",
            },
        ]
    )


@router.post("/export", summary="导出通知记录")
def export_notifications(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("notification_export")
    task["filters"] = payload or {}
    task["fileType"] = (payload or {}).get("fileType", "xlsx")
    return _mock.api_response(task)


@router.get("/{notificationId}", summary="通知详情")
def get_notification(notificationId: str):
    item = next((notice for notice in _notification_items() if notice["id"] == notificationId), None)
    if not item:
        raise HTTPException(status_code=404, detail={"code": "NOTIFICATION_NOT_FOUND", "message": "通知不存在"})
    detail = {
        **item,
        "detail": _notification_detail(item),
        "actions": [
            {"key": item["actionType"], "label": item["actionLabel"], "targetPath": item.get("actionPath")},
            {"key": "mark_done", "label": "标记完成", "targetPath": None},
        ],
    }
    return _mock.api_response({**detail, "notification": detail})


@router.post("/{notificationId}/read", summary="单条已读")
def mark_notification_read(notificationId: str):
    return _mock.api_response({"id": notificationId, "notificationId": notificationId, "unread": False, "read": True, "readAt": _mock.now_iso()})


@router.post("/{notificationId}/handle", summary="处理通知动作")
def handle_notification(notificationId: str, payload: dict[str, Any] = Body(default_factory=dict)):
    item = next((notice for notice in _notification_items() if notice["id"] == notificationId), None)
    if not item:
        raise HTTPException(status_code=404, detail={"code": "NOTIFICATION_NOT_FOUND", "message": "通知不存在"})
    action_key = payload.get("actionKey") or payload.get("action") or item["actionType"]
    return _mock.api_response(
        {
            "id": notificationId,
            "notificationId": notificationId,
            "actionKey": action_key,
            "handled": True,
            "status": "completed",
            "statusCode": "completed",
            "handledAt": _mock.now_iso(),
            "targetPath": item.get("actionPath"),
            "remark": payload.get("remark"),
        }
    )


@preferences_router.get("/me", summary="获取通知偏好")
def get_notification_preferences():
    return _mock.api_response(_notification_preferences())


@preferences_router.put("/me", summary="保存通知偏好")
def update_notification_preferences(payload: dict[str, Any] = Body(...)):
    return _mock.api_response({**_notification_preferences(), **payload, "updatedAt": _mock.now_iso(), "saved": True})


@ai_router.get("/notification-suggestions", summary="AI 通知建议")
def get_ai_notification_suggestions(
    context: str | None = Query(default="notifications"),
    category: str | None = Query(default=None),
):
    return _mock.api_response(
        {
            "context": _plain_query_value(context, "notifications") or "notifications",
            "category": _plain_query_value(category, "all") or "all",
            "primarySuggestion": {
                "id": "sug_notice_001",
                "title": "通知处理建议",
                "content": "建议先完成高优先级权限审计，再处理角色模板申请；AI 晨报和日志评论类通知可回到工作台集中收尾。",
                "actions": [
                    {"key": "accept", "label": "采纳建议"},
                    {"key": "later", "label": "稍后处理"},
                ],
            },
            "items": [
                {
                    "id": "sug_notice_002",
                    "title": "统一入口已生效",
                    "description": "通知详情现在承载在独立页面中，标题栏按钮不再打开旧弹窗。",
                },
                {
                    "id": "sug_notice_003",
                    "title": "可继续扩展筛选",
                    "description": "后续可扩展状态筛选、已读管理或批量操作。",
                },
            ],
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/notification-suggestions/{suggestionId}/apply", summary="采纳 AI 通知建议")
def apply_ai_notification_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "actionKey": body.get("actionKey", "accept"),
            "notificationIds": body.get("notificationIds", []),
            "applied": True,
            "resultMessage": "已将高优先级通知置顶，并生成处理顺序建议。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _notification_items() -> list[dict[str, Any]]:
    base = [
        {
            "id": "notice-role-change",
            "category": "pending",
            "type": "role_change_request",
            "icon": "warning",
            "iconTheme": "warning",
            "statusCode": "pending",
            "priority": "P1",
            "title": "角色模板变更申请",
            "description": "用户「张三」申请将项目角色从“研发”调整为“PM”，需要确认权限边界与成员分配策略。",
            "unread": True,
            "createdAt": _mock.now_iso(),
            "sourceName": "后台管理",
            "tags": [
                {"label": "后台管理", "type": "p1", "colorSemantic": "warning"},
                {"label": "角色变更", "type": "neutral", "colorSemantic": "neutral"},
            ],
            "actionLabel": "查看角色管理",
            "actionType": "navigate",
            "actionPath": "/admin/roles",
            "targetId": "role_req_001",
            "handled": False,
        },
        {
            "id": "notice-audit-risk",
            "category": "pending",
            "type": "audit_risk",
            "icon": "shield",
            "iconTheme": "danger",
            "statusCode": "high_priority",
            "priority": "P0",
            "title": "高风险权限审计提醒",
            "description": "检测到权限矩阵存在高风险变更，请在审计日志中确认操作链路。",
            "unread": True,
            "createdAt": "2026-05-16T09:20:00+08:00",
            "sourceName": "审计日志",
            "tags": [
                {"label": "P0", "type": "p0", "colorSemantic": "danger"},
                {"label": "权限审计", "type": "warning", "colorSemantic": "warning"},
            ],
            "actionLabel": "查看审计日志",
            "actionType": "navigate",
            "actionPath": "/admin/logs",
            "targetId": "audit_001",
            "handled": False,
        },
        {
            "id": "notice-system-channel",
            "category": "system",
            "type": "notification_channel",
            "icon": "settings",
            "iconTheme": "success",
            "statusCode": "completed",
            "priority": "P2",
            "title": "通知通道配置已更新",
            "description": "站内通知和邮件通道已完成配置校验，企业微信通道仍待配置。",
            "unread": False,
            "createdAt": "2026-05-15T18:10:00+08:00",
            "sourceName": "系统配置",
            "tags": [{"label": "系统更新", "type": "success", "colorSemantic": "success"}],
            "actionLabel": "查看通道配置",
            "actionType": "navigate",
            "actionPath": "/admin/system",
            "targetId": "notification_channels",
            "handled": True,
            "handledAt": "2026-05-15T18:20:00+08:00",
        },
        {
            "id": "notice-ai-briefing",
            "category": "ai",
            "type": "daily_ai_briefing",
            "icon": "auto_awesome",
            "iconTheme": "ai",
            "statusCode": "ai_reminder",
            "priority": "P2",
            "title": "AI 晨报已生成",
            "description": "今日建议优先处理阻塞任务，并同步项目周报摘要。",
            "unread": True,
            "createdAt": "2026-05-17T08:45:00+08:00",
            "sourceName": "AI 助手",
            "tags": [{"label": "AI", "type": "ai", "colorSemantic": "ai"}],
            "actionLabel": "返回工作台",
            "actionType": "navigate",
            "actionPath": "/workbench",
            "targetId": "daily_report_latest",
            "handled": False,
        },
        {
            "id": "notice-log-feedback",
            "category": "collaboration",
            "type": "log_feedback",
            "icon": "chat",
            "iconTheme": "neutral",
            "statusCode": "collaboration_feedback",
            "priority": "P3",
            "title": "日志互动反馈",
            "description": "陈思远在你的工作日志下补充了联调验证说明。",
            "unread": False,
            "createdAt": "2026-05-14T16:30:00+08:00",
            "sourceName": "个人工作台",
            "tags": [{"label": "协作反馈", "type": "neutral", "colorSemantic": "neutral"}],
            "actionLabel": "查看工作台",
            "actionType": "navigate",
            "actionPath": "/workbench",
            "targetId": "log_20260514",
            "handled": True,
            "handledAt": "2026-05-14T17:00:00+08:00",
        },
    ]
    for item in base:
        item["status"] = STATUS_LABELS.get(item["statusCode"], item["statusCode"])
        item["read"] = not item["unread"]
        item["targetPath"] = item.get("actionPath")
    return base


def _notification_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    unread_count = len([item for item in items if item["unread"]])
    high_priority_count = len([item for item in items if item["priority"] in {"P0", "P1"} and not item["handled"]])
    processed_today_count = len([item for item in items if item.get("handled")])
    return {
        "unreadCount": unread_count,
        "unread": unread_count,
        "highPriorityCount": high_priority_count,
        "processedTodayCount": processed_today_count,
        "pending": len([item for item in items if item["statusCode"] == "pending"]),
        "total": len(items),
        "categoryCounts": _category_counts(items),
        "categories": [
            {"category": key, "count": value}
            for key, value in _category_counts(items).items()
            if key != "all"
        ],
        "generatedAt": _mock.now_iso(),
    }


def _category_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"all": len(items), "pending": 0, "system": 0, "ai": 0, "collaboration": 0}
    for item in items:
        category = item.get("category", "other")
        counts[category] = counts.get(category, 0) + 1
    return counts


def _process_advice_items() -> list[dict[str, Any]]:
    return [
        {
            "title": "先处理权限和角色类通知",
            "description": "这两类通知会直接影响后台配置与项目权限边界，优先级高于一般系统更新和信息提醒。",
            "priority": 1,
        },
        {
            "title": "AI 摘要类通知适合批量收尾",
            "description": "晨报、日志草稿和任务补录等内容可回到工作台集中处理。",
            "priority": 2,
        },
    ]


def _notification_detail(item: dict[str, Any]) -> dict[str, Any]:
    if item["type"] == "role_change_request":
        return {"requesterName": "张三", "fromRole": "研发", "toRole": "PM", "projectName": "纳米材料项目 A"}
    if item["type"] == "audit_risk":
        return {"operatorName": "Zhang Gong", "riskLevel": "P0", "resource": "权限矩阵", "target": item["targetId"]}
    return {"sourceName": item["sourceName"], "targetId": item.get("targetId")}


def _notification_preferences() -> dict[str, Any]:
    return {
        "inAppEnabled": True,
        "emailEnabled": True,
        "enterpriseWechatEnabled": False,
        "taskStatus": True,
        "logFeedback": True,
        "reportSubscription": False,
        "channels": {"inApp": True, "email": True, "wecom": False},
        "categories": {
            "pending": True,
            "system": True,
            "ai": True,
            "collaboration": True,
        },
        "quietHours": {
            "enabled": False,
            "start": "22:00",
            "end": "08:00",
        },
        "updatedAt": _mock.now_iso(),
        "version": 3,
    }


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
