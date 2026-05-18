# TODO: 工作台/PBC 接口当前为首版联调实现，后续接入 PyMySQL 的任务、日志、PBC 目标和 AI 建议服务。
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()

PRIORITY_LABELS = {
    "p0": "P0",
    "p1": "P1",
    "p2": "P2",
    "p3": "P3",
    "P0": "P0",
    "P1": "P1",
    "P2": "P2",
    "P3": "P3",
}

STATUS_LABELS = {
    "pending": "待开始",
    "todo": "待开始",
    "in_progress": "进行中",
    "doing": "进行中",
    "review": "待评审",
    "completed": "已完成",
    "done": "已完成",
    "blocked": "已阻塞",
}


@router.get("/overview", summary="工作台聚合数据")
def get_workbench_overview(
    tab: str | None = Query(default="logs"),
    dateValue: str | None = Query(default=None, alias="date"),
):
    active_tab = _plain_query_value(tab, "logs") or "logs"
    target_date = _plain_query_value(dateValue, None) or _mock.today()
    today_log = _today_log(target_date)
    kanban = _workbench_kanban_payload(priority=None, due_range=None, blocked_only=False, keyword=None, group_by="project")
    pbc = _pbc_payload(period_id=None)
    interactions = _log_interactions()
    unread_count = len([item for item in _mock.notifications() if not item["read"]])
    focus = {
        "todoTaskCount": len([task for task in _workbench_tasks() if task["status"] not in {"completed", "done"}]),
        "logInteractionCount": len(interactions),
        "aiSummary": "AI 判断今天最值得优先处理的是阻塞任务和即将到期的评审事项。",
    }
    return _mock.api_response(
        {
            "userId": _mock.current_user()["id"],
            "activeTab": active_tab,
            "currentUser": _mock.current_user(),
            "notificationUnreadCount": unread_count,
            "unreadCount": unread_count,
            "focus": focus,
            "todayLog": today_log,
            "todayLogs": [
                {
                    "id": today_log["logId"],
                    "logId": today_log["logId"],
                    "projectId": "project_001",
                    "taskId": "task_001",
                    "content": today_log["completed"],
                    "hours": 2.5,
                    "createdAt": _mock.now_iso(),
                }
            ],
            "tomorrowPlans": [
                {
                    "id": "plan_001",
                    "title": "确认联调资源窗口并推进评审",
                    "priority": "P1",
                    "projectId": "project_001",
                }
            ],
            "blockedItems": [task for task in _workbench_tasks() if task["isBlocked"]],
            "kanban": kanban,
            "kanbanTasks": [task for column in kanban["columns"] for task in column["tasks"]],
            "pbc": pbc,
            "pbcObjectives": pbc["goals"],
            "quickTaskDefaults": _task_create_options()["defaultValues"],
            "aiCards": _workbench_ai_cards(),
            "aiSuggestions": _workbench_suggestion_items(active_tab),
        }
    )


@router.get("/logs/today", summary="获取今日日志")
def get_today_log(dateValue: str | None = Query(default=None, alias="date")):
    target_date = _plain_query_value(dateValue, None) or _mock.today()
    return _mock.api_response(_today_log(target_date))


@router.put("/logs/today", summary="保存今日日志")
def save_today_log(payload: dict[str, Any] = Body(...)):
    completed = str(payload.get("completed") or "").strip()
    if not completed:
        raise HTTPException(status_code=400, detail={"code": "WORKLOG_VALIDATE_FAILED", "message": "请输入今日完成内容"})
    version = int(payload.get("version", 1)) + 1
    return _mock.api_response(
        {
            "logId": payload.get("logId") or f"log_{str(payload.get('date') or _mock.today()).replace('-', '')}",
            "date": payload.get("date") or _mock.today(),
            "completed": completed,
            "tomorrowPlan": payload.get("tomorrowPlan", ""),
            "blockers": payload.get("blockers", ""),
            "version": version,
            "updatedAt": _mock.now_iso(),
        }
    )


@router.get("/logs/interactions", summary="获取日志互动")
def list_log_interactions(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
):
    data = _mock.paged(
        _log_interactions(),
        int(_plain_query_value(page, 1) or 1),
        int(_plain_query_value(pageSize, 10) or 10),
    )
    return _mock.api_response(
        {
            "list": data["list"],
            "pagination": {
                "page": data["page"],
                "pageSize": data["pageSize"],
                "total": data["total"],
            },
        }
    )


@router.get("/kanban", summary="个人看板")
def get_workbench_kanban(
    priority: str | None = Query(default=None),
    dueRange: str | None = Query(default=None),
    blockedOnly: bool = Query(default=False),
    keyword: str | None = Query(default=None),
    groupBy: str | None = Query(default="project"),
):
    return _mock.api_response(
        _workbench_kanban_payload(
            priority=_plain_query_value(priority),
            due_range=_plain_query_value(dueRange),
            blocked_only=bool(_plain_query_value(blockedOnly, False)),
            keyword=_plain_query_value(keyword),
            group_by=_plain_query_value(groupBy, "project") or "project",
        )
    )


@router.get("/pbc", summary="PBC 目标")
def get_workbench_pbc(periodId: str | None = Query(default=None)):
    return _mock.api_response(_pbc_payload(_plain_query_value(periodId)))


@router.post("/pbc/{goalId}/bind-tasks", summary="绑定任务到 PBC 目标")
def bind_tasks_to_pbc(goalId: str, payload: dict[str, Any] = Body(...)):
    task_ids = payload.get("taskIds") or ["task_001", "task_002"]
    if not isinstance(task_ids, list) or not task_ids:
        raise HTTPException(status_code=400, detail={"code": "PBC_TASK_IDS_REQUIRED", "message": "请选择要绑定的任务"})
    return _mock.api_response(
        {
            "goalId": goalId,
            "boundTaskIds": task_ids,
            "boundTaskCount": len(task_ids),
            "forecastRate": 73,
            "updatedAt": _mock.now_iso(),
        }
    )


@router.get("/task-create-options", summary="新建任务弹窗选项")
def get_task_create_options():
    return _mock.api_response(_task_create_options())


@router.get("/pbc-objectives", summary="PBC 目标列表")
def list_pbc_objectives():
    return _mock.api_response({"list": _pbc_goals(), "goals": _pbc_goals()})


@router.post("/pbc-objectives", summary="创建 PBC 目标")
def create_pbc_objective(payload: dict[str, Any] = Body(...)):
    title = str(payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail={"code": "PBC_TITLE_REQUIRED", "message": "请输入目标名称"})
    objective = {
        "goalId": _mock.make_id("pbc"),
        "id": _mock.make_id("pbc"),
        "goalType": payload.get("goalType", "numeric"),
        "title": title,
        "description": payload.get("description", ""),
        "progressRate": int(payload.get("progressRate", payload.get("progress", 0)) or 0),
        "progress": int(payload.get("progressRate", payload.get("progress", 0)) or 0),
        "ownerId": payload.get("ownerId", _mock.current_user()["id"]),
        "status": payload.get("status", "in_progress"),
        "boundTaskCount": 0,
        "completedTaskCount": 0,
        "createdAt": _mock.now_iso(),
    }
    return _mock.api_response({**objective, "objective": objective})


@ai_router.post("/workbench/log-draft", summary="AI 生成工作台日志草稿")
def generate_workbench_log_draft(payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    target_date = body.get("date") or _mock.today()
    return _mock.api_response(
        {
            "logId": f"log_{str(target_date).replace('-', '')}",
            "date": target_date,
            "completed": "1. 推进联调环境参数回灌；2. 完成异常样本记录补齐；3. 同步评审人处理计划。",
            "tomorrowPlan": "1. 确认资源窗口；2. 推动阻塞任务进入评审；3. 更新 PBC 绑定任务。",
            "blockers": "联调环境资源窗口仍需项目负责人确认。",
            "sourceTaskIds": body.get("taskIds", ["task_001", "task_002"]),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.get("/workbench-suggestions", summary="AI 工作台建议")
def get_workbench_suggestions(
    context: str | None = Query(default="workbench"),
    tab: str | None = Query(default="logs"),
):
    active_tab = _plain_query_value(tab, "logs") or "logs"
    return _mock.api_response(
        {
            "context": _plain_query_value(context, "workbench") or "workbench",
            "tab": active_tab,
            "card": {
                "suggestionId": "sug_workbench_001",
                "title": "工作建议",
                "content": "建议先生成今日日志草稿，再处理阻塞任务和 PBC 绑定事项。",
                "actions": [
                    {"key": "generate_log_draft", "label": "立即生成"},
                    {"key": "remind_later", "label": "稍后提醒"},
                ],
            },
            "items": _workbench_suggestion_items(active_tab),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/workbench-suggestions/{suggestionId}/apply", summary="采纳 AI 工作台建议")
def apply_workbench_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    action_key = body.get("actionKey", "generate_log_draft")
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "actionKey": action_key,
            "applied": True,
            "affectedSections": _affected_sections_for_action(action_key),
            "message": "已采纳工作台建议，并同步相关模块的刷新标记。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _today_log(target_date: str) -> dict[str, Any]:
    return {
        "logId": f"log_{target_date.replace('-', '')}",
        "date": target_date,
        "completed": "1. 完成联调验证说明补齐；2. 跟进异常样本记录；3. 处理项目看板阻塞项。",
        "tomorrowPlan": "1. 跟进平台组联调环境准备；2. 推进待评审任务关闭。",
        "blockers": "联调环境参数回灌任务仍缺少资源窗口确认。",
        "aiDraftAvailable": True,
        "interactions": _log_interactions(),
        "version": 3,
        "updatedAt": _mock.now_iso(),
    }


def _log_interactions() -> list[dict[str, Any]]:
    return [
        {
            "id": "interaction_001",
            "type": "comment",
            "user": {"id": "u_10002", "name": "Chen Siyuan"},
            "content": "已补充异常样本截图，等待你确认。",
            "targetLogId": f"log_{_mock.today().replace('-', '')}",
            "createdAt": _mock.now_iso(),
        },
        {
            "id": "interaction_002",
            "type": "ai_summary",
            "user": {"id": "ai", "name": "AI 助手"},
            "content": "今天的重点任务集中在阻塞清理和评审推动。",
            "targetLogId": f"log_{_mock.today().replace('-', '')}",
            "createdAt": _mock.now_iso(),
        },
    ]


def _workbench_kanban_payload(
    priority: str | None,
    due_range: str | None,
    blocked_only: bool,
    keyword: str | None,
    group_by: str,
) -> dict[str, Any]:
    tasks = _workbench_tasks()
    if priority and priority != "all":
        wanted = _priority_label(priority)
        tasks = [task for task in tasks if task["priority"] == wanted]
    if blocked_only:
        tasks = [task for task in tasks if task["isBlocked"]]
    if due_range == "this_week":
        tasks = [task for task in tasks if _is_due_this_week(task.get("deadlineAt"))]
    if keyword:
        lowered = keyword.lower()
        tasks = [
            task
            for task in tasks
            if lowered in task["title"].lower()
            or lowered in (task.get("projectName") or "").lower()
            or lowered in " ".join(task.get("tags", [])).lower()
        ]
    columns = _group_tasks(tasks, group_by)
    return {
        "columns": columns,
        "summary": {
            "taskTotal": len(tasks),
            "blockedTaskCount": len([task for task in tasks if task["isBlocked"]]),
            "p0p1TaskCount": len([task for task in tasks if task["priority"] in {"P0", "P1"}]),
            "dueThisWeekCount": len([task for task in tasks if _is_due_this_week(task.get("deadlineAt"))]),
        },
        "filters": {
            "priority": priority or "all",
            "dueRange": due_range or "all",
            "blockedOnly": blocked_only,
            "keyword": keyword,
            "groupBy": group_by,
        },
        "updatedAt": _mock.now_iso(),
    }


def _workbench_tasks() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for task in _mock.tasks():
        priority = _priority_label(task.get("priority"))
        deadline_at = task.get("dueAt") or f"{_mock.today()}T18:00:00+08:00"
        items.append(
            {
                "id": task["id"],
                "taskId": task["id"],
                "title": task["title"],
                "projectId": task.get("projectId"),
                "projectName": task.get("projectName"),
                "priority": priority,
                "tag": (task.get("tags") or ["任务"])[0],
                "tags": task.get("tags", []),
                "deadline": _deadline_label(deadline_at),
                "deadlineAt": deadline_at,
                "progress": task.get("progress", 0),
                "status": task.get("status"),
                "statusLabel": STATUS_LABELS.get(task.get("status"), task.get("status")),
                "isBlocked": task.get("status") == "blocked",
                "blockedReason": task.get("blockedReason"),
                "pbcGoalId": "pbc_001" if task["id"] != "task_003" else "pbc_002",
                "detailPath": f"/task/{task['id']}",
            }
        )
    return items


def _group_tasks(tasks: list[dict[str, Any]], group_by: str) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for task in tasks:
        if group_by == "status":
            key = str(task.get("status") or "pending")
            name = STATUS_LABELS.get(key, key)
        else:
            key = task.get("projectId") or "general"
            name = task.get("projectName") or "通用事项"
        group = groups.setdefault(key, {"columnId": key, "columnName": name, "tasks": []})
        group["tasks"].append(task)
    return list(groups.values())


def _pbc_payload(period_id: str | None) -> dict[str, Any]:
    return {
        "periodId": period_id or "2026Q2",
        "goals": _pbc_goals(),
        "evaluationThread": [
            {
                "type": "self",
                "content": "本周期已完成 5 个关键任务，联调与日报效率改造推进正常。",
                "createdAt": _mock.now_iso(),
            },
            {
                "type": "manager",
                "content": "方向正确，建议下周期把负载热力图和智能分配作为核心推进项。",
                "createdAt": _mock.now_iso(),
            },
        ],
        "summary": {
            "goalTotal": len(_pbc_goals()),
            "averageProgressRate": round(sum(item["progressRate"] for item in _pbc_goals()) / len(_pbc_goals()), 1),
            "waitingFeedbackCount": len([item for item in _pbc_goals() if item["status"] == "waiting_manager_feedback"]),
        },
    }


def _pbc_goals() -> list[dict[str, Any]]:
    return [
        {
            "goalId": "pbc_001",
            "id": "pbc_001",
            "goalType": "numeric",
            "title": "提升团队协作效率",
            "description": "对齐部门 OKR：缩短联调和日报协作耗时。",
            "progressRate": 64,
            "progress": 64,
            "status": "in_progress",
            "boundTaskCount": 8,
            "completedTaskCount": 5,
            "selfReview": "本周期已完成联调协同流程优化。",
            "managerFeedback": "继续关注阻塞任务清理效率。",
            "forecastRate": 73,
            "forecastDays": 7,
            "ownerId": _mock.current_user()["id"],
        },
        {
            "goalId": "pbc_002",
            "id": "pbc_002",
            "goalType": "milestone",
            "title": "完成协作管理系统首版上线",
            "description": "对齐季度 KPI：完成项目全生命周期协同平台首版交付。",
            "progressRate": 51,
            "progress": 51,
            "status": "waiting_manager_feedback",
            "boundTaskCount": 6,
            "completedTaskCount": 3,
            "selfReview": "核心页面已完成，后端接口正在分批补齐。",
            "managerFeedback": "建议优先保障项目和任务闭环。",
            "forecastRate": 68,
            "forecastDays": 10,
            "ownerId": _mock.current_user()["id"],
        },
    ]


def _task_create_options() -> dict[str, Any]:
    projects = [
        {"id": item["id"], "name": item["name"], "label": item["name"], "value": item["id"]}
        for item in _mock.projects()
    ]
    projects.append({"id": "general", "name": "通用事项", "label": "通用事项", "value": "general"})
    users = [
        {
            "id": item["id"],
            "name": item["name"],
            "label": item["name"],
            "value": item["id"],
            "avatar": item.get("avatar"),
        }
        for item in _mock.users()
    ]
    return {
        "projects": projects,
        "assignees": users,
        "reviewers": users,
        "pbcGoals": [{"id": item["goalId"], "title": item["title"], "label": item["title"], "value": item["goalId"]} for item in _pbc_goals()],
        "templates": [
            {"id": "log_followup", "name": "日志跟进任务", "label": "日志跟进任务", "recommended": True},
            {"id": "kanban_progress", "name": "看板推进任务", "label": "看板推进任务", "recommended": False},
            {"id": "pbc_bound", "name": "PBC 绑定任务", "label": "PBC 绑定任务", "recommended": False},
        ],
        "defaultValues": {
            "projectId": "project_001",
            "assigneeId": _mock.current_user()["id"],
            "status": "todo",
            "priority": "P1",
            "startDate": _mock.today(),
            "deadlineAt": f"{_mock.today()}T18:00:00+08:00",
            "progress": 0,
            "riskType": "none",
            "reminderChannels": ["in_app", "wechat_work"],
            "syncOptions": {
                "syncTodayLog": True,
                "addTomorrowPlan": True,
                "syncPersonalKanban": True,
                "bindPbcTrend": True,
            },
        },
        "aiSuggestions": [
            {
                "suggestionId": "task_create_sug_001",
                "title": "优先补齐联调收尾任务",
                "content": "如果任务和联调验证相关，建议直接设置为 P1 并同步到 PBC。",
            }
        ],
    }


def _workbench_ai_cards() -> dict[str, Any]:
    return {
        "logSuggestion": {
            "title": "AI 日志建议",
            "content": "今天完成的任务中，有 2 个可自动映射到日报。",
        },
        "pbcTrend": {
            "title": "AI 趋势提示",
            "content": "按照当前任务完成速度，本周期 PBC 达成率预计将在 7 天内提升至 73%。",
        },
    }


def _workbench_suggestion_items(tab: str) -> list[dict[str, Any]]:
    return [
        {
            "suggestionId": "sug_workbench_log",
            "title": "日志提醒",
            "content": "建议先生成今日日志草稿，再手动确认阻塞描述。",
            "actionKey": "generate_log_draft",
            "tab": tab,
        },
        {
            "suggestionId": "sug_workbench_kanban",
            "title": "看板提醒",
            "content": "联调回灌任务仍在阻塞列，建议今天优先处理。",
            "actionKey": "open_blocked_tasks",
            "tab": tab,
        },
        {
            "suggestionId": "sug_workbench_pbc",
            "title": "PBC 建议",
            "content": "当前有任务尚未绑定目标，自动关联后周期趋势会更完整。",
            "actionKey": "bind_pbc_tasks",
            "tab": tab,
        },
    ]


def _affected_sections_for_action(action_key: str) -> list[str]:
    if action_key == "generate_log_draft":
        return ["todayLog", "aiCards"]
    if action_key == "bind_pbc_tasks":
        return ["pbc", "kanban"]
    return ["overview"]


def _priority_label(value: Any) -> str:
    text = str(value or "P2")
    return PRIORITY_LABELS.get(text, PRIORITY_LABELS.get(text.lower(), text.upper() if text.lower().startswith("p") else text))


def _deadline_label(value: str) -> str:
    day = str(value)[:10]
    if day == _mock.today():
        return "今天 18:00"
    return day


def _is_due_this_week(value: Any) -> bool:
    target = _safe_date(value)
    today = date.fromisoformat(_mock.today())
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start <= target <= week_end


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
