# TODO: 审计日志接口当前为首版联调实现，后续接入操作日志表、筛选查询、导出任务和权限校验。
from typing import Any

from fastapi import APIRouter, Body, Query, Response

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 从审计日志表分页查询，支持 keyword/type/timeRange 过滤，并补充操作者与目标资源信息。
@router.get("/logs", summary="审计日志列表")
def list_admin_logs(
    keyword: str | None = Query(default=None),
    globalKeyword: str | None = Query(default=None),
    type: str | None = Query(default=None),
    startTime: str | None = Query(default=None),
    endTime: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    sortBy: str | None = Query(default="occurredAt"),
    sortOrder: str | None = Query(default="desc"),
):
    filters = _log_filters(keyword, globalKeyword, type, startTime, endTime, page, pageSize, sortBy, sortOrder)
    items = _filter_audit_items(filters)
    items.sort(key=lambda item: item.get(filters["sortBy"]) or "", reverse=filters["sortOrder"] != "asc")
    data = _mock.paged(items, int(filters["page"]), int(filters["pageSize"]))
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    data["filterOptions"] = _log_options()
    data["summary"] = {
        "total": data["total"],
        "failedCount": len([item for item in items if item["resultStatus"] == "failure"]),
        "highRiskCount": len([item for item in items if item["riskLevel"] == "high"]),
    }
    return _mock.api_response(data)


@router.get("/logs/options", summary="审计日志选项")
def get_admin_log_options():
    return _mock.api_response(_log_options())


# TODO: GET 导出用于前端 blob 下载，返回可下载 CSV；POST 导出保留异步任务兼容。
@router.get("/logs/export", summary="导出审计日志文件")
def export_admin_logs_file(
    keyword: str | None = Query(default=None),
    globalKeyword: str | None = Query(default=None),
    type: str | None = Query(default=None),
    startTime: str | None = Query(default=None),
    endTime: str | None = Query(default=None),
):
    filters = _log_filters(keyword, globalKeyword, type, startTime, endTime, 1, 100, "occurredAt", "desc")
    rows = _filter_audit_items(filters)
    csv = _audit_csv(rows)
    file_name = f"audit-logs-{_mock.today()}.csv"
    return Response(
        content=csv.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.post("/logs/export", summary="创建审计日志导出任务")
def export_admin_logs(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("audit_log_export")
    task.update(
        {
            "filters": payload or {},
            "fileName": f"audit-logs-{_mock.today()}.csv",
            "message": "审计日志导出任务已创建",
            "createdAt": _mock.now_iso(),
        }
    )
    return _mock.api_response(task)


@router.get("/logs/{logId}/export", summary="导出审计日志详情")
def export_admin_log_detail(logId: str):
    item = _find_audit_item(logId)
    csv = _audit_csv([item])
    return Response(
        content=csv.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="audit-log-{logId}.csv"'},
    )


@router.get("/logs/{logId}", summary="审计日志详情")
def get_admin_log_detail(logId: str):
    item = _find_audit_item(logId)
    return _mock.api_response(
        {
            "log": item,
            "diff": [
                {"field": "status", "before": "disabled", "after": "enabled"},
                {"field": "version", "before": 2, "after": 3},
            ],
            "request": {
                "requestId": item["requestId"],
                "method": "PUT",
                "path": "/api/admin/system-config",
                "ip": item["ip"],
                "userAgent": "Chrome / Windows",
            },
        }
    )


def _audit_items() -> list[dict[str, Any]]:
    base_rows = [
        {
            "id": "audit_001",
            "occurredAt": _mock.now_iso(),
            "operatorId": "u_10001",
            "operator": "Zhang Gong",
            "action": "修改系统配置",
            "actionKey": "update_system_config",
            "target": "通知通道策略",
            "targetType": "system_config",
            "targetId": "system_notification",
            "resultStatus": "success",
            "type": "config",
            "riskLevel": "high",
        },
        {
            "id": "audit_002",
            "occurredAt": "2026-05-12T18:20:00+08:00",
            "operatorId": "u_10002",
            "operator": "Chen Siyuan",
            "action": "创建项目任务",
            "actionKey": "create_task",
            "target": "task_002",
            "targetType": "task",
            "targetId": "task_002",
            "resultStatus": "success",
            "type": "other",
            "riskLevel": "low",
        },
        {
            "id": "audit_003",
            "occurredAt": "2026-05-12T17:40:00+08:00",
            "operatorId": "u_10003",
            "operator": "Wang Yating",
            "action": "查看文档",
            "actionKey": "review_document",
            "target": "doc_002",
            "targetType": "document",
            "targetId": "doc_002",
            "resultStatus": "success",
            "type": "other",
            "riskLevel": "low",
        },
        {
            "id": "audit_004",
            "occurredAt": "2026-05-11T16:10:00+08:00",
            "operatorId": "u_10001",
            "operator": "Zhang Gong",
            "action": "删除项目模板",
            "actionKey": "delete_project_template",
            "target": "临时排障模板",
            "targetType": "project_template",
            "targetId": "tpl_temp",
            "resultStatus": "success",
            "type": "delete",
            "riskLevel": "medium",
        },
        {
            "id": "audit_005",
            "occurredAt": "2026-05-10T09:26:00+08:00",
            "operatorId": "u_10004",
            "operator": "Li Ming",
            "action": "停用用户失败",
            "actionKey": "disable_user",
            "target": "u_10003",
            "targetType": "user",
            "targetId": "u_10003",
            "resultStatus": "failure",
            "type": "config",
            "riskLevel": "high",
        },
    ]
    return [_audit_item(row) for row in base_rows]


def _audit_item(row: dict[str, Any]) -> dict[str, Any]:
    result_label = "成功" if row["resultStatus"] == "success" else "失败"
    return {
        **row,
        "logId": row["id"],
        "time": row["occurredAt"].replace("T", " ")[:16],
        "result": result_label,
        "status": row["resultStatus"],
        "ip": row.get("ip", "192.168.*.*"),
        "requestId": row.get("requestId", _mock.make_id("req")),
        "riskLabel": {"high": "高", "medium": "中", "low": "低"}.get(row["riskLevel"], row["riskLevel"]),
    }


def _filter_audit_items(filters: dict[str, Any]) -> list[dict[str, Any]]:
    items = _audit_items()
    keywords = [filters.get("keyword"), filters.get("globalKeyword")]
    for keyword in [item for item in keywords if item]:
        lowered = str(keyword).lower()
        items = [
            item
            for item in items
            if lowered in item["operator"].lower()
            or lowered in item["action"].lower()
            or lowered in item["target"].lower()
            or lowered in item["result"].lower()
        ]
    if filters.get("type") and filters["type"] != "all":
        items = [item for item in items if item["type"] == filters["type"]]
    if filters.get("startTime"):
        items = [item for item in items if item["occurredAt"] >= filters["startTime"]]
    if filters.get("endTime"):
        items = [item for item in items if item["occurredAt"] <= filters["endTime"]]
    return items


def _find_audit_item(log_id: str) -> dict[str, Any]:
    found = next((item for item in _audit_items() if item["id"] == log_id or item["logId"] == log_id), None)
    if found:
        return found
    item = _audit_items()[0]
    item["id"] = log_id
    item["logId"] = log_id
    return item


def _log_options() -> dict[str, Any]:
    types = [
        {"key": "all", "value": "all", "label": "全部动作"},
        {"key": "delete", "value": "delete", "label": "删除"},
        {"key": "config", "value": "config", "label": "配置"},
        {"key": "other", "value": "other", "label": "其他"},
    ]
    results = [
        {"key": "success", "value": "success", "label": "成功"},
        {"key": "failure", "value": "failure", "label": "失败"},
    ]
    risk_levels = [
        {"key": "high", "value": "high", "label": "高风险"},
        {"key": "medium", "value": "medium", "label": "中风险"},
        {"key": "low", "value": "low", "label": "低风险"},
    ]
    return {
        "types": types,
        "typeOptions": types,
        "results": results,
        "resultOptions": results,
        "riskLevels": risk_levels,
    }


def _log_filters(
    keyword: Any,
    global_keyword: Any,
    log_type: Any,
    start_time: Any,
    end_time: Any,
    page: Any,
    page_size: Any,
    sort_by: Any,
    sort_order: Any,
) -> dict[str, Any]:
    return {
        "keyword": _plain_query_value(keyword),
        "globalKeyword": _plain_query_value(global_keyword),
        "type": _plain_query_value(log_type, "all") or "all",
        "startTime": _plain_query_value(start_time),
        "endTime": _plain_query_value(end_time),
        "page": _plain_query_value(page, 1) or 1,
        "pageSize": _plain_query_value(page_size, 20) or 20,
        "sortBy": _plain_query_value(sort_by, "occurredAt") or "occurredAt",
        "sortOrder": _plain_query_value(sort_order, "desc") or "desc",
    }


def _audit_csv(rows: list[dict[str, Any]]) -> str:
    header = ["日志ID", "时间", "操作者", "动作", "对象", "结果", "类型", "IP", "请求ID"]
    lines = [",".join(header)]
    for row in rows:
        values = [
            row["id"],
            row["time"],
            row["operator"],
            row["action"],
            row["target"],
            row["result"],
            row["type"],
            row["ip"],
            row["requestId"],
        ]
        lines.append(",".join(_csv_cell(value) for value in values))
    return "\n".join(lines)


def _csv_cell(value: Any) -> str:
    text = str(value).replace('"', '""')
    return f'"{text}"'


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
