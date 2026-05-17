# TODO: 项目接口当前为首版联调实现，后续接入项目 service、数据库查询、草稿保存和业务校验。
from typing import Any

from fastapi import APIRouter, Body, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()

PROJECT_ENABLED_PAGES = ["overview", "members", "kanban", "gantt", "risk", "reports", "docs"]

STATUS_LABELS = {
    "active": "进行中",
    "in_progress": "进行中",
    "pending": "待启动",
    "paused": "已暂停",
    "completed": "已完成",
    "archived": "已归档",
}

HEALTH_LABELS = {
    "good": "良好",
    "attention": "需关注",
    "risk": "风险",
    "critical": "严重",
    "completed": "完成",
}

COLOR_SEMANTICS = {
    "good": "primary",
    "attention": "warning",
    "risk": "danger",
    "critical": "danger",
    "completed": "success",
}


# TODO: 按当前用户可见项目统计总数、状态、健康度和平均进度，避免统计无权限项目。
@router.get("/summary", summary="项目矩阵头部统计")
def get_projects_summary(
    scope: str | None = Query(default="mine"),
    date: str | None = Query(default=None),
):
    items = _mock.projects()
    members = _mock.members()
    return _mock.api_response(
        {
            "total": len(items),
            "active": len([item for item in items if item["status"] == "active"]),
            "attention": len([item for item in items if item["health"] == "attention"]),
            "risk": len([item for item in items if item["health"] == "risk"]),
            "averageProgress": round(sum(item["progress"] for item in items) / len(items), 1),
            "activeMemberCount": sum(item["memberCount"] for item in items),
            "activeMemberAvatars": [
                {
                    "userId": item["userId"],
                    "name": item["name"],
                    "avatar": item["avatar"],
                }
                for item in members[:5]
            ],
            "rdBudgetAmount": 12400000,
            "rdBudgetDisplay": "¥ 12.4M",
            "rdBudgetTrendRate": 4.2,
            "rdBudgetUsageRate": 60,
            "monthlyNewExperimentCount": 24,
            "patentApplicationTotal": 182,
            "statusDistribution": _count_by(items, "status"),
            "healthDistribution": _count_by(items, "health"),
            "scope": scope or "mine",
            "date": date or _mock.today(),
            "updatedAt": _mock.now_iso(),
        }
    )


# TODO: 使用数据库分页查询项目矩阵，支持 keyword/status/health/owner/tag 和安全排序字段白名单。
@router.get("", summary="项目列表、筛选、排序")
def list_projects(
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    health: str | None = Query(default=None),
    ownerId: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    sortField: str | None = Query(default=None),
    sortOrder: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    items = [_project_list_item(item) for item in _mock.projects()]
    if keyword:
        lowered = keyword.lower()
        items = [
            item
            for item in items
            if lowered in item["name"].lower()
            or lowered in item["code"].lower()
            or lowered in item["owner"]["name"].lower()
        ]
    if status:
        items = [item for item in items if item["status"] == status]
    if health:
        items = [item for item in items if item["health"] == health]
    if ownerId:
        items = [item for item in items if item["owner"]["id"] == ownerId]
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]
    if sortField:
        sort_key = _project_sort_key(sortField)
        items.sort(key=sort_key, reverse=sortOrder == "desc")

    data = _mock.paged(items, page, pageSize)
    data["pagination"] = {
        "page": data["page"],
        "pageSize": data["pageSize"],
        "total": data["total"],
    }
    data["filterOptions"] = {
        "statuses": [{"value": key, "label": value} for key, value in STATUS_LABELS.items()],
        "health": [{"value": key, "label": value} for key, value in HEALTH_LABELS.items()],
        "owners": [
            {"id": item["id"], "name": item["name"], "label": item["name"], "value": item["id"]}
            for item in _mock.users()
        ],
        "tags": sorted({tag for project in items for tag in project.get("tags", [])}),
    }
    return _mock.api_response(data)


# TODO: 从团队、用户、项目模板和页面配置表读取创建项目所需选项，并按 project:create 权限裁剪。
@router.get("/create-options", summary="新建项目弹窗字典")
def get_project_create_options():
    options = _mock.option_items()
    options["teams"] = [
        {
            **item,
            "name": item["label"],
        }
        for item in options["teams"]
    ]
    options["owners"] = [
        {
            **item,
            "name": item["label"],
            "avatar": item.get("extra", {}).get("avatar"),
        }
        for item in options["owners"]
    ]
    options["templates"] = [_project_template_option(item, index == 0) for index, item in enumerate(_mock.project_templates())]
    options["enabledPages"] = [_page_option(page) for page in PROJECT_ENABLED_PAGES]
    options["defaultValues"] = {
        "status": "active",
        "health": "good",
        "priority": "P1",
        "riskSyncEnabled": True,
        "reportSubscriptionCycle": "weekly_monday",
        "defaultView": "overview",
        "riskReminderFrequency": "daily",
        "initMode": "auto_structure",
        "enabledPages": PROJECT_ENABLED_PAGES,
        "initialProgress": 0,
    }
    options["aiSuggestions"] = [
        {
            "id": item["id"],
            "title": item["title"],
            "content": item["summary"],
            "confidence": item["confidence"],
        }
        for item in _mock.ai_suggestions("project_create")
    ]
    return _mock.api_response(options)


# TODO: 将项目创建表单保存到草稿表，支持同一用户覆盖更新未提交草稿。
@router.post("/drafts", summary="保存项目草稿")
def save_project_draft(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "draftId": _mock.make_id("project_draft"),
            "savedAt": _mock.now_iso(),
            "recoverable": True,
            "draft": _normalize_project_payload(payload),
        }
    )


# TODO: 校验 code 唯一、日期范围、模板和成员有效性，创建项目、成员关系、默认看板和订阅配置。
@router.post("", summary="创建项目")
def create_project(payload: dict[str, Any] = Body(...)):
    project = _project_from_payload(payload)
    return _mock.api_response(
        {
            "projectId": project["id"],
            "name": project["name"],
            "code": project["code"],
            "status": project["status"],
            "targetPath": project["detailPath"],
            "project": project,
        }
    )


# TODO: 查询项目头部信息、启用页签、成员摘要和当前用户项目权限；项目不存在返回 PROJECT_NOT_FOUND。
@router.get("/{projectId}", summary="项目头部信息、可用页签、权限")
def get_project(projectId: str):
    project = _project_list_item(_mock.project_lite(projectId))
    return _mock.api_response(
        {
            "project": project,
            "projectId": project["id"],
            "summary": project.get("summary", "当前阶段集中处理联调验证中的时间偏差。"),
            "currentStage": "Integration Validation",
            "enabledPages": project["enabledPages"],
            "enabledTabs": project["enabledPages"],
            "targetPath": project["detailPath"],
            "defaultTab": project.get("defaultView", "overview"),
            "defaultView": project.get("defaultView", "overview"),
            "permissions": [
                "project:read",
                "project:update",
                "task:create",
                "task:update",
                "project:member:update",
            ],
            "membersBrief": [
                {
                    "id": item["userId"],
                    "name": item["name"],
                    "avatar": item["avatar"],
                    "role": item["role"],
                }
                for item in _mock.members()
            ],
        }
    )


# TODO: 聚合概览页所有卡片数据，拆分调用里程碑、任务、成员负载、风险、报表和文档服务。
@router.get("/{projectId}/overview", summary="项目概览页聚合数据")
def get_project_overview(projectId: str):
    project = _mock.project_lite(projectId)
    return _mock.api_response(
        {
            "milestones": [
                {"id": "ms_001", "title": "Planning complete", "date": "2026-04-20", "status": "completed"},
                {"id": "ms_002", "title": "Integration validation", "date": "2026-05-15", "status": "active"},
            ],
            "weekTasks": _mock.tasks(projectId),
            "loads": [{"memberId": item["userId"], "name": item["name"], "workload": item["workload"]} for item in _mock.members()],
            "memberList": _mock.members(),
            "heatmap": [
                {"memberId": "u_10001", "day": "2026-05-12", "value": 6},
                {"memberId": "u_10002", "day": "2026-05-12", "value": 8},
            ],
            "kanbanPreview": {"columns": kanban_columns(projectId), "total": len(_mock.tasks(projectId))},
            "flowRules": flow_rules(),
            "ganttPreview": {
                "timeline": {"start": project["startDate"], "end": project["endDate"], "unit": "day"},
                "items": gantt_items(projectId),
            },
            "riskInsights": {"count": len(_mock.risks()), "level": "attention", "items": _mock.risks()},
            "riskTasks": [task for task in _mock.tasks(projectId) if task["status"] == "blocked"],
            "reportsPreview": {"progress": project["progress"], "confidence": 82, "updatedAt": _mock.now_iso()},
            "docList": _mock.documents(),
            "aiDrawer": {"summary": "AI suggests clearing the blocked integration task first.", "suggestions": _mock.ai_suggestions("project")},
        }
    )


# TODO: 读取项目编辑表单初始值和可选字典，带出 version 用于后续乐观锁更新。
@router.get("/{projectId}/edit-form", summary="编辑弹窗初始化")
def get_project_edit_form(projectId: str):
    return _mock.api_response(
        {
            "project": _project_list_item(_mock.project_lite(projectId)),
            "options": get_project_create_options()["data"],
            "version": 1,
        }
    )


# TODO: 保存项目变更时校验 version、日期范围、成员/订阅人有效性，并同步项目动态。
@router.put("/{projectId}", summary="保存项目变更")
def update_project(projectId: str, payload: dict[str, Any] = Body(...)):
    project = _project_list_item(_mock.project_lite(projectId))
    project.update(_normalize_project_payload(payload))
    project["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"project": project})


# TODO: 保存项目编辑草稿，区分创建草稿和已存在项目编辑草稿，返回可恢复的 draftId。
@router.post("/{projectId}/draft", summary="保存编辑草稿")
def save_project_edit_draft(projectId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "projectId": projectId,
            "draftId": _mock.make_id("project_edit_draft"),
            "savedAt": _mock.now_iso(),
            "recoverable": True,
            "draft": _normalize_project_payload(payload),
        }
    )


# TODO: 归档前校验未完成任务、未关闭风险和权限，执行软归档并禁止后续写操作。
@router.post("/{projectId}/archive", summary="归档项目")
def archive_project(projectId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response(
        {
            "projectId": projectId,
            "status": "archived",
            "statusLabel": STATUS_LABELS["archived"],
            "reason": (payload or {}).get("reason"),
            "targetPath": "/projects",
            "archivedAt": _mock.now_iso(),
        }
    )


# TODO: 生成项目排期/任务快照作为基线，保存快照明细并返回 baselineId。
@router.post("/{projectId}/baseline", summary="设置项目基线")
def set_project_baseline(projectId: str, payload: dict[str, Any] = Body(default_factory=dict)):
    return _mock.api_response(
        {
            "baselineId": _mock.make_id("baseline"),
            "projectId": projectId,
            "name": payload.get("name", "Default Baseline"),
            "status": "active",
            "createdAt": _mock.now_iso(),
        }
    )


@ai_router.get("/project-matrix-suggestions", summary="AI 项目矩阵建议")
def get_project_matrix_suggestions(context: str | None = Query(default="projects")):
    suggestions = _mock.ai_suggestions("project")
    primary = suggestions[0]
    secondary = suggestions[1:]
    return _mock.api_response(
        {
            "context": context or "projects",
            "primarySuggestion": {
                "id": primary["id"],
                "title": primary["title"],
                "content": primary["summary"],
                "confidence": primary["confidence"],
                "actions": [
                    {"key": "apply", "label": "一键采纳"},
                    {"key": "view_project", "label": "查看项目"},
                ],
            },
            "items": [
                {
                    "id": item["id"],
                    "title": item["title"],
                    "description": item["summary"],
                    "confidence": item["confidence"],
                }
                for item in secondary
            ],
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/project-suggestions/{suggestionId}/apply", summary="采纳 AI 项目建议")
def apply_project_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "actionKey": body.get("actionKey", "apply"),
            "projectIds": body.get("projectIds", []),
            "applied": True,
            "resultMessage": "已生成项目矩阵优化建议，并同步到项目提醒队列。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _count_by(items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    counters: dict[str, int] = {}
    for item in items:
        value = str(item.get(field) or "unknown")
        counters[value] = counters.get(value, 0) + 1
    return [{"key": key, "count": count} for key, count in counters.items()]


def _project_list_item(project: dict[str, Any]) -> dict[str, Any]:
    status = project.get("status", "active")
    health = project.get("health", "good")
    enabled_pages = project.get("enabledPages") or PROJECT_ENABLED_PAGES
    deadline = project.get("deadline") or project.get("endDate")
    owner_id = project.get("ownerId", "u_10001")
    owner_name = project.get("ownerName", "Zhang Gong")
    owner_avatar = project.get("ownerAvatar")
    item = {
        **project,
        "department": project.get("department") or project.get("teamName"),
        "healthLabel": HEALTH_LABELS.get(health, health),
        "statusLabel": STATUS_LABELS.get(status, status),
        "owner": {
            "id": owner_id,
            "name": owner_name,
            "avatar": owner_avatar,
        },
        "deadline": deadline,
        "colorSemantic": COLOR_SEMANTICS.get(health, "neutral"),
        "detailPath": f"/project/{project['id']}",
        "enabledPages": enabled_pages,
        "defaultView": project.get("defaultView", "overview"),
        "weight": _project_weight(project),
        "updatedAt": project.get("updatedAt") or _mock.now_iso(),
    }
    return item


def _project_weight(project: dict[str, Any]) -> int:
    health_weight = {"critical": 40, "risk": 30, "attention": 20, "good": 10, "completed": 0}
    return health_weight.get(project.get("health"), 10) + int(project.get("riskCount", 0)) * 3 + max(0, 100 - int(project.get("progress", 0))) // 10


def _project_sort_key(sort_field: str):
    if sort_field == "owner":
        return lambda item: item["owner"]["name"]
    if sort_field == "deadline":
        return lambda item: item.get("deadline") or ""
    if sort_field == "weight":
        return lambda item: item.get("weight", 0)
    if sort_field == "health":
        order = {"critical": 4, "risk": 3, "attention": 2, "good": 1, "completed": 0}
        return lambda item: order.get(item.get("health"), 0)
    return lambda item: item.get(sort_field) or ""


def _project_template_option(template: dict[str, Any], recommended: bool) -> dict[str, Any]:
    return {
        "id": template["id"],
        "name": template["name"],
        "label": template["name"],
        "value": template["id"],
        "description": template.get("description"),
        "recommended": recommended,
        "enabledPages": template.get("enabledPages", PROJECT_ENABLED_PAGES),
        "defaultStages": template.get("defaultStages", []),
        "active": template.get("active", True),
        "extra": template,
    }


def _page_option(page: str) -> dict[str, Any]:
    labels = {
        "overview": "概览",
        "members": "成员",
        "kanban": "看板",
        "gantt": "甘特",
        "risk": "风险",
        "reports": "报表",
        "docs": "文档",
    }
    return {"id": page, "label": labels.get(page, page), "value": page, "extra": {}}


def _normalize_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = payload.copy()
    if "deadline" not in normalized and "endDate" in normalized:
        normalized["deadline"] = normalized["endDate"]
    if "endDate" not in normalized and "deadline" in normalized:
        normalized["endDate"] = normalized["deadline"]
    normalized.setdefault("status", "active")
    normalized.setdefault("health", "good")
    normalized.setdefault("initialProgress", 0)
    normalized.setdefault("enabledPages", PROJECT_ENABLED_PAGES)
    normalized.setdefault("defaultView", "overview")
    normalized.setdefault("riskSyncEnabled", True)
    normalized.setdefault("reportSubscriptionCycle", "weekly_monday")
    normalized.setdefault("riskReminderFrequency", "daily")
    normalized.setdefault("initMode", "auto_structure")
    return normalized


def _project_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_project_payload(payload)
    owner = next((item for item in _mock.users() if item["id"] == normalized.get("ownerId")), _mock.users()[0])
    team_options = _mock.option_items()["teams"]
    team = next((item for item in team_options if item["id"] == normalized.get("teamId")), team_options[0])
    project_id = _mock.make_id("project")
    project = {
        "id": project_id,
        "code": normalized.get("code", f"RD-{_mock.today().replace('-', '')}-NEW"),
        "name": normalized.get("name", "New Project"),
        "status": normalized["status"],
        "health": normalized["health"],
        "progress": normalized["initialProgress"],
        "ownerId": owner["id"],
        "ownerName": owner["name"],
        "teamId": team["id"],
        "teamName": team["label"],
        "department": team["label"],
        "memberCount": normalized.get("estimatedMemberCount", len(normalized.get("memberIds", [])) or 1),
        "startDate": normalized.get("startDate", _mock.today()),
        "endDate": normalized.get("endDate"),
        "deadline": normalized.get("deadline"),
        "tags": normalized.get("tags", []),
        "ownerAvatar": owner.get("avatar"),
        "activeMemberAvatars": [owner.get("avatar")] if owner.get("avatar") else [],
        "templateName": normalized.get("templateId", "custom_template"),
        "riskCount": 0,
        "defaultView": normalized["defaultView"],
        "enabledPages": normalized["enabledPages"],
        "summary": normalized.get("summary", ""),
        "priority": normalized.get("priority", "P1"),
        "createdAt": _mock.now_iso(),
    }
    return _project_list_item(project)


def kanban_columns(project_id: str) -> list[dict[str, Any]]:
    statuses = [
        ("todo", "pending", "To Do"),
        ("doing", "in_progress", "Doing"),
        ("review", "review", "Review"),
        ("done", "completed", "Done"),
        ("blocked", "blocked", "Blocked"),
    ]
    project_tasks = _mock.tasks(project_id)
    return [
        {
            "key": column_key,
            "title": title,
            "status": status,
            "tasks": [task for task in project_tasks if task["status"] == status],
        }
        for column_key, status, title in statuses
    ]


def flow_rules() -> list[dict[str, Any]]:
    return [
        {"from": "pending", "to": "in_progress", "requiresReason": False},
        {"from": "in_progress", "to": "review", "requiresReason": False},
        {"from": "review", "to": "completed", "requiresReason": False},
        {"from": "*", "to": "blocked", "requiresReason": True},
    ]


def gantt_items(project_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": task["id"],
            "title": task["title"],
            "type": "task",
            "startDate": task["startDate"],
            "endDate": task["dueAt"][:10],
            "progress": task["progress"],
            "ownerName": task["assigneeName"],
        }
        for task in _mock.tasks(project_id)
    ]
