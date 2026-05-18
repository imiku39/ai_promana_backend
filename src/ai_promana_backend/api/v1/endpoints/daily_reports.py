# TODO: Dashboard、日报和报表接口当前为首版联调实现，后续接入报表服务、AI 服务、导出任务和真实权限。
from typing import Any

from fastapi import APIRouter, Body, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
dashboard_router = APIRouter()
project_router = APIRouter()
reports_router = APIRouter()
ai_router = APIRouter()


# TODO: 从任务、项目、通知、日志和 PBC 服务聚合首屏数据，并按当前用户权限过滤不可见项目。
@dashboard_router.get("/overview", summary="Dashboard 首屏聚合数据")
def get_dashboard_overview():
    return _mock.api_response(
        {
            "currentUser": _mock.current_user(),
            "unreadCount": len([item for item in _mock.notifications() if not item["read"]]),
            "greeting": {
                "title": "Good morning",
                "summary": "You have one blocked task and two reports to review.",
                "updatedAt": _mock.now_iso(),
            },
            "kpis": {
                "todoCompletionRate": 78,
                "blockedTaskCount": 1,
                "pbcCompletionRate": 64,
                "activeProjectCount": 2,
            },
            "teamEfficiency": {
                "value": 86,
                "progress": 72,
                "description": "Team delivery is stable with one visible bottleneck.",
                "tags": ["stable", "blocked-task"],
            },
            "todos": _mock.tasks(),
            "activities": [
                {
                    "id": "activity_001",
                    "type": "task",
                    "title": "Task moved to blocked",
                    "content": "Integration environment parameters need confirmation.",
                    "occurredAt": _mock.now_iso(),
                    "targetPath": "/project/project_001/kanban",
                }
            ],
            "projectHealth": [
                {
                    "projectId": item["id"],
                    "projectName": item["name"],
                    "progress": item["progress"],
                    "health": item["health"],
                    "note": "On track" if item["health"] == "good" else "Needs attention",
                }
                for item in _mock.projects()
            ],
            "deliveryConfidence": {"level": "medium", "score": 82},
            "operationMetrics": [
                {"key": "cycle_time", "name": "Cycle Time", "value": 3.6, "unit": "days", "status": "good"},
                {"key": "review_load", "name": "Review Load", "value": 7, "unit": "items", "status": "attention"},
            ],
        }
    )


# TODO: 汇总当天任务、阻塞项和项目进展后调用 AI 生成日报，保存 reportId 供 latest 接口读取。
@router.post("/generate", summary="生成 AI 日报")
def generate_daily_report(payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response(
        {
            "reportId": _mock.make_id("daily_report"),
            "status": "generated",
            "content": "Today focuses on blocked task clearance, report review, and risk mitigation.",
            "generatedAt": _mock.now_iso(),
            "inputs": payload or {},
        }
    )


# TODO: 查询当前用户最近一次 AI 日报，没有日报时返回空状态而不是 mock 内容。
@router.get("/latest", summary="获取最新日报")
def get_latest_daily_report():
    return _mock.api_response(
        {
            "reportId": "daily_report_latest",
            "title": "Daily AI Briefing",
            "content": "One blocked task requires immediate coordination.",
            "generatedAt": _mock.now_iso(),
            "highlights": ["Clear lab schedule", "Review stability report", "Confirm baseline"],
        }
    )


# TODO: 创建晨报导出任务，持久化导出参数，并由异步任务生成可下载文件。
@dashboard_router.post("/morning-report/export", summary="导出晨报")
def export_morning_report(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("morning_report_export")
    task["filters"] = payload or {}
    return _mock.api_response(task)


# TODO: 按 projectId 聚合燃尽、工时、缺陷、阻塞负载和 AI 洞察，校验 project:report:read 权限。
@project_router.get("/{projectId}/reports/page-data", summary="项目报表聚合数据")
def get_project_reports_page(projectId: str):
    overview = _project_report_overview(projectId)
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "options": _project_report_options(projectId),
            **overview,
        }
    )


@project_router.get("/{projectId}/reports/options", summary="项目报表筛选项")
def get_project_report_options(projectId: str):
    return _mock.api_response(_project_report_options(projectId))


@project_router.get("/{projectId}/reports/overview", summary="项目报表总览")
def get_project_report_overview(
    projectId: str,
    period: str | None = Query(default="last_30_days"),
    memberId: str | None = Query(default="all"),
    reportTypes: str | None = Query(default="all"),
):
    return _mock.api_response(
        _project_report_overview(
            projectId,
            period=_plain_query_value(period, "last_30_days"),
            member_id=_plain_query_value(memberId, "all"),
            report_types=_split_csv(_plain_query_value(reportTypes)),
        )
    )


@project_router.get("/{projectId}/reports/ai-insight", summary="项目 AI 报表洞察")
def get_project_report_ai_insight(
    projectId: str,
    period: str | None = Query(default="last_30_days"),
):
    return _mock.api_response(_project_report_ai_insight(projectId, _plain_query_value(period, "last_30_days")))


@project_router.get("/{projectId}/reports/burndown", summary="项目燃尽图")
def get_project_report_burndown(projectId: str, period: str | None = Query(default="last_30_days")):
    return _mock.api_response(_project_report_burndown(projectId, _plain_query_value(period, "last_30_days")))


@project_router.get("/{projectId}/reports/work-hours", summary="项目工时报表")
def get_project_report_work_hours(projectId: str, memberId: str | None = Query(default="all")):
    return _mock.api_response(_project_report_work_hours(projectId, _plain_query_value(memberId, "all")))


@project_router.get("/{projectId}/reports/bugs", summary="项目 Bug 趋势")
def get_project_report_bugs(projectId: str, period: str | None = Query(default="last_30_days")):
    return _mock.api_response(_project_report_bugs(projectId, _plain_query_value(period, "last_30_days")))


@project_router.get("/{projectId}/reports/block-load", summary="项目阻塞与负载")
def get_project_report_block_load(projectId: str):
    return _mock.api_response(_project_report_block_load(projectId))


# TODO: 创建项目报表导出任务，记录筛选条件、导出人和 projectId，返回可追踪 taskId。
@project_router.post("/{projectId}/reports/export", summary="导出项目报表")
def export_project_report(projectId: str, payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("project_report_export")
    task["exportTaskId"] = task["taskId"]
    task["status"] = "processing"
    task["projectId"] = projectId
    task["filters"] = payload or {}
    task["format"] = (payload or {}).get("format", "markdown")
    return _mock.api_response(task)


# TODO: 校验订阅周期和订阅人，保存项目报表订阅，并同步通知偏好或定时任务。
@project_router.post("/{projectId}/reports/subscriptions", summary="订阅报表")
def subscribe_project_report(projectId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "subscriptionId": _mock.make_id("report_subscription"),
            "projectId": projectId,
            "cycle": payload.get("cycle", "weekly"),
            "format": payload.get("format", "markdown"),
            "subscriberIds": payload.get("subscriberIds", []),
            "channels": payload.get("channels", ["in_app"]),
            "enabled": payload.get("enabled", True),
            "nextRunAt": "2026-05-18T09:00:00+08:00",
        }
    )


@reports_router.get("/global/overview", summary="全局报表总览")
def get_global_reports_overview(
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
    projectIds: str | None = Query(default=None),
    departmentIds: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
):
    filters = _global_report_filters(startDate, endDate, projectIds, departmentIds, keyword)
    return _mock.api_response(_global_report_overview(filters))


@reports_router.get("/global/project-health", summary="项目健康度分布")
def get_global_project_health(
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
    projectIds: str | None = Query(default=None),
    departmentIds: str | None = Query(default=None),
    healthStatus: str | None = Query(default=None),
):
    filters = _global_report_filters(startDate, endDate, projectIds, departmentIds, None)
    items = _global_project_health()
    status_value = _plain_query_value(healthStatus)
    if status_value and status_value != "all":
        items = [item for item in items if item["healthStatus"] == status_value]
    project_ids = set(filters["projectIds"])
    if project_ids:
        items = [item for item in items if item["projectId"] in project_ids]
    return _mock.api_response(items)


@reports_router.get("/global/resource-load", summary="成员/资源负载分布")
def get_global_resource_load(
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
    resourceType: str | None = Query(default=None),
    departmentIds: str | None = Query(default=None),
    projectIds: str | None = Query(default=None),
):
    items = _global_resource_load()
    resource_type = _plain_query_value(resourceType)
    if resource_type and resource_type != "all":
        items = [item for item in items if item["resourceType"] == resource_type]
    return _mock.api_response(items)


@reports_router.get("/global/options", summary="全局报表筛选项")
def get_global_reports_options():
    return _mock.api_response(_global_report_options())


@reports_router.post("/global/export", summary="导出全局报表")
def export_global_report_compat(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("global_report_export")
    task["exportTaskId"] = task["taskId"]
    task["status"] = "processing"
    task["filters"] = payload or {}
    task["format"] = (payload or {}).get("format", "csv")
    task["expiresAt"] = None
    return _mock.api_response(task)


@reports_router.post("/global/subscriptions", summary="创建全局报表订阅")
def create_global_report_subscription(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "subscriptionId": _mock.make_id("global_report_sub"),
            "name": payload.get("name", "研发管理周报"),
            "cycle": payload.get("cycle", "weekly_monday"),
            "format": payload.get("format", "markdown"),
            "projectIds": payload.get("projectIds", []),
            "departmentIds": payload.get("departmentIds", []),
            "subscriberIds": payload.get("subscriberIds", []),
            "channels": payload.get("channels", ["in_app"]),
            "enabled": True,
            "nextRunAt": "2026-05-18T09:00:00+08:00",
            "createdAt": _mock.now_iso(),
        }
    )


@reports_router.get("/global/subscriptions", summary="全局报表订阅列表")
def list_global_report_subscriptions():
    return _mock.api_response(
        {
            "list": [
                {
                    "subscriptionId": "global_report_sub_001",
                    "name": "研发管理周报",
                    "cycle": "weekly_monday",
                    "format": "markdown",
                    "enabled": True,
                    "nextRunAt": "2026-05-18T09:00:00+08:00",
                }
            ]
        }
    )


# TODO: 基于全局筛选条件聚合项目趋势、成员排行和风险指标，按用户可见项目裁剪数据。
@reports_router.get("/overview", summary="全局报表聚合")
def get_reports_overview():
    return _mock.api_response(
        {
            "currentUser": _mock.current_user(),
            "unreadCount": len([item for item in _mock.notifications() if not item["read"]]),
            "filters": {
                "projects": _mock.projects(),
                "teams": _mock.option_items()["teams"],
                "cycles": ["daily", "weekly", "monthly"],
                "dateRange": {"start": "2026-05-01", "end": _mock.today()},
            },
            "summaryCards": [
                {"key": "active_projects", "title": "Active projects", "value": 2, "trend": 8},
                {"key": "completion_rate", "title": "Completion rate", "value": 78, "unit": "%", "trend": 4},
                {"key": "blocked_tasks", "title": "Blocked tasks", "value": 1, "trend": -2},
            ],
            "trendCharts": [
                {
                    "key": "progress",
                    "name": "Progress trend",
                    "points": [
                        {"date": "2026-05-10", "value": 69},
                        {"date": "2026-05-11", "value": 71},
                        {"date": "2026-05-12", "value": 72},
                    ],
                }
            ],
            "rankingLists": [
                {
                    "key": "workload",
                    "name": "Workload ranking",
                    "items": [
                        {"id": "u_10002", "name": "Chen Siyuan", "value": 42},
                        {"id": "u_10001", "name": "Zhang Gong", "value": 38},
                    ],
                }
            ],
            "aiInsight": {
                "summary": "Delivery is stable, but review and blocked task load need attention.",
                "suggestions": _mock.ai_suggestions("global_report"),
            },
        }
    )


# TODO: 从项目、团队、成员和报表指标配置表读取筛选项，避免前端写死枚举。
@reports_router.get("/options", summary="报表筛选项")
def get_reports_options():
    return _mock.api_response(_global_report_options())


# TODO: 创建全局报表导出任务，校验 report:export 权限并限制导出范围为当前用户可见数据。
@reports_router.post("/export", summary="导出全局报表")
def export_global_report(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("global_report_export")
    task["exportTaskId"] = task["taskId"]
    task["status"] = "processing"
    task["filters"] = payload or {}
    task["format"] = (payload or {}).get("format", "xlsx")
    return _mock.api_response(task)


# TODO: 将报表异常、趋势变化和用户筛选条件提交给 AI 服务，返回可采纳的分析建议。
@ai_router.get("/report-suggestions", summary="全局报表 AI 建议")
def get_ai_report_suggestions():
    return _mock.api_response({"suggestions": _mock.ai_suggestions("report")})


@ai_router.post("/feedback", summary="AI 反馈")
def submit_ai_feedback(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "feedbackId": _mock.make_id("ai_feedback"),
            "targetId": payload.get("targetId") or payload.get("insightId") or payload.get("suggestionId"),
            "feedback": payload.get("feedback", payload.get("type", "like")),
            "comment": payload.get("comment"),
            "createdAt": _mock.now_iso(),
        }
    )


@ai_router.get("/global-report-suggestions", summary="AI 全局报表建议")
def get_global_report_suggestions(
    context: str | None = Query(default="global_reports"),
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
):
    return _mock.api_response(
        {
            "context": _plain_query_value(context, "global_reports") or "global_reports",
            "card": _global_report_suggestion_card(),
            "relatedProjects": [
                {"projectId": item["id"], "name": item["name"]}
                for item in _mock.projects()[:2]
            ],
            "period": {
                "startDate": _plain_query_value(startDate, "2026-05-04") or "2026-05-04",
                "endDate": _plain_query_value(endDate, _mock.today()) or _mock.today(),
            },
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/global-report-weekly", summary="生成管理周报")
def generate_global_report_weekly(payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    report_format = body.get("format", "markdown")
    return _mock.api_response(
        {
            "reportId": _mock.make_id("weekly_global"),
            "format": report_format,
            "content": "# 研发管理周报\n\n本周团队整体效率提升 9%，但 QA 资源存在跨项目窗口冲突，建议提前锁定验证排期。",
            "downloadUrl": None,
            "filters": body,
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/global-report-suggestions/{suggestionId}/apply", summary="采纳 AI 全局报表建议")
def apply_global_report_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    action_key = body.get("actionKey", "create_resource_reminder")
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "actionKey": action_key,
            "applied": True,
            "createdReminderIds": [_mock.make_id("resource_reminder")] if action_key == "create_resource_reminder" else [],
            "generatedReportId": _mock.make_id("weekly_global") if action_key == "generate_management_weekly" else None,
            "message": "已采纳全局报表建议，并同步管理提醒。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _project_report_options(project_id: str) -> dict[str, Any]:
    return {
        "projectId": project_id,
        "periods": [
            {"value": "last_30_days", "label": "最近 30 天"},
            {"value": "this_week", "label": "本周"},
        ],
        "cycles": ["daily", "weekly", "monthly"],
        "members": [
            {"id": item["id"], "name": item["name"], "label": item["name"], "value": item["id"]}
            for item in _mock.users()
        ],
        "reportTypes": [
            {"value": "progress", "label": "进度报表"},
            {"value": "work_hours", "label": "工时报表"},
            {"value": "quality", "label": "质量报表"},
        ],
        "metrics": ["progress", "work_hours", "bugs", "block_load"],
        "exportFormats": ["markdown", "pdf", "xlsx"],
        "defaultValues": {"period": "last_30_days", "memberId": "all", "reportTypes": ["progress", "work_hours", "quality"]},
    }


def _project_report_overview(
    project_id: str,
    period: str | None = "last_30_days",
    member_id: str | None = "all",
    report_types: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "aiInsight": _project_report_ai_insight(project_id, period),
        "burndown": _project_report_burndown(project_id, period),
        "workHours": _project_report_work_hours(project_id, member_id),
        "bugs": _project_report_bugs(project_id, period),
        "blockLoad": _project_report_block_load(project_id),
        "filters": {
            "period": period or "last_30_days",
            "memberId": member_id or "all",
            "reportTypes": report_types or ["progress", "work_hours", "quality"],
        },
        "updatedAt": _mock.now_iso(),
    }


def _project_report_ai_insight(project_id: str, period: str | None) -> dict[str, Any]:
    return {
        "insightId": "insight_report_001",
        "projectId": project_id,
        "title": "本周团队效率提升 12%，但联调节点仍是唯一主风险源。",
        "content": "AI 综合燃尽图、成员负载与 Bug 趋势后判断：当前项目整体可控。",
        "reportPeriod": {"period": period or "last_30_days", "startDate": "2026-05-01", "endDate": _mock.today()},
        "efficiencyGrowthRate": 12,
        "actions": [
            {"key": "export_markdown", "label": "导出 Markdown"},
            {"key": "feedback_like", "label": "有帮助"},
        ],
        "generatedAt": _mock.now_iso(),
        "summary": "Project progress is healthy, but blocked work is creating short-term schedule pressure.",
        "suggestions": _mock.ai_suggestions("project_report"),
    }


def _project_report_burndown(project_id: str, period: str | None) -> list[dict[str, Any]]:
    return [
        {"date": "2026-05-01", "actualRemaining": 74, "targetRemaining": 78, "unit": "story_point", "projectId": project_id},
        {"date": "2026-05-08", "actualRemaining": 42, "targetRemaining": 46, "unit": "story_point", "projectId": project_id},
        {"date": _mock.today(), "actualRemaining": 18, "targetRemaining": 22, "unit": "story_point", "projectId": project_id},
    ]


def _project_report_work_hours(project_id: str, member_id: str | None) -> list[dict[str, Any]]:
    rows = [
        {"userId": "u_10001", "memberId": "u_10001", "name": "Zhang Gong", "plannedHours": 40, "actualHours": 45, "usageRate": 82, "level": "primary"},
        {"userId": "u_10002", "memberId": "u_10002", "name": "Chen Siyuan", "plannedHours": 38, "actualHours": 42, "usageRate": 88, "level": "warning"},
        {"userId": "u_10003", "memberId": "u_10003", "name": "Wang Yating", "plannedHours": 32, "actualHours": 29, "usageRate": 70, "level": "success"},
    ]
    if member_id and member_id != "all":
        rows = [row for row in rows if row["userId"] == member_id]
    return rows


def _project_report_bugs(project_id: str, period: str | None) -> list[dict[str, Any]]:
    return [
        {"date": "2026-05-01", "createdCount": 4, "closedCount": 2, "criticalOpenCount": 1, "projectId": project_id},
        {"date": "2026-05-08", "createdCount": 3, "closedCount": 4, "criticalOpenCount": 1, "projectId": project_id},
        {"date": _mock.today(), "createdCount": 2, "closedCount": 5, "criticalOpenCount": 0, "projectId": project_id},
    ]


def _project_report_block_load(project_id: str) -> list[dict[str, Any]]:
    return [
        {"label": "联调环境", "value": 78, "displayValue": "31h", "type": "block_hours", "level": "danger", "projectId": project_id},
        {"label": "QA 评审", "value": 62, "displayValue": "18h", "type": "review_load", "level": "warning", "projectId": project_id},
        {"label": "平台支持", "value": 44, "displayValue": "12h", "type": "resource_load", "level": "primary", "projectId": project_id},
    ]


def _global_report_filters(
    start_date: str | None,
    end_date: str | None,
    project_ids: str | None,
    department_ids: str | None,
    keyword: str | None,
) -> dict[str, Any]:
    return {
        "startDate": _plain_query_value(start_date, "2026-05-04") or "2026-05-04",
        "endDate": _plain_query_value(end_date, _mock.today()) or _mock.today(),
        "projectIds": _split_csv(_plain_query_value(project_ids)),
        "departmentIds": _split_csv(_plain_query_value(department_ids)),
        "keyword": _plain_query_value(keyword),
    }


def _global_report_overview(filters: dict[str, Any]) -> dict[str, Any]:
    project_health = _global_project_health()
    resource_load = _global_resource_load()
    keyword = filters.get("keyword")
    if keyword:
        lowered = str(keyword).lower()
        project_health = [item for item in project_health if lowered in item["projectName"].lower()]
        resource_load = [item for item in resource_load if lowered in item["resourceName"].lower()]
    return {
        "currentUser": _mock.current_user(),
        "unreadCount": len([item for item in _mock.notifications() if not item["read"]]),
        "aiInsight": _global_ai_insight(),
        "projectHealth": project_health,
        "resourceLoad": resource_load,
        "summary": {
            "averageHealthScore": round(sum(item["healthScore"] for item in project_health) / max(len(project_health), 1), 1),
            "overloadedResourceCount": len([item for item in resource_load if item["loadLevel"] == "danger"]),
            "reportGeneratedAt": _mock.now_iso(),
        },
        "filters": filters,
    }


def _global_ai_insight() -> dict[str, Any]:
    return {
        "insightId": "insight_global_001",
        "title": "本周团队整体效率提升 9%，但 3 个项目共享同一 QA 资源，存在下周资源冲突风险。",
        "content": "建议从全局层面优先平衡 QA 资源窗口，并提前对联调验证、自动化巡检和协议升级三条线做时间切分。",
        "efficiencyGrowthRate": 9,
        "conflictProjectCount": 3,
        "conflictResource": "QA",
        "generatedAt": _mock.now_iso(),
        "actions": [
            {"key": "generate_management_weekly", "label": "生成管理周报"},
            {"key": "export_csv", "label": "导出 CSV"},
        ],
    }


def _global_project_health() -> list[dict[str, Any]]:
    return [
        {
            "projectId": item["id"],
            "projectName": item["name"],
            "healthScore": 85 if item["health"] == "good" else 58 if item["health"] == "attention" else 72,
            "healthStatus": "good" if item["health"] == "good" else "warning" if item["health"] == "attention" else "danger",
            "ownerId": item.get("ownerId"),
            "departmentId": item.get("teamId"),
            "riskCount": item.get("riskCount", 0),
            "progress": item.get("progress", 0),
        }
        for item in _mock.projects()
    ]


def _global_resource_load() -> list[dict[str, Any]]:
    return [
        {
            "resourceId": "resource_qa",
            "resourceName": "QA 资源",
            "resourceType": "role_group",
            "loadRate": 89,
            "loadLevel": "danger",
            "projectCount": 3,
            "taskCount": 18,
            "conflictWindow": "下周一至周三",
        },
        {
            "resourceId": "team_platform",
            "resourceName": "平台组",
            "resourceType": "team",
            "loadRate": 78,
            "loadLevel": "warning",
            "projectCount": 4,
            "taskCount": 31,
            "conflictWindow": "本周四",
        },
        {
            "resourceId": "u_10002",
            "resourceName": "Chen Siyuan",
            "resourceType": "member",
            "loadRate": 68,
            "loadLevel": "success",
            "projectCount": 2,
            "taskCount": 11,
            "conflictWindow": None,
        },
    ]


def _global_report_options() -> dict[str, Any]:
    return {
        "projects": _mock.projects(),
        "teams": _mock.option_items()["teams"],
        "departments": _mock.option_items()["teams"],
        "members": _mock.users(),
        "cycles": ["daily", "weekly", "monthly"],
        "metrics": ["health", "load", "risk", "progress"],
        "healthStatuses": [
            {"value": "good", "label": "健康"},
            {"value": "warning", "label": "需关注"},
            {"value": "danger", "label": "高风险"},
            {"value": "completed", "label": "已完成"},
        ],
        "resourceTypes": [
            {"value": "role_group", "label": "角色组"},
            {"value": "team", "label": "团队"},
            {"value": "member", "label": "成员"},
        ],
        "exportFormats": ["csv", "xlsx", "pdf", "markdown"],
        "dateRange": {"start": "2026-05-04", "end": _mock.today()},
    }


def _global_report_suggestion_card() -> dict[str, Any]:
    return {
        "suggestionId": "sug_global_report_001",
        "title": "全局建议",
        "content": "建议从下周一开始冻结 QA 的跨项目时段，避免 3 个高优先级项目在同一时间抢占验证资源。",
        "actions": [
            {"key": "generate_management_weekly", "label": "生成管理周报"},
            {"key": "create_resource_reminder", "label": "生成资源提醒"},
        ],
        "confidence": 0.91,
    }


def _split_csv(value: Any) -> list[str]:
    if not isinstance(value, str) or not value or value == "all":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
