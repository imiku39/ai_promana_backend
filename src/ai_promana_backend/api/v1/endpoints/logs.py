# TODO: 审计日志接口当前为首版联调实现，后续接入操作日志表、筛选查询、导出任务和权限校验。
from typing import Any

from fastapi import APIRouter, Body, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


def _audit_items() -> list[dict[str, Any]]:
    return [
        {
            "id": "audit_001",
            "time": _mock.now_iso(),
            "operator": "Zhang Gong",
            "action": "Updated system config",
            "target": "system-config",
            "result": "success",
            "type": "config",
        },
        {
            "id": "audit_002",
            "time": "2026-05-12T18:20:00+08:00",
            "operator": "Chen Siyuan",
            "action": "Created project task",
            "target": "task_002",
            "result": "success",
            "type": "task",
        },
        {
            "id": "audit_003",
            "time": "2026-05-12T17:40:00+08:00",
            "operator": "Wang Yating",
            "action": "Reviewed document",
            "target": "doc_002",
            "result": "success",
            "type": "document",
        },
    ]


# TODO: 从审计日志表分页查询，支持 keyword/type/timeRange 过滤，并补充操作者与目标资源信息。
@router.get("/logs", summary="审计日志列表")
def list_admin_logs(
    keyword: str | None = Query(default=None),
    type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    items = _audit_items()
    if keyword:
        lowered = keyword.lower()
        items = [
            item
            for item in items
            if lowered in item["operator"].lower()
            or lowered in item["action"].lower()
            or lowered in item["target"].lower()
        ]
    if type:
        items = [item for item in items if item["type"] == type]
    data = _mock.paged(items, page, pageSize)
    data["filterOptions"] = {"types": ["config", "task", "document", "user"], "results": ["success", "failed"]}
    return _mock.api_response(data)


# TODO: 创建审计日志导出任务，复用列表筛选条件，并限制只有 admin:log:export 可调用。
@router.post("/logs/export", summary="导出审计日志")
def export_admin_logs(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("audit_log_export")
    task["filters"] = payload or {}
    return _mock.api_response(task)
