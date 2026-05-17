# TODO: 任务接口当前为首版联调实现，后续接入 PyMySQL repository、评论/子任务表、看板排序和状态机。
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
project_router = APIRouter()
ai_router = APIRouter()

KANBAN_COLUMN_DEFS: list[dict[str, Any]] = [
    {
        "columnId": "todo",
        "name": "待开始",
        "title": "待开始",
        "status": "todo",
        "aliases": {"todo", "pending"},
        "order": 1,
        "styleLevel": "neutral",
    },
    {
        "columnId": "doing",
        "name": "进行中",
        "title": "进行中",
        "status": "doing",
        "aliases": {"doing", "in_progress", "active"},
        "order": 2,
        "styleLevel": "primary",
    },
    {
        "columnId": "review",
        "name": "待评审",
        "title": "待评审",
        "status": "review",
        "aliases": {"review"},
        "order": 3,
        "styleLevel": "warning",
    },
    {
        "columnId": "done",
        "name": "已完成",
        "title": "已完成",
        "status": "done",
        "aliases": {"done", "completed"},
        "order": 4,
        "styleLevel": "success",
    },
    {
        "columnId": "blocked",
        "name": "已阻塞",
        "title": "已阻塞",
        "status": "blocked",
        "aliases": {"blocked"},
        "order": 5,
        "styleLevel": "danger",
    },
]

STATUS_LABELS = {
    "todo": "待开始",
    "pending": "待开始",
    "doing": "进行中",
    "in_progress": "进行中",
    "active": "进行中",
    "review": "待评审",
    "done": "已完成",
    "completed": "已完成",
    "blocked": "已阻塞",
}

DETAIL_STATUS_BY_COLUMN = {
    "todo": "pending",
    "doing": "in_progress",
    "review": "review",
    "done": "completed",
    "blocked": "blocked",
}

PRIORITY_LABELS = {
    "p0": "P0",
    "p1": "P1",
    "p2": "P2",
    "p3": "P3",
    "P0": "P0",
    "P1": "P1",
    "P2": "P2",
    "P3": "P3",
    "urgent": "紧急",
    "high": "高",
    "medium": "中",
    "low": "低",
}

PRIORITY_STYLE = {
    "P0": "danger",
    "P1": "warning",
    "P2": "primary",
    "P3": "neutral",
    "紧急": "danger",
    "高": "warning",
    "中": "primary",
    "低": "neutral",
}


@router.post("/drafts", summary="保存任务草稿")
def save_task_draft(payload: dict[str, Any] = Body(...)):
    draft = _normalize_task_payload(payload)
    return _mock.api_response(
        {
            "draftId": _mock.make_id("task_draft"),
            "savedAt": _mock.now_iso(),
            "recoverable": True,
            "draft": draft,
        }
    )


@router.post("", summary="创建任务")
def create_task(payload: dict[str, Any] = Body(...)):
    task = _task_from_payload(payload)
    return _mock.api_response({"taskId": task["id"], "task": _task_detail(task)})


@router.get("/{taskId}", summary="任务详情")
def get_task_detail(taskId: str):
    task = _task_detail(_mock.task_lite(taskId))
    return _mock.api_response({**task, "task": task})


@router.put("/{taskId}", summary="更新任务")
def replace_task(taskId: str, payload: dict[str, Any] = Body(...)):
    task = _task_detail(_merge_task_payload(taskId, payload))
    return _mock.api_response(
        {
            "taskId": taskId,
            "version": task["version"],
            "updatedAt": task["updatedAt"],
            "task": task,
        }
    )


@router.patch("/{taskId}", summary="更新任务字段")
def update_task(taskId: str, payload: dict[str, Any] = Body(...)):
    task = _task_detail(_merge_task_payload(taskId, payload))
    return _mock.api_response({"task": task})


@router.delete("/{taskId}", summary="删除任务")
def delete_task(taskId: str):
    return _mock.api_response(
        {
            "taskId": taskId,
            "deleted": True,
            "deletedAt": _mock.now_iso(),
            "targetPath": "/workbench",
        }
    )


@router.get("/{taskId}/transition-options", summary="任务状态流转选项")
def get_task_transition_options(taskId: str):
    current = _task_detail(_mock.task_lite(taskId))
    options = [
        {
            "status": item["status"],
            "value": DETAIL_STATUS_BY_COLUMN[item["columnId"]],
            "columnKey": item["columnId"],
            "label": item["name"],
            "styleLevel": item["styleLevel"],
            "requiresReason": item["columnId"] == "blocked",
            "allowed": not (current["columnKey"] == "todo" and item["columnId"] == "done"),
        }
        for item in KANBAN_COLUMN_DEFS
    ]
    return _mock.api_response(
        {
            "taskId": taskId,
            "currentStatus": current["status"],
            "currentColumnKey": current["columnKey"],
            "options": options,
            "rules": _flow_rules_detailed(),
        }
    )


@router.post("/{taskId}/transition", summary="任务状态流转")
def transition_task(taskId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response(_transition_payload(task_id=taskId, project_id=None, payload=payload))


@router.get("/{taskId}/comments", summary="获取评论列表")
def list_task_comments(
    taskId: str,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    comments = _task_comments(taskId)
    data = _mock.paged(
        comments,
        int(_plain_query_value(page, 1) or 1),
        int(_plain_query_value(pageSize, 20) or 20),
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


@router.post("/{taskId}/comments", summary="添加评论")
def add_task_comment(taskId: str, payload: dict[str, Any] = Body(...)):
    content = str(payload.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=400, detail={"code": "COMMENT_CONTENT_INVALID", "message": "请输入评论内容"})
    comment = {
        "id": _mock.make_id("comment"),
        "taskId": taskId,
        "author": _comment_author(_mock.current_user()),
        "content": content,
        "mentionedUserIds": payload.get("mentionedUserIds", []),
        "createdAt": _mock.now_iso(),
        "permissions": ["delete"],
    }
    return _mock.api_response({**comment, "comment": comment})


@router.delete("/{taskId}/comments/{commentId}", summary="删除评论")
def delete_task_comment(taskId: str, commentId: str):
    return _mock.api_response({"taskId": taskId, "commentId": commentId, "deleted": True, "deletedAt": _mock.now_iso()})


@router.post("/{taskId}/subtasks", summary="创建子任务")
def create_subtask(taskId: str, payload: dict[str, Any] = Body(...)):
    title = str(payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail={"code": "SUBTASK_TITLE_REQUIRED", "message": "请输入子任务标题"})
    subtask = {
        "id": _mock.make_id("subtask"),
        "taskId": taskId,
        "title": title,
        "completed": False,
        "assigneeId": payload.get("assigneeId"),
        "sortOrder": payload.get("sortOrder", 6000),
        "version": 1,
        "createdAt": _mock.now_iso(),
    }
    return _mock.api_response({**subtask, "subtask": subtask})


@router.patch("/{taskId}/subtasks/{subtaskId}", summary="勾选子任务")
def update_subtask(taskId: str, subtaskId: str, payload: dict[str, Any] = Body(...)):
    completed = bool(payload.get("completed", True))
    return _mock.api_response(
        {
            "id": subtaskId,
            "taskId": taskId,
            "completed": completed,
            "completedAt": _mock.now_iso() if completed else None,
            "taskProgress": 40 if completed else 20,
            "version": int(payload.get("version", 1)) + 1,
        }
    )


@router.delete("/{taskId}/subtasks/{subtaskId}", summary="删除子任务")
def delete_subtask(taskId: str, subtaskId: str):
    return _mock.api_response({"taskId": taskId, "subtaskId": subtaskId, "deleted": True, "deletedAt": _mock.now_iso()})


@project_router.get("/{projectId}/kanban/summary", summary="看板统计")
def get_project_kanban_summary(
    projectId: str,
    status: str | None = Query(default=None),
    priorities: str | None = Query(default=None),
    dueRange: str | None = Query(default=None),
    blockedOnly: bool = Query(default=False),
    milestoneId: str | None = Query(default=None),
):
    filters = _kanban_filters(status, priorities, dueRange, blockedOnly, milestoneId)
    return _mock.api_response(_kanban_summary(_filtered_project_tasks(projectId, filters)))


@project_router.get("/{projectId}/kanban", summary="看板列和任务")
def get_project_kanban(
    projectId: str,
    status: str | None = Query(default=None),
    priorities: str | None = Query(default=None),
    dueRange: str | None = Query(default=None),
    blockedOnly: bool = Query(default=False),
    milestoneId: str | None = Query(default=None),
):
    filters = _kanban_filters(status, priorities, dueRange, blockedOnly, milestoneId)
    tasks = _filtered_project_tasks(projectId, filters)
    return _mock.api_response(
        {
            "summary": _kanban_summary(tasks),
            "columns": _kanban_columns_from_tasks(tasks),
            "filters": filters,
            "updatedAt": _mock.now_iso(),
        }
    )


@project_router.get("/{projectId}/kanban/flow-rules", summary="状态流转规则")
def get_project_kanban_flow_rules(projectId: str):
    return _mock.api_response({"projectId": projectId, "rules": _flow_rules_detailed()})


@project_router.get("/{projectId}/kanban/options", summary="看板筛选选项")
def get_project_kanban_options(projectId: str):
    return _mock.api_response(
        {
            "projectId": projectId,
            "statuses": [
                {
                    "label": item["name"],
                    "value": item["columnId"],
                    "status": item["status"],
                    "styleLevel": item["styleLevel"],
                }
                for item in KANBAN_COLUMN_DEFS
            ],
            "priorities": [
                {"label": label, "value": value, "styleLevel": PRIORITY_STYLE.get(label, "neutral")}
                for value, label in [("P0", "P0"), ("P1", "P1"), ("P2", "P2"), ("P3", "P3")]
            ],
            "dueRanges": [
                {"label": "全部", "value": "all"},
                {"label": "本周截止", "value": "this_week"},
                {"label": "已逾期", "value": "overdue"},
            ],
            "milestones": [
                {"id": "ms_001", "label": "需求确认", "value": "ms_001"},
                {"id": "ms_002", "label": "联调验证", "value": "ms_002"},
            ],
            "assignees": [
                {"id": item["id"], "name": item["name"], "label": item["name"], "value": item["id"]}
                for item in _mock.users()
            ],
        }
    )


@project_router.get("/{projectId}/kanban/page-data", summary="看板聚合数据")
def get_project_kanban_page(projectId: str):
    tasks = _filtered_project_tasks(projectId, _kanban_filters(None, None, None, False, None))
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "summary": _kanban_summary(tasks),
            "columns": _kanban_columns_from_tasks(tasks),
            "flowRules": _flow_rules_detailed(),
            "filters": get_project_kanban_options(projectId)["data"],
            "aiSuggestions": _project_kanban_suggestions(projectId),
            "updatedAt": _mock.now_iso(),
        }
    )


@project_router.post("/{projectId}/tasks", summary="在项目内创建任务")
def create_project_task(projectId: str, payload: dict[str, Any] = Body(...)):
    payload = {**payload, "projectId": projectId}
    task = _task_from_payload(payload)
    return _mock.api_response({"taskId": task["id"], "task": _task_card(task), "detail": _task_detail(task)})


@project_router.put("/{projectId}/tasks/{taskId}", summary="编辑任务")
def update_project_task(projectId: str, taskId: str, payload: dict[str, Any] = Body(...)):
    task = _merge_task_payload(taskId, {**payload, "projectId": projectId})
    return _mock.api_response({"task": _task_detail(task), "card": _task_card(task), "updatedAt": _mock.now_iso()})


@project_router.post("/{projectId}/tasks/{taskId}/transition", summary="任务状态流转")
def transition_project_task(projectId: str, taskId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response(_transition_payload(task_id=taskId, project_id=projectId, payload=payload))


@project_router.patch("/{projectId}/kanban/order", summary="调整看板顺序")
def update_kanban_order(projectId: str, payload: dict[str, Any] = Body(...)):
    columns = payload.get("columns", payload.get("order", []))
    return _mock.api_response(
        {
            "projectId": projectId,
            "columns": columns,
            "version": int(payload.get("version", 1)) + 1,
            "updatedAt": _mock.now_iso(),
        }
    )


@ai_router.get("/project-kanban-suggestions", summary="AI 看板建议")
def get_project_kanban_suggestions(
    projectId: str | None = Query(default=None),
    context: str | None = Query(default="project_kanban"),
):
    return _mock.api_response(
        {
            "projectId": projectId,
            "context": context or "project_kanban",
            "suggestions": _project_kanban_suggestions(projectId),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/project-kanban-suggestions/{suggestionId}/apply", summary="采纳 AI 看板建议")
def apply_project_kanban_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    changed_tasks = body.get("taskIds") or body.get("changedTasks") or ["task_001"]
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "actionKey": body.get("actionKey", "apply"),
            "applied": True,
            "changedTasks": changed_tasks,
            "message": "已采纳看板建议，并同步任务卡片与成员通知。",
            "appliedAt": _mock.now_iso(),
        }
    )


@ai_router.get("/task-suggestions", summary="AI 任务建议")
def get_task_suggestions(
    taskId: str = Query(...),
    context: str | None = Query(default="task_detail"),
):
    return _mock.api_response(_task_ai_suggestion_payload(taskId, context or "task_detail"))


@ai_router.post("/task-suggestions/{suggestionId}/apply", summary="采纳 AI 任务建议")
def apply_task_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "taskId": body.get("taskId"),
            "actionKey": body.get("actionKey", "create_subtasks"),
            "applied": True,
            "createdSubtasks": body.get("createdSubtasks", ["subtask_ai_001", "subtask_ai_002"]),
            "message": "已采纳任务拆解建议。",
            "appliedAt": _mock.now_iso(),
        }
    )


@ai_router.get("/tasks/{taskId}/suggestions", summary="任务 AI 建议")
def get_task_ai_suggestions(taskId: str):
    return _mock.api_response(_task_ai_suggestion_payload(taskId, "task_detail"))


@ai_router.post("/tasks/{taskId}/suggestions/{suggestionId}/apply", summary="采纳任务 AI 建议")
def apply_task_ai_suggestion(taskId: str, suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    body.setdefault("taskId", taskId)
    result = apply_task_suggestion(suggestionId, body)["data"]
    result["taskId"] = taskId
    return _mock.api_response(result)


def _task_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_task_payload(payload)
    task_id = normalized.get("id") or _mock.make_id("task")
    return {
        "id": task_id,
        "title": normalized["title"],
        "status": normalized["status"],
        "columnKey": normalized["columnKey"],
        "priority": normalized["priority"],
        "projectId": normalized["projectId"],
        "projectName": normalized.get("projectName", _mock.project_lite(normalized["projectId"]).get("name")),
        "assigneeId": normalized.get("assigneeId"),
        "assigneeName": normalized.get("assigneeName"),
        "reviewerId": normalized.get("reviewerId"),
        "reviewerName": normalized.get("reviewerName"),
        "progress": normalized["progress"],
        "startDate": normalized["startDate"],
        "dueAt": normalized["dueAt"],
        "deadline": normalized["deadline"],
        "estimatedHours": normalized.get("estimatedHours"),
        "estimateHours": normalized.get("estimateHours", normalized.get("estimatedHours")),
        "blockedReason": normalized.get("blockedReason"),
        "description": normalized.get("description"),
        "tags": normalized.get("tags", []),
        "milestoneId": normalized.get("milestoneId", "ms_002"),
        "dependencyTaskIds": normalized.get("dependencyTaskIds", []),
        "sortOrder": normalized.get("sortOrder", 1000),
        "version": normalized.get("version", 1),
        "createdAt": normalized.get("createdAt", _mock.now_iso()),
        "updatedAt": _mock.now_iso(),
    }


def _normalize_task_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = payload.copy()
    column_key = _column_key_for_status(normalized.get("columnKey") or normalized.get("status") or "todo")
    detail_status = _detail_status_for_column(column_key)
    priority = _priority_value(normalized.get("priority", "P2"))
    assignee_id = normalized.get("assigneeId") or normalized.get("ownerId")
    assignee = _user_by_id(assignee_id)
    deadline = normalized.get("deadline") or _date_part(normalized.get("dueAt")) or _mock.today()
    normalized.update(
        {
            "title": normalized.get("title") or "未命名任务",
            "status": detail_status,
            "columnKey": column_key,
            "priority": priority,
            "projectId": normalized.get("projectId") or "project_001",
            "assigneeId": assignee_id or assignee["id"],
            "assigneeName": normalized.get("assigneeName") or normalized.get("ownerName") or assignee["name"],
            "progress": int(normalized.get("progress", 0) or 0),
            "startDate": normalized.get("startDate") or _mock.today(),
            "deadline": deadline,
            "dueAt": normalized.get("dueAt") or f"{deadline}T18:00:00+08:00",
            "tags": normalized.get("tags") or [],
            "dependencyTaskIds": normalized.get("dependencyTaskIds") or [],
        }
    )
    return normalized


def _merge_task_payload(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    base = _mock.task_lite(task_id)
    merged = {**base, **payload, "id": task_id}
    return _task_from_payload(merged)


def _task_detail(task: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_task_payload(task)
    assignee = _user_by_id(normalized.get("assigneeId"))
    project = _mock.project_lite(normalized["projectId"])
    subtasks = _task_subtasks(normalized["id"])
    comments = _task_comments(normalized["id"])
    completed_count = len([item for item in subtasks if item["completed"]])
    progress = normalized["progress"] or int(completed_count / max(len(subtasks), 1) * 100)
    return {
        "id": normalized["id"],
        "taskId": normalized["id"],
        "title": normalized["title"],
        "status": normalized["status"],
        "statusLabel": STATUS_LABELS.get(normalized["status"], normalized["status"]),
        "columnKey": normalized["columnKey"],
        "kanbanStatus": normalized["columnKey"],
        "priority": normalized["priority"],
        "priorityLabel": PRIORITY_LABELS.get(normalized["priority"], normalized["priority"]),
        "priorityStyle": PRIORITY_STYLE.get(PRIORITY_LABELS.get(normalized["priority"], ""), "neutral"),
        "assignee": _task_user(assignee),
        "owner": _task_user(assignee),
        "assigneeId": assignee["id"],
        "assigneeName": assignee["name"],
        "deadline": normalized["deadline"],
        "dueAt": normalized["dueAt"],
        "project": {"id": project["id"], "name": project["name"]},
        "projectId": project["id"],
        "projectName": project["name"],
        "description": normalized.get("description") or "当前任务用于前后端联调，后续会替换为数据库中的任务描述。",
        "progress": progress,
        "blockedReason": normalized.get("blockedReason"),
        "tags": normalized.get("tags", []),
        "dependencyTaskIds": normalized.get("dependencyTaskIds", []),
        "subtasks": subtasks,
        "comments": comments,
        "summary": {
            "subtaskTotal": len(subtasks),
            "completedSubtaskCount": completed_count,
            "commentCount": len(comments),
            "progress": progress,
        },
        "permissions": ["task:update", "task:delete", "task:transition", "task:comment:create", "task:subtask:update"],
        "createdBy": _task_user(_mock.current_user()),
        "createdAt": normalized.get("createdAt", _mock.now_iso()),
        "updatedAt": normalized.get("updatedAt", _mock.now_iso()),
        "version": int(normalized.get("version", 1)),
        "aiSuggestions": _task_ai_suggestion_payload(normalized["id"], "task_detail"),
    }


def _task_card(task: dict[str, Any], sort_order: int | None = None) -> dict[str, Any]:
    normalized = _normalize_task_payload(task)
    assignee = _user_by_id(normalized.get("assigneeId"))
    priority_label = PRIORITY_LABELS.get(normalized["priority"], normalized["priority"])
    return {
        "taskId": normalized["id"],
        "id": normalized["id"],
        "title": normalized["title"],
        "status": normalized["columnKey"],
        "detailStatus": normalized["status"],
        "statusLabel": STATUS_LABELS.get(normalized["status"], normalized["status"]),
        "columnKey": normalized["columnKey"],
        "priority": priority_label,
        "priorityValue": normalized["priority"],
        "priorityStyle": PRIORITY_STYLE.get(priority_label, "neutral"),
        "tags": normalized.get("tags", []),
        "note": normalized.get("note") or f"负责人：{assignee['name']} · 进度 {normalized['progress']}%",
        "owner": _task_user(assignee),
        "assignee": _task_user(assignee),
        "progress": normalized["progress"],
        "deadline": normalized["deadline"],
        "milestoneId": normalized.get("milestoneId", "ms_002"),
        "blockedReason": normalized.get("blockedReason"),
        "dependencyTaskIds": normalized.get("dependencyTaskIds", []),
        "sortOrder": sort_order if sort_order is not None else int(normalized.get("sortOrder", 1000)),
        "version": int(normalized.get("version", 1)),
        "detailPath": f"/task/{normalized['id']}",
    }


def _filtered_project_tasks(project_id: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = [_task_from_payload(task) for task in _mock.tasks(project_id)]
    status_filter = filters.get("status")
    if status_filter and status_filter != "all":
        column_key = _column_key_for_status(status_filter)
        tasks = [task for task in tasks if _column_key_for_status(task.get("status") or task.get("columnKey")) == column_key]
    if filters.get("blockedOnly"):
        tasks = [task for task in tasks if _column_key_for_status(task.get("status")) == "blocked"]
    priorities = filters.get("priorities") or []
    if priorities:
        wanted = {_priority_value(item) for item in priorities}
        tasks = [task for task in tasks if _priority_value(task.get("priority")) in wanted]
    if filters.get("dueRange") == "this_week":
        tasks = [task for task in tasks if _is_due_this_week(task.get("deadline") or _date_part(task.get("dueAt")))]
    if filters.get("dueRange") == "overdue":
        today = date.fromisoformat(_mock.today())
        tasks = [
            task
            for task in tasks
            if _safe_date(task.get("deadline") or _date_part(task.get("dueAt"))) < today
        ]
    if filters.get("milestoneId"):
        tasks = [task for task in tasks if task.get("milestoneId", "ms_002") == filters["milestoneId"]]
    return tasks


def _kanban_columns_from_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    columns = []
    for definition in KANBAN_COLUMN_DEFS:
        column_tasks = [
            task
            for task in tasks
            if _column_key_for_status(task.get("status") or task.get("columnKey")) == definition["columnId"]
        ]
        cards = [_task_card(task, (index + 1) * 1000) for index, task in enumerate(column_tasks)]
        columns.append(
            {
                "columnId": definition["columnId"],
                "key": definition["columnId"],
                "name": definition["name"],
                "title": definition["title"],
                "status": definition["status"],
                "count": len(cards),
                "order": definition["order"],
                "styleLevel": definition["styleLevel"],
                "cards": cards,
                "tasks": cards,
            }
        )
    return columns


def _kanban_summary(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    blocked_count = len([task for task in tasks if _column_key_for_status(task.get("status")) == "blocked"])
    p0p1_count = len([task for task in tasks if _priority_value(task.get("priority")) in {"P0", "P1"}])
    due_this_week_count = len(
        [task for task in tasks if _is_due_this_week(task.get("deadline") or _date_part(task.get("dueAt")))]
    )
    return {
        "taskTotal": len(tasks),
        "totalTasks": len(tasks),
        "blockedCount": blocked_count,
        "blockedTasks": blocked_count,
        "p0p1Count": p0p1_count,
        "dueThisWeekCount": due_this_week_count,
        "updatedAt": _mock.now_iso(),
    }


def _kanban_filters(
    status: str | None,
    priorities: str | None,
    due_range: str | None,
    blocked_only: bool,
    milestone_id: str | None,
) -> dict[str, Any]:
    status_value = _plain_query_value(status, "all")
    priorities_value = _plain_query_value(priorities)
    due_range_value = _plain_query_value(due_range, "all")
    blocked_only_value = bool(_plain_query_value(blocked_only, False))
    milestone_id_value = _plain_query_value(milestone_id)
    return {
        "status": status_value or "all",
        "priorities": _split_csv(priorities_value),
        "dueRange": due_range_value or "all",
        "blockedOnly": blocked_only_value,
        "milestoneId": milestone_id_value,
    }


def _flow_rules_detailed() -> list[dict[str, Any]]:
    return [
        {
            "ruleId": "rule_001",
            "rule": "待开始不可直接完成",
            "description": "任务必须先进入进行中或待评审，再标记完成。",
            "notifyRule": "无",
            "fromStatus": "todo",
            "toStatus": "done",
            "allowed": False,
            "requiredFields": [],
        },
        {
            "ruleId": "rule_002",
            "rule": "标记阻塞需填写原因",
            "description": "流转到已阻塞时必须填写阻塞原因，可附带依赖任务。",
            "notifyRule": "通知创建者与项目负责人",
            "fromStatus": "*",
            "toStatus": "blocked",
            "allowed": True,
            "requiredFields": ["blockedReason"],
        },
        {
            "ruleId": "rule_003",
            "rule": "待评审完成后通知相关人员",
            "description": "评审通过并完成后，通知负责人、评审人与项目负责人。",
            "notifyRule": "通知负责人、评审人与 PM",
            "fromStatus": "review",
            "toStatus": "done",
            "allowed": True,
            "requiredFields": [],
        },
    ]


def _transition_payload(task_id: str, project_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    from_status = payload.get("fromStatus")
    to_status = payload.get("toStatus") or payload.get("status") or payload.get("columnKey")
    if not to_status:
        raise HTTPException(status_code=400, detail={"code": "TASK_VALIDATE_FAILED", "message": "toStatus is required"})

    from_column = _column_key_for_status(from_status or _mock.task_lite(task_id).get("status"))
    to_column = _column_key_for_status(to_status)
    if from_column == "todo" and to_column == "done":
        raise HTTPException(status_code=400, detail={"code": "TASK_TRANSITION_DENIED", "message": "待开始任务不可直接完成"})
    if to_column == "blocked" and not str(payload.get("blockedReason") or "").strip():
        raise HTTPException(status_code=400, detail={"code": "TASK_BLOCK_REASON_REQUIRED", "message": "请填写阻塞原因"})

    version = int(payload.get("version", 1)) + 1
    notified_users = payload.get("notifiedUsers") or ["u_10001", "u_10002"]
    result = {
        "taskId": task_id,
        "status": _detail_status_for_column(to_column),
        "statusLabel": STATUS_LABELS.get(to_column),
        "kanbanStatus": to_column,
        "columnKey": to_column,
        "version": version,
        "blockedReason": payload.get("blockedReason"),
        "dependencyTaskIds": payload.get("dependencyTaskIds", []),
        "notifiedUsers": notified_users,
        "transitionedAt": _mock.now_iso(),
    }
    if project_id:
        result["projectId"] = project_id
    return result


def _task_subtasks(task_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "subtask_001",
            "taskId": task_id,
            "title": "确认验收口径",
            "completed": True,
            "assigneeId": "u_10001",
            "sortOrder": 1000,
            "completedAt": _mock.now_iso(),
            "version": 1,
        },
        {
            "id": "subtask_002",
            "taskId": task_id,
            "title": "同步评审人和阻塞处理计划",
            "completed": False,
            "assigneeId": "u_10002",
            "sortOrder": 2000,
            "completedAt": None,
            "version": 1,
        },
    ]


def _task_comments(task_id: str) -> list[dict[str, Any]]:
    users = _mock.users()
    return [
        {
            "id": "comment_001",
            "taskId": task_id,
            "author": _comment_author(users[1]),
            "content": "请保持看板卡片上的阻塞原因可见，方便项目负责人快速判断。",
            "createdAt": _mock.now_iso(),
            "mentionedUserIds": ["u_10001"],
            "permissions": [],
        },
        {
            "id": "comment_002",
            "taskId": task_id,
            "author": _comment_author(users[0]),
            "content": "已同步评审窗口，今天下班前补齐验证记录。",
            "createdAt": _mock.now_iso(),
            "mentionedUserIds": [],
            "permissions": ["delete"],
        },
    ]


def _task_ai_suggestion_payload(task_id: str, context: str) -> dict[str, Any]:
    suggestions = _mock.ai_suggestions("task")
    primary = suggestions[0]
    return {
        "taskId": task_id,
        "context": context,
        "suggestionId": primary["id"],
        "breakdown": "建议拆分为：确认验收口径、补齐验证记录、同步评审人、关闭阻塞项。",
        "scheduling": "建议今天完成资料补齐，明天上午进入评审，评审后同步看板状态。",
        "confidence": primary["confidence"],
        "actions": [
            {"key": "create_subtasks", "label": "生成子任务"},
            {"key": "update_schedule", "label": "更新排期"},
            {"key": "notify_reviewers", "label": "提醒评审人"},
        ],
        "items": [
            {
                "suggestionId": item["id"],
                "title": item["title"],
                "content": item["summary"],
                "confidence": item["confidence"],
                "action": item["action"],
            }
            for item in suggestions
        ],
        "generatedAt": _mock.now_iso(),
    }


def _project_kanban_suggestions(project_id: str | None) -> list[dict[str, Any]]:
    return [
        {
            "suggestionId": "kanban_sug_001",
            "id": "kanban_sug_001",
            "title": "优先处理阻塞任务",
            "content": "建议先处理联调环境参数回灌任务，并通知项目负责人确认资源窗口。",
            "confidence": 0.88,
            "actionKey": "notify_owner",
            "projectId": project_id,
            "affectedTaskIds": ["task_001"],
        },
        {
            "suggestionId": "kanban_sug_002",
            "id": "kanban_sug_002",
            "title": "提前释放评审压力",
            "content": "评审列任务接近完成，可提前提醒 QA 准备验证清单。",
            "confidence": 0.81,
            "actionKey": "notify_reviewers",
            "projectId": project_id,
            "affectedTaskIds": ["task_003"],
        },
    ]


def _column_key_for_status(status: Any) -> str:
    value = str(status or "todo")
    for definition in KANBAN_COLUMN_DEFS:
        if value == definition["columnId"] or value in definition["aliases"]:
            return definition["columnId"]
    return "todo"


def _detail_status_for_column(column_key: str) -> str:
    return DETAIL_STATUS_BY_COLUMN.get(_column_key_for_status(column_key), "pending")


def _priority_value(priority: Any) -> str:
    value = str(priority or "P2")
    lower = value.lower()
    if lower in {"p0", "urgent"}:
        return "P0"
    if lower in {"p1", "high"}:
        return "P1"
    if lower in {"p2", "medium"}:
        return "P2"
    if lower in {"p3", "low"}:
        return "P3"
    return value.upper() if value.lower().startswith("p") else value


def _split_csv(value: str | None) -> list[str]:
    if not isinstance(value, str) or not value or value == "all":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value


def _task_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user.get("id"),
        "name": user.get("name") or user.get("nickname") or user.get("username"),
        "avatar": user.get("avatar"),
        "avatarColor": user.get("avatarColor", "#409eff"),
    }


def _comment_author(user: dict[str, Any]) -> dict[str, Any]:
    author = _task_user(user)
    author["avatarColor"] = user.get("avatarColor", "#67c23a")
    return author


def _user_by_id(user_id: str | None) -> dict[str, Any]:
    users = _mock.users()
    return next((item for item in users if item["id"] == user_id), users[0])


def _date_part(value: Any) -> str | None:
    if not value:
        return None
    return str(value)[:10]


def _safe_date(value: Any) -> date:
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return date.fromisoformat(_mock.today())


def _is_due_this_week(value: Any) -> bool:
    target = _safe_date(value)
    today = date.fromisoformat(_mock.today())
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start <= target <= week_end
