# TODO: 后台管理接口当前为首版联调实现，后续接入 admin service、权限校验、审计记录和真实错误码。
from typing import Any

from fastapi import APIRouter, Body, Query, UploadFile, File

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()


# TODO: 聚合真实后台指标：统计用户/项目/审计日志，读取最近配置变更和权限矩阵，并按 admin:access 校验访问。
@router.get("/overview", summary="后台首页聚合数据")
def get_admin_overview():
    return _mock.api_response(
        {
            "currentUser": _mock.current_user(),
            "unreadCount": len([item for item in _mock.notifications() if not item["read"]]),
            "metrics": [
                {"key": "users", "name": "Users", "value": len(_mock.users()), "trend": 6},
                {"key": "projects", "name": "Projects", "value": len(_mock.projects()), "trend": 3},
                {"key": "audit_logs", "name": "Audit logs", "value": 128, "trend": 12},
            ],
            "roleUsageBars": [
                {"role": "admin", "count": 1},
                {"role": "developer", "count": 1},
                {"role": "qa", "count": 1},
            ],
            "configChangeRows": [
                {"id": "cfg_001", "name": "Audit trail", "value": True, "updatedAt": _mock.now_iso()}
            ],
            "recentAuditItems": audit_items(),
            "platformMatrix": _mock.platform_matrix(),
            "projectMatrix": _mock.project_matrix(),
            "roleTemplateDefaults": _mock.role_templates(),
            "aiSuggestions": _mock.ai_suggestions("admin"),
        }
    )


# TODO: 从 users 表分页查询，支持 keyword/role/status 组合过滤，并补充角色、状态、部门筛选项。
@router.get("/users", summary="用户列表")
def list_admin_users(
    keyword: str | None = Query(default=None),
    role: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    users = _mock.users()
    if keyword:
        lowered = keyword.lower()
        users = [item for item in users if lowered in item["name"].lower() or lowered in item["email"].lower()]
    if role:
        users = [item for item in users if item["platformRole"] == role]
    if status:
        users = [item for item in users if item["status"] == status]
    data = _mock.paged(users, page, pageSize)
    data["filterOptions"] = {
        "roles": ["super_admin", "admin", "pm", "developer", "qa", "product", "collaborator", "user"],
        "statuses": ["pending", "active", "disabled"],
        "departments": ["R&D Center", "Material Science", "Quality Lab"],
    }
    return _mock.api_response(data)


# TODO: 校验邮箱唯一性和角色合法性，写入 users 表，生成初始激活状态并发送邀请/激活通知。
@router.post("/users", summary="创建用户")
def create_admin_user(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "user": {
                "id": _mock.make_id("u"),
                "name": payload.get("name"),
                "email": payload.get("email"),
                "department": payload.get("department"),
                "platformRole": payload.get("platformRole", "user"),
                "status": payload.get("status", "pending"),
                "joinDate": payload.get("joinDate", _mock.today()),
            }
        }
    )


# TODO: 仅允许更新白名单字段，校验邮箱/部门/角色变更规则，并记录修改前后的审计日志。
@router.patch("/users/{userId}", summary="编辑用户资料")
def update_admin_user(userId: str, payload: dict[str, Any] = Body(...)):
    payload["id"] = userId
    payload["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"user": payload})


# TODO: 实现 pending/active/disabled 状态机，停用用户时同步失效会话和项目权限缓存。
@router.patch("/users/{userId}/status", summary="激活/停用用户")
def update_admin_user_status(userId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response({"userId": userId, "status": payload.get("status", "active"), "updatedAt": _mock.now_iso()})


# TODO: 返回真实模板文件或流式下载响应，模板字段需与导入解析器保持一致。
@router.get("/users/import/template", summary="下载导入模板")
def get_user_import_template():
    return _mock.api_response(
        {
            "fileName": "admin-users-import-template.xlsx",
            "downloadUrl": "https://example.com/templates/admin-users-import-template.xlsx",
        }
    )


# TODO: 解析上传 Excel，逐行校验邮箱、角色、部门和重复数据，返回可确认导入的临时批次 ID。
@router.post("/users/import/preview", summary="上传并预览导入")
def preview_user_import(file: UploadFile = File(...)):
    return _mock.api_response(
        {
            "fileName": file.filename,
            "totalCount": 1,
            "rows": [
                {
                    "name": "Zhao Manager",
                    "email": "zhao@example.com",
                    "department": "Product",
                    "platformRole": "user",
                    "platformRoleLabel": "User",
                }
            ],
        }
    )


# TODO: 根据预览批次落库用户数据，跳过无效行并返回创建、更新、失败明细。
@router.post("/users/import/commit", summary="确认导入")
def commit_user_import(payload: dict[str, Any] = Body(...)):
    rows = payload.get("rows", [])
    return _mock.api_response({"createdCount": len(rows), "skippedCount": 0, "fileName": payload.get("fileName")})


# TODO: 汇总管理员待处理事项、权限异常和系统配置风险，调用 AI 服务生成可执行建议。
@ai_router.get("/admin-suggestions", summary="后台 AI 建议")
def get_ai_admin_suggestions():
    return _mock.api_response({"suggestions": _mock.ai_suggestions("admin")})


# TODO: 按 suggestionId 执行建议动作，例如跳转配置、创建审计任务或批量修复权限，并记录采纳结果。
@ai_router.post("/admin-suggestions/{suggestionId}/apply", summary="采纳后台 AI 建议")
def apply_ai_admin_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"suggestionId": suggestionId, "applied": True, "payload": payload or {}})


def audit_items() -> list[dict[str, Any]]:
    return [
        {
            "id": "audit_001",
            "time": _mock.now_iso(),
            "operator": "Zhang Gong",
            "action": "Updated system config",
            "target": "system-config",
            "result": "success",
            "type": "config",
        },
        {
            "id": "audit_002",
            "time": "2026-05-12T18:20:00+08:00",
            "operator": "Chen Siyuan",
            "action": "Created project task",
            "target": "task_002",
            "result": "success",
            "type": "task",
        },
    ]
