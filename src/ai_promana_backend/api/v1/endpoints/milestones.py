# TODO: 甘特/里程碑接口当前为首版联调实现，后续接入 PyMySQL 的排期、基线、依赖关系和权限校验。
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()


@router.get("/{projectId}/gantt/summary", summary="甘特摘要")
def get_project_gantt_summary(projectId: str):
    return _mock.api_response(_gantt_summary(projectId))


@router.get("/{projectId}/gantt", summary="甘特数据")
def get_project_gantt(
    projectId: str,
    viewMode: str | None = Query(default="week"),
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
    baselineVersion: str | None = Query(default=None),
    showBaseline: bool = Query(default=True),
):
    project = _mock.project_lite(projectId)
    timeline_start = _plain_query_value(startDate) or project["startDate"]
    timeline_end = _plain_query_value(endDate) or project.get("endDate") or project.get("deadline") or _mock.today()
    mode = _plain_query_value(viewMode, "week") or "week"
    show_baseline = bool(_plain_query_value(showBaseline, True))
    return _mock.api_response(
        {
            "projectId": projectId,
            "timeline": _timeline(mode, timeline_start, timeline_end),
            "summary": _gantt_summary(projectId, baselineVersion=_plain_query_value(baselineVersion)),
            "items": _gantt_items(projectId, show_baseline=show_baseline),
            "dependencies": _dependencies(projectId),
            "baselineVersion": _plain_query_value(baselineVersion, "V2") or "V2",
            "showBaseline": show_baseline,
            "updatedAt": _mock.now_iso(),
        }
    )


@router.get("/{projectId}/gantt/page-data", summary="甘特页聚合数据")
def get_project_gantt_page(projectId: str):
    project = _mock.project_lite(projectId)
    return _mock.api_response(
        {
            "project": project,
            "summary": _gantt_summary(projectId),
            "timeline": _timeline("week", project["startDate"], project.get("endDate") or _mock.today()),
            "items": _gantt_items(projectId, show_baseline=True),
            "baselines": _baselines(projectId),
            "dependencies": _dependencies(projectId),
            "aiSuggestions": _schedule_suggestions(projectId),
            "permissions": ["project:gantt:read", "project:schedule:update", "project:baseline:update"],
            "updatedAt": _mock.now_iso(),
        }
    )


@router.patch("/{projectId}/schedule/items/{itemId}", summary="更新排期")
def update_schedule_item(projectId: str, itemId: str, payload: dict[str, Any] = Body(...)):
    planned_start = payload.get("plannedStart") or payload.get("startDate")
    planned_end = payload.get("plannedEnd") or payload.get("endDate")
    if planned_start and planned_end and _safe_date(planned_start) > _safe_date(planned_end):
        raise HTTPException(status_code=400, detail={"code": "SCHEDULE_DATE_INVALID", "message": "结束日期需晚于开始日期"})
    delay_days = _delay_days(planned_end or _mock.today(), _baseline_end_for_item(itemId))
    return _mock.api_response(
        {
            "projectId": projectId,
            "itemId": itemId,
            "plannedStart": planned_start,
            "plannedEnd": planned_end,
            "ownerId": payload.get("ownerId"),
            "delayDays": delay_days,
            "version": int(payload.get("version", 1)) + 1,
            "affectedDependencies": ["task_004"] if delay_days > 0 else [],
            "updatedAt": _mock.now_iso(),
        }
    )


@router.get("/{projectId}/baselines", summary="获取基线列表")
def list_project_baselines(projectId: str):
    return _mock.api_response(_baselines(projectId))


@router.get("/{projectId}/dependencies", summary="获取任务依赖")
def get_project_dependencies(projectId: str):
    return _mock.api_response({"projectId": projectId, "dependencies": _dependencies(projectId)})


@router.put("/{projectId}/dependencies", summary="保存任务依赖")
def save_project_dependencies(projectId: str, payload: dict[str, Any] = Body(...)):
    dependencies = payload.get("dependencies", [])
    if _has_self_dependency(dependencies):
        raise HTTPException(status_code=400, detail={"code": "DEPENDENCY_CYCLE_DETECTED", "message": "依赖关系不能指向自身"})
    return _mock.api_response(
        {
            "projectId": projectId,
            "dependencies": dependencies,
            "dependencyCount": len(dependencies),
            "version": int(payload.get("version", 1)) + 1,
            "updatedAt": _mock.now_iso(),
        }
    )


@ai_router.get("/project-schedule-suggestions", summary="AI 排期建议")
def get_project_schedule_suggestions(
    projectId: str | None = Query(default=None),
    context: str | None = Query(default="project_gantt"),
):
    return _mock.api_response(
        {
            "projectId": _plain_query_value(projectId),
            "context": _plain_query_value(context, "project_gantt") or "project_gantt",
            "suggestions": _schedule_suggestions(_plain_query_value(projectId)),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/project-schedule-suggestions/{suggestionId}/apply", summary="采纳 AI 排期建议")
def apply_project_schedule_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "applied": True,
            "createdTasks": body.get("createdTasks", ["task_schedule_recovery_001"]),
            "updatedScheduleItems": body.get("updatedScheduleItems", ["task_001"]),
            "recoverableDays": body.get("recoverableDays", 0.8),
            "message": "已生成排期补救计划，并标记需要刷新甘特图。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _gantt_items(project_id: str, show_baseline: bool) -> list[dict[str, Any]]:
    tasks = _mock.tasks(project_id)
    users = _mock.users()
    items: list[dict[str, Any]] = []
    for index, task in enumerate(tasks):
        planned_start = task.get("startDate") or _mock.today()
        planned_end = str(task.get("dueAt") or _mock.today())[:10]
        baseline_start = (_safe_date(planned_start) - timedelta(days=1)).isoformat()
        baseline_end = _baseline_end_for_item(task["id"])
        delay_days = _delay_days(planned_end, baseline_end)
        owner = next((user for user in users if user["id"] == task.get("assigneeId")), users[0])
        status = "delayed" if delay_days > 0 else "at_risk" if task.get("status") == "blocked" else "normal"
        item = {
            "itemId": task["id"],
            "id": task["id"],
            "itemType": "task",
            "type": "task",
            "name": task["title"],
            "title": task["title"],
            "owner": {"id": owner["id"], "name": owner["name"], "avatar": owner.get("avatar")},
            "plannedStart": planned_start,
            "plannedEnd": planned_end,
            "startDate": planned_start,
            "endDate": planned_end,
            "progress": task.get("progress", 0),
            "status": status,
            "barClass": "red" if status == "delayed" else "amber" if status == "at_risk" else "green",
            "dependencyIds": ["task_002"] if task["id"] == "task_001" else [],
            "isCriticalPath": index < 2,
            "delayDays": delay_days,
            "version": index + 1,
        }
        if show_baseline:
            item["baselineStart"] = baseline_start
            item["baselineEnd"] = baseline_end
        items.append(item)

    project = _mock.project_lite(project_id)
    items.append(
        {
            "itemId": "ms_acceptance",
            "id": "ms_acceptance",
            "itemType": "milestone",
            "type": "milestone",
            "name": "阶段验收",
            "title": "阶段验收",
            "owner": {"id": project.get("ownerId"), "name": project.get("ownerName")},
            "plannedStart": project.get("endDate") or _mock.today(),
            "plannedEnd": project.get("endDate") or _mock.today(),
            "baselineStart": project.get("endDate") or _mock.today(),
            "baselineEnd": project.get("endDate") or _mock.today(),
            "progress": project.get("progress", 0),
            "status": "normal",
            "barClass": "blue",
            "dependencyIds": [tasks[-1]["id"]] if tasks else [],
            "isCriticalPath": True,
            "delayDays": 0,
            "version": 1,
        }
    )
    return items


def _gantt_summary(project_id: str, baselineVersion: str | None = None) -> dict[str, Any]:
    items = _gantt_items(project_id, show_baseline=True)
    delayed = [item for item in items if item.get("delayDays", 0) > 0]
    critical = [item for item in items if item.get("isCriticalPath")]
    max_delay = max([item.get("delayDays", 0) for item in items] or [0])
    project = _mock.project_lite(project_id)
    return {
        "startDate": project["startDate"],
        "endDate": project.get("endDate"),
        "progress": project.get("progress", 0),
        "criticalPathCount": len(critical),
        "baselineVersion": baselineVersion or "V2",
        "baselineCount": len(_baselines(project_id)),
        "delayedNodeCount": len(delayed),
        "maxDelayDays": max_delay,
        "recoverableDays": 0.8,
        "criticalPathText": "开发 → 联调 → 验收",
        "delaySummary": f"+{max_delay} 天" if max_delay > 0 else "无延期",
        "description": "当前实际计划主要偏差集中在联调验证，请优先处理阻塞项。",
    }


def _timeline(view_mode: str, start: str, end: str) -> dict[str, Any]:
    mode = view_mode if view_mode in {"day", "week", "month"} else "week"
    start_date = _safe_date(start)
    end_date = _safe_date(end)
    if end_date < start_date:
        end_date = start_date
    step = 1 if mode == "day" else 7 if mode == "week" else 30
    ticks = []
    cursor = start_date
    while cursor <= end_date:
        ticks.append(cursor.strftime("%m/%d"))
        cursor += timedelta(days=step)
    if not ticks:
        ticks.append(start_date.strftime("%m/%d"))
    return {
        "viewMode": mode,
        "unit": mode,
        "timelineStart": start_date.isoformat(),
        "timelineEnd": end_date.isoformat(),
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "ticks": ticks,
    }


def _baselines(project_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "baseline_001",
            "baselineId": "baseline_001",
            "projectId": project_id,
            "name": "V1 初始基线",
            "version": "V1",
            "createdBy": {"id": "u_10001", "name": "Zhang Gong"},
            "createdAt": "2026-04-14T09:00:00+08:00",
            "itemCount": len(_mock.tasks(project_id)),
            "status": "archived",
        },
        {
            "id": "baseline_002",
            "baselineId": "baseline_002",
            "projectId": project_id,
            "name": "V2 联调基线",
            "version": "V2",
            "createdBy": {"id": "u_10001", "name": "Zhang Gong"},
            "createdAt": "2026-05-01T09:00:00+08:00",
            "itemCount": len(_mock.tasks(project_id)),
            "status": "active",
        },
    ]


def _dependencies(project_id: str) -> list[dict[str, Any]]:
    tasks = _mock.tasks(project_id)
    if len(tasks) < 2:
        return []
    return [
        {
            "id": "dep_001",
            "dependencyId": "dep_001",
            "sourceId": tasks[0]["id"],
            "targetId": tasks[1]["id"],
            "type": "finish_to_start",
            "lagDays": 0,
        }
    ]


def _schedule_suggestions(project_id: str | None) -> list[dict[str, Any]]:
    return [
        {
            "suggestionId": "schedule_sug_001",
            "id": "schedule_sug_001",
            "projectId": project_id,
            "title": "追回联调偏差",
            "content": "建议把联调验证拆成两个并行补救任务，预计可追回 0.8 天。",
            "recoverableDays": 0.8,
            "confidence": 0.84,
            "actions": [
                {"key": "create_recovery_task", "label": "生成补救任务"},
                {"key": "notify_owner", "label": "通知负责人"},
            ],
        },
        {
            "suggestionId": "schedule_sug_002",
            "id": "schedule_sug_002",
            "projectId": project_id,
            "title": "更新基线说明",
            "content": "当前计划和 V2 基线存在偏差，建议设置说明并同步风险看板。",
            "recoverableDays": 0.3,
            "confidence": 0.78,
            "actions": [{"key": "sync_risk", "label": "同步风险"}],
        },
    ]


def _baseline_end_for_item(item_id: str) -> str:
    if item_id == "task_001":
        return (_safe_date(_mock.today()) - timedelta(days=2)).isoformat()
    return _mock.today()


def _delay_days(planned_end: Any, baseline_end: Any) -> int:
    return max((_safe_date(planned_end) - _safe_date(baseline_end)).days, 0)


def _has_self_dependency(dependencies: list[dict[str, Any]]) -> bool:
    return any(item.get("sourceId") and item.get("sourceId") == item.get("targetId") for item in dependencies)


def _safe_date(value: Any) -> date:
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return date.fromisoformat(_mock.today())


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
