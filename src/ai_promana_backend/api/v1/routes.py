from fastapi import APIRouter, Security

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
    system_settings,
    tasks,
    teams,
    templates,
    users,
)
from ai_promana_backend.core.security import require_access_token

router = APIRouter()
public_api_router = APIRouter(prefix="/api")
protected_api_router = APIRouter(prefix="/api", dependencies=[Security(require_access_token)])

public_api_router.include_router(users.auth_router, prefix="/auth", tags=["认证"])

protected_api_router.include_router(users.protected_auth_router, prefix="/auth", tags=["认证"])
protected_api_router.include_router(daily_reports.dashboard_router, prefix="/dashboard", tags=["工作台"])
protected_api_router.include_router(daily_reports.router, prefix="/ai/daily-report", tags=["AI 日报"])
protected_api_router.include_router(daily_reports.project_router, prefix="/projects", tags=["项目报表"])
protected_api_router.include_router(daily_reports.reports_router, prefix="/reports", tags=["全局报表"])
protected_api_router.include_router(daily_reports.ai_router, prefix="/ai", tags=["AI 报表建议"])
protected_api_router.include_router(projects.router, prefix="/projects", tags=["项目"])
protected_api_router.include_router(project_members.router, prefix="/projects", tags=["项目成员"])
protected_api_router.include_router(tasks.project_router, prefix="/projects", tags=["项目任务"])
protected_api_router.include_router(milestones.router, prefix="/projects", tags=["项目甘特"])
protected_api_router.include_router(risks.router, prefix="/projects", tags=["项目风险"])
protected_api_router.include_router(documents.router, prefix="/projects", tags=["项目文档"])
protected_api_router.include_router(tasks.router, prefix="/tasks", tags=["任务"])
protected_api_router.include_router(tasks.ai_router, prefix="/ai", tags=["AI 任务建议"])
protected_api_router.include_router(pbc.router, prefix="/workbench", tags=["个人工作台"])
protected_api_router.include_router(notifications.router, prefix="/notifications", tags=["通知"])
protected_api_router.include_router(notifications.preferences_router, prefix="/notification-preferences", tags=["通知偏好"])
protected_api_router.include_router(notifications.ai_router, prefix="/ai", tags=["AI 通知建议"])
protected_api_router.include_router(system_settings.settings_router, prefix="/settings", tags=["个人设置"])
protected_api_router.include_router(system_settings.admin_router, prefix="/admin", tags=["系统配置"])
protected_api_router.include_router(system_settings.ai_router, prefix="/ai", tags=["AI 设置建议"])
protected_api_router.include_router(admin.router, prefix="/admin", tags=["后台管理"])
protected_api_router.include_router(admin.ai_router, prefix="/ai", tags=["AI 后台建议"])
protected_api_router.include_router(roles_permissions.router, prefix="/admin", tags=["角色权限"])
protected_api_router.include_router(templates.router, prefix="/admin", tags=["项目模板"])
protected_api_router.include_router(logs.router, prefix="/admin", tags=["审计日志"])
protected_api_router.include_router(teams.router, prefix="/teams", tags=["团队"])
protected_api_router.include_router(operation_logs.router, prefix="/operation-logs", tags=["操作日志"])
protected_api_router.include_router(managments.router, prefix="/management", tags=["管理选项"])

router.include_router(public_api_router)
router.include_router(protected_api_router)
