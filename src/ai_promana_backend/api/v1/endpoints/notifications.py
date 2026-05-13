# TODO: 通知接口当前为首版联调实现，后续接入通知表、偏好设置、消息推送和真实处理流。
from typing import Any

from fastapi import APIRouter, Body, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
preferences_router = APIRouter()
ai_router = APIRouter()


# TODO: 统计当前用户未读通知数量，需排除已删除和已过期通知。
@router.get("/unread-count", summary="顶部未读角标")
def get_unread_count():
    return _mock.api_response({"count": len([item for item in _mock.notifications() if not item["read"]])})


# TODO: 按分类、处理状态和未读状态聚合通知数量，用于通知中心顶部统计卡片。
@router.get("/summary", summary="通知统计")
def get_notifications_summary():
    items = _mock.notifications()
    return _mock.api_response(
        {
            "total": len(items),
            "unread": len([item for item in items if not item["read"]]),
            "pending": len([item for item in items if item["status"] == "pending"]),
            "categories": [
                {"category": "pending", "count": len([item for item in items if item["category"] == "pending"])},
                {"category": "system", "count": len([item for item in items if item["category"] == "system"])},
                {"category": "ai", "count": len([item for item in items if item["category"] == "ai"])},
                {"category": "other", "count": len([item for item in items if item["category"] == "other"])},
            ],
        }
    )


# TODO: 从通知表分页查询当前用户通知，支持 category/status/unreadOnly 过滤和创建时间排序。
@router.get("", summary="通知列表")
def list_notifications(
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    unreadOnly: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    items = _mock.notifications()
    if category:
        items = [item for item in items if item["category"] == category]
    if status:
        items = [item for item in items if item["status"] == status]
    if unreadOnly:
        items = [item for item in items if not item["read"]]
    return _mock.api_response(_mock.paged(items, page, pageSize))


# TODO: 批量更新通知已读状态，校验 notificationIds 均属于当前用户并返回实际更新数量。
@router.post("/read-batch", summary="批量已读")
def mark_notifications_read_batch(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "notificationIds": payload.get("notificationIds", []),
            "read": True,
            "readAt": _mock.now_iso(),
        }
    )


# TODO: 基于当前待处理通知生成处理建议，合并任务、风险、审批等可跳转动作。
@router.get("/process-advice", summary="处理建议面板")
def get_notification_process_advice():
    return _mock.api_response(
        {
            "suggestions": _mock.ai_suggestions("notification_process"),
            "quickActions": [
                {"key": "read_all", "label": "Mark all as read"},
                {"key": "open_blocked", "label": "Open blocked tasks"},
            ],
        }
    )


# TODO: 查询单条通知详情，包含动作按钮、来源业务对象和已读状态；不存在时返回 NOTIFICATION_NOT_FOUND。
@router.get("/{notificationId}", summary="通知详情")
def get_notification(notificationId: str):
    item = next((notice for notice in _mock.notifications() if notice["id"] == notificationId), _mock.notifications()[0])
    item["id"] = notificationId
    item["actions"] = [
        {"key": "view", "label": "View", "targetPath": item.get("targetPath")},
        {"key": "mark_done", "label": "Mark done", "targetPath": None},
    ]
    return _mock.api_response({"notification": item})


# TODO: 将单条通知标记为已读，保证幂等并记录首次阅读时间。
@router.post("/{notificationId}/read", summary="单条已读")
def mark_notification_read(notificationId: str):
    return _mock.api_response({"notificationId": notificationId, "read": True, "readAt": _mock.now_iso()})


# TODO: 根据通知类型执行处理动作，例如确认风险、跳转任务或完成审批，并更新处理状态。
@router.post("/{notificationId}/handle", summary="处理通知动作")
def handle_notification(notificationId: str, payload: dict[str, Any] = Body(default_factory=dict)):
    return _mock.api_response(
        {
            "notificationId": notificationId,
            "action": payload.get("action", "mark_done"),
            "status": "completed",
            "handledAt": _mock.now_iso(),
        }
    )


# TODO: 读取当前用户通知偏好，合并系统默认值、用户覆盖值和渠道可用状态。
@preferences_router.get("/me", summary="获取通知偏好")
def get_notification_preferences():
    return _mock.api_response(
        {
            "taskStatus": True,
            "logFeedback": True,
            "reportSubscription": "weekly",
            "channels": {"inApp": True, "email": False, "wecom": True},
        }
    )


# TODO: 校验通知偏好字段和渠道开关，保存用户覆盖配置并刷新推送订阅。
@preferences_router.put("/me", summary="保存通知偏好")
def update_notification_preferences(payload: dict[str, Any] = Body(...)):
    payload["updatedAt"] = _mock.now_iso()
    return _mock.api_response(payload)


# TODO: 将未读/待处理通知上下文提交给 AI 服务，生成合并、降噪或优先级建议。
@ai_router.get("/notification-suggestions", summary="AI 通知建议")
def get_ai_notification_suggestions():
    return _mock.api_response({"suggestions": _mock.ai_suggestions("notification")})


# TODO: 采纳 AI 通知建议后执行批量已读、偏好调整或任务创建等动作，并写入采纳记录。
@ai_router.post("/notification-suggestions/{suggestionId}/apply", summary="采纳 AI 通知建议")
def apply_ai_notification_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"suggestionId": suggestionId, "applied": True, "payload": payload or {}})
