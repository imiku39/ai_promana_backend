# TODO: 项目接口当前为首版联调实现，后续接入项目 service、数据库查询、草稿保存和业务校验。
from typing import Any

from fastapi import APIRouter, Body, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 按当前用户可见项目统计总数、状态、健康度和平均进度，避免统计无权限项目。
@router.get("/summary", summary="项目矩阵头部统计")
def get_projects_summary():
    items = _mock.projects()
    return _mock.api_response(
        {
            "total": len(items),
            "active": len([item for item in items if item["status"] == "active"]),
            "attention": len([item for item in items if item["health"] == "attention"]),
            "risk": len([item for item in items if item["health"] == "risk"]),
            "averageProgress": round(sum(item["progress"] for item in items) / len(items), 1),
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
    items = _mock.projects()
    if keyword:
        lowered = keyword.lower()
        items = [
            item
            for item in items
            if lowered in item["name"].lower() or lowered in item["code"].lower()
        ]
    if status:
        items = [item for item in items if item["status"] == status]
    if health:
        items = [item for item in items if item["health"] == health]
    if ownerId:
        items = [item for item in items if item["ownerId"] == ownerId]
    if tag:
        items = [item for item in items if tag in item.get("tags", [])]
    if sortField and all(sortField in item for item in items):
        items.sort(key=lambda item: item[sortField], reverse=sortOrder == "desc")
    return _mock.api_response(_mock.paged(items, page, pageSize))


# TODO: 从团队、用户、项目模板和页面配置表读取创建项目所需选项，并按 project:create 权限裁剪。
@router.get("/create-options", summary="新建项目弹窗字典")
def get_project_create_options():
    options = _mock.option_items()
    options["templates"] = [
        {"id": item["id"], "label": item["name"], "value": item["id"], "extra": item}
        for item in _mock.project_templates()
    ]
    options["enabledPages"] = [
        {"id": "overview", "label": "Overview", "value": "overview", "extra": {}},
        {"id": "members", "label": "Members", "value": "members", "extra": {}},
        {"id": "kanban", "label": "Kanban", "value": "kanban", "extra": {}},
        {"id": "gantt", "label": "Gantt", "value": "gantt", "extra": {}},
        {"id": "risk", "label": "Risk", "value": "risk", "extra": {}},
        {"id": "reports", "label": "Reports", "value": "reports", "extra": {}},
        {"id": "docs", "label": "Docs", "value": "docs", "extra": {}},
    ]
    return _mock.api_response(options)


# TODO: 将项目创建表单保存到草稿表，支持同一用户覆盖更新未提交草稿。
@router.post("/drafts", summary="保存项目草稿")
def save_project_draft(payload: dict[str, Any] = Body(...)):
    return _mock.api_response({"draftId": _mock.make_id("project_draft"), "savedAt": _mock.now_iso(), "draft": payload})


# TODO: 校验 code 唯一、日期范围、模板和成员有效性，创建项目、成员关系、默认看板和订阅配置。
@router.post("", summary="创建项目")
def create_project(payload: dict[str, Any] = Body(...)):
    project = {
        "id": _mock.make_id("project"),
        "code": payload.get("code", "RD-2026-NEW"),
        "name": payload.get("name", "New Project"),
        "status": payload.get("status", "active"),
        "health": payload.get("health", "good"),
        "progress": payload.get("initialProgress", 0),
        "ownerId": payload.get("ownerId", "u_10001"),
        "teamId": payload.get("teamId", "team_material"),
        "enabledPages": payload.get(
            "enabledPages",
            ["overview", "members", "kanban", "gantt", "risk", "reports", "docs"],
        ),
        "createdAt": _mock.now_iso(),
    }
    return _mock.api_response({"project": project})


# TODO: 查询项目头部信息、启用页签、成员摘要和当前用户项目权限；项目不存在返回 PROJECT_NOT_FOUND。
@router.get("/{projectId}", summary="项目头部信息、可用页签、权限")
def get_project(projectId: str):
    project = _mock.project_lite(projectId)
    return _mock.api_response(
        {
            "project": project,
            "summary": "Current focus is integration validation and schedule risk control.",
            "currentStage": "Integration Validation",
            "enabledTabs": ["overview", "members", "kanban", "gantt", "risk", "reports", "docs"],
            "defaultTab": project.get("defaultView", "overview"),
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
    return _mock.api_response({"project": _mock.project_lite(projectId), "options": _mock.option_items()})


# TODO: 保存项目变更时校验 version、日期范围、成员/订阅人有效性，并同步项目动态。
@router.put("/{projectId}", summary="保存项目变更")
def update_project(projectId: str, payload: dict[str, Any] = Body(...)):
    project = _mock.project_lite(projectId)
    project.update(payload)
    project["id"] = projectId
    project["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"project": project})


# TODO: 保存项目编辑草稿，区分创建草稿和已存在项目编辑草稿，返回可恢复的 draftId。
@router.post("/{projectId}/draft", summary="保存编辑草稿")
def save_project_edit_draft(projectId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response({"projectId": projectId, "draftId": _mock.make_id("project_edit_draft"), "savedAt": _mock.now_iso(), "draft": payload})


# TODO: 归档前校验未完成任务、未关闭风险和权限，执行软归档并禁止后续写操作。
@router.post("/{projectId}/archive", summary="归档项目")
def archive_project(projectId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"projectId": projectId, "status": "archived", "reason": (payload or {}).get("reason"), "archivedAt": _mock.now_iso()})


# TODO: 生成项目排期/任务快照作为基线，保存快照明细并返回 baselineId。
@router.post("/{projectId}/baseline", summary="设置项目基线")
def set_project_baseline(projectId: str, payload: dict[str, Any] = Body(default_factory=dict)):
    return _mock.api_response(
        {
            "baselineId": _mock.make_id("baseline"),
            "projectId": projectId,
            "name": payload.get("name", "Default Baseline"),
            "createdAt": _mock.now_iso(),
        }
    )


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
