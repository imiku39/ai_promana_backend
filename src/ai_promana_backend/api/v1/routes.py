# TODO: `api/v1/endpoints` 是接口标准目录；routes.py 只做聚合挂载和路径分发。
from fastapi import APIRouter
from ai_promana_backend.api.v1.endpoints import (
    admin,
    daily_reports,
    documents,
    logs,
    managments,
    milestones,
    notifications,
    operation_logs,
    pbc,
    project_members,
    projects,
    risks,
    roles_permissions,
    search,
    system_settings,
    tasks,
    teams,
    templates,
    users,
)

router = APIRouter()
api_router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/api/v1")

api_router.include_router(users.auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(daily_reports.dashboard_router, prefix="/dashboard", tags=["工作台"])
api_router.include_router(daily_reports.router, prefix="/ai/daily-report", tags=["AI 日报"])
api_router.include_router(daily_reports.project_router, prefix="/projects", tags=["项目报表"])
api_router.include_router(daily_reports.reports_router, prefix="/reports", tags=["全局报表"])
api_router.include_router(daily_reports.ai_router, prefix="/ai", tags=["AI 报表建议"])
api_router.include_router(search.router, tags=["全局搜索"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目"])
api_router.include_router(projects.ai_router, prefix="/ai", tags=["AI 项目建议"])
api_router.include_router(project_members.router, prefix="/projects", tags=["项目成员"])
api_router.include_router(project_members.ai_router, prefix="/ai", tags=["AI 项目成员建议"])
api_router.include_router(tasks.project_router, prefix="/projects", tags=["项目任务"])
api_router.include_router(milestones.router, prefix="/projects", tags=["项目甘特"])
api_router.include_router(milestones.ai_router, prefix="/ai", tags=["AI 项目排期建议"])
api_router.include_router(risks.router, prefix="/projects", tags=["项目风险"])
api_router.include_router(risks.ai_router, prefix="/ai", tags=["AI 项目风险洞察"])
api_router.include_router(documents.router, prefix="/projects", tags=["项目文档"])
api_router.include_router(documents.ai_router, prefix="/ai", tags=["AI 项目文档建议"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务"])
api_router.include_router(tasks.ai_router, prefix="/ai", tags=["AI 任务建议"])
api_router.include_router(pbc.router, prefix="/workbench", tags=["个人工作台"])
api_router.include_router(pbc.ai_router, prefix="/ai", tags=["AI 工作台建议"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["通知"])
api_router.include_router(notifications.preferences_router, prefix="/notification-preferences", tags=["通知偏好"])
api_router.include_router(notifications.ai_router, prefix="/ai", tags=["AI 通知建议"])
api_router.include_router(system_settings.settings_router, prefix="/settings", tags=["个人设置"])
api_router.include_router(system_settings.admin_router, prefix="/admin", tags=["系统配置"])
api_router.include_router(admin.router, prefix="/admin", tags=["后台管理"])
api_router.include_router(admin.ai_router, prefix="/ai", tags=["AI 后台建议"])
api_router.include_router(roles_permissions.router, prefix="/admin", tags=["角色权限"])
api_router.include_router(templates.router, prefix="/admin", tags=["项目模板"])
api_router.include_router(logs.router, prefix="/admin", tags=["审计日志"])
api_router.include_router(teams.router, prefix="/teams", tags=["团队"])
api_router.include_router(operation_logs.router, prefix="/operation-logs", tags=["操作日志"])
api_router.include_router(managments.router, prefix="/management", tags=["管理选项"])

v1_router.include_router(users.router, prefix="/users", tags=["用户管理"])

router.include_router(api_router)
router.include_router(v1_router)
