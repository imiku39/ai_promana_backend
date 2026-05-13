# TODO: Dashboard、日报和报表接口当前为首版联调实现，后续接入报表服务、AI 服务、导出任务和真实权限。
from typing import Any

from fastapi import APIRouter, Body

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
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "options": {
                "cycles": ["daily", "weekly", "monthly"],
                "metrics": ["progress", "work_hours", "bugs", "block_load"],
            },
            "aiInsight": {
                "summary": "Project progress is healthy, but blocked work is creating short-term schedule pressure.",
                "suggestions": _mock.ai_suggestions("project_report"),
            },
            "burndown": [
                {"date": "2026-05-10", "remaining": 24},
                {"date": "2026-05-11", "remaining": 18},
                {"date": "2026-05-12", "remaining": 15},
            ],
            "workHours": [
                {"memberId": "u_10001", "name": "Zhang Gong", "hours": 38},
                {"memberId": "u_10002", "name": "Chen Siyuan", "hours": 42},
            ],
            "bugs": [{"severity": "high", "count": 1}, {"severity": "medium", "count": 3}],
            "blockLoad": [{"date": "2026-05-12", "count": 1}],
        }
    )


# TODO: 创建项目报表导出任务，记录筛选条件、导出人和 projectId，返回可追踪 taskId。
@project_router.post("/{projectId}/reports/export", summary="导出项目报表")
def export_project_report(projectId: str, payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("project_report_export")
    task["projectId"] = projectId
    task["filters"] = payload or {}
    return _mock.api_response(task)


# TODO: 校验订阅周期和订阅人，保存项目报表订阅，并同步通知偏好或定时任务。
@project_router.post("/{projectId}/reports/subscriptions", summary="订阅报表")
def subscribe_project_report(projectId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "subscriptionId": _mock.make_id("report_subscription"),
            "projectId": projectId,
            "cycle": payload.get("cycle", "weekly"),
            "subscriberIds": payload.get("subscriberIds", []),
            "enabled": payload.get("enabled", True),
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
    return _mock.api_response(
        {
            "projects": _mock.projects(),
            "teams": _mock.option_items()["teams"],
            "members": _mock.users(),
            "cycles": ["daily", "weekly", "monthly"],
            "metrics": ["progress", "work_hours", "bugs", "block_load"],
        }
    )


# TODO: 创建全局报表导出任务，校验 report:export 权限并限制导出范围为当前用户可见数据。
@reports_router.post("/export", summary="导出全局报表")
def export_global_report(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("global_report_export")
    task["filters"] = payload or {}
    return _mock.api_response(task)


# TODO: 将报表异常、趋势变化和用户筛选条件提交给 AI 服务，返回可采纳的分析建议。
@ai_router.get("/report-suggestions", summary="全局报表 AI 建议")
def get_ai_report_suggestions():
    return _mock.api_response({"suggestions": _mock.ai_suggestions("report")})
