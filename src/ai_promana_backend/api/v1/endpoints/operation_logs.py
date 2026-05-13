# TODO: 操作日志接口当前为首版联调实现，后续接入操作日志中间件产物和真实分页查询。
from fastapi import APIRouter, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 从操作日志表按 targetId/operatorId 分页查询，并补充目标类型、操作者和变更摘要。
@router.get("", summary="操作日志列表")
def list_operation_logs(
    targetId: str | None = Query(default=None),
    operatorId: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    logs = [
        {
            "id": "oplog_001",
            "operatorId": "u_10001",
            "operatorName": "Zhang Gong",
            "action": "project.update",
            "targetId": "project_001",
            "targetType": "project",
            "content": "Updated project progress",
            "createdAt": _mock.now_iso(),
        },
        {
            "id": "oplog_002",
            "operatorId": "u_10002",
            "operatorName": "Chen Siyuan",
            "action": "task.transition",
            "targetId": "task_001",
            "targetType": "task",
            "content": "Moved task to blocked",
            "createdAt": "2026-05-12T17:30:00+08:00",
        },
    ]
    if targetId:
        logs = [item for item in logs if item["targetId"] == targetId]
    if operatorId:
        logs = [item for item in logs if item["operatorId"] == operatorId]
    return _mock.api_response(_mock.paged(logs, page, pageSize))
