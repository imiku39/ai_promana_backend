# TODO: 后台管理接口当前为首版联调实现，后续接入 admin service、权限校验、审计记录和真实错误码。
from typing import Any

from fastapi import APIRouter, Body, Query, UploadFile, File

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()


# TODO: 聚合真实后台指标：统计用户/项目/审计日志，读取最近配置变更和权限矩阵，并按 admin:access 校验访问。
@router.get("/overview", summary="后台首页聚合数据")
def get_admin_overview():
    metrics = [
        {"key": "activeAccounts", "label": "活跃账号数", "name": "活跃账号数", "value": 1284, "status": "正常", "statusType": "success", "trend": 6},
        {"key": "pendingRoleTemplates", "label": "角色模板变更申请", "name": "角色模板变更申请", "value": 12, "status": "待处理", "statusType": "warning", "trend": 3},
        {"key": "abnormalAudits", "label": "异常审计事件", "name": "异常审计事件", "value": 4, "status": "关注", "statusType": "danger", "trend": 1},
        {"key": "aiRuleAdoptionRate", "label": "推荐规则采纳率", "name": "推荐规则采纳率", "value": 67, "unit": "%", "status": "AI", "statusType": "ai", "trend": 8},
    ]
    role_usage = [
        {"roleKey": "pm", "roleName": "PM", "role": "PM", "count": 18, "usageRate": 88},
        {"roleKey": "dev", "roleName": "研发", "role": "研发", "count": 42, "usageRate": 96},
        {"roleKey": "qa", "roleName": "QA", "role": "QA", "count": 15, "usageRate": 72},
    ]
    config_risks = [
        {"key": "permissionChange", "label": "权限变更操作", "riskLevel": "high", "riskRate": 84, "name": "权限变更操作", "value": True, "updatedAt": _mock.now_iso()},
        {"key": "notificationChannel", "label": "通知通道配置", "riskLevel": "medium", "riskRate": 52, "name": "通知通道配置", "value": True, "updatedAt": _mock.now_iso()},
    ]
    recent_audits = [
        {
            "id": item["id"],
            "title": item["action"],
            "description": f"{item['operator']} {item['action']}，对象：{item['target']}。",
            "occurredAt": item["time"],
            "riskLevel": "high" if item["type"] == "config" else "medium",
            **item,
        }
        for item in audit_items()
    ]
    return _mock.api_response(
        {
            "currentUser": _mock.current_user(),
            "unreadCount": len([item for item in _mock.notifications() if not item["read"]]),
            "metrics": metrics,
            "roleUsage": role_usage,
            "roleUsageBars": role_usage,
            "configRisks": config_risks,
            "configChangeRows": config_risks,
            "recentAudits": recent_audits,
            "recentAuditItems": recent_audits,
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
    roleKey: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    sortBy: str | None = Query(default="joinDate"),
    sortOrder: str | None = Query(default="desc"),
):
    keyword = _plain_query_value(keyword)
    selected_role = _plain_query_value(roleKey) or _plain_query_value(role)
    status = _plain_query_value(status)
    page = _plain_query_value(page, 1) or 1
    pageSize = _plain_query_value(pageSize, 20) or 20
    sort_by = _plain_query_value(sortBy, "joinDate") or "joinDate"
    sort_order = _plain_query_value(sortOrder, "desc") or "desc"
    users = [_admin_user_item(item) for item in _mock.users()]
    if keyword:
        lowered = keyword.lower()
        users = [
            item
            for item in users
            if lowered in item["name"].lower()
            or lowered in item["email"].lower()
            or lowered in item["departmentName"].lower()
        ]
    if selected_role:
        users = [item for item in users if item["roleKey"] == selected_role]
    if status:
        users = [item for item in users if item["status"] == status]
    reverse = sort_order != "asc"
    users.sort(key=lambda item: item.get(sort_by) or "", reverse=reverse)
    data = _mock.paged(users, page, pageSize)
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    data["filterOptions"] = _admin_user_options()
    return _mock.api_response(data)


@router.get("/users/options", summary="用户管理选项")
def get_admin_user_options():
    return _mock.api_response(_admin_user_options())


@router.get("/users/create-options", summary="新增用户默认选项")
def get_admin_user_create_options():
    return _mock.api_response(
        {
            **_admin_user_options(),
            "defaultValues": {
                "roleKey": "user",
                "status": "pending",
                "joinDate": _mock.today(),
                "sendInvite": True,
            },
        }
    )


# TODO: 校验邮箱唯一性和角色合法性，写入 users 表，生成初始激活状态并发送邀请/激活通知。
@router.post("/users", summary="创建用户")
def create_admin_user(payload: dict[str, Any] = Body(...)):
    user = _admin_user_from_payload(payload, user_id=_mock.make_id("user"))
    return _mock.api_response(
        {
            "id": user["id"],
            "status": user["status"],
            "inviteSent": bool(payload.get("sendInvite", True)),
            "createdAt": _mock.now_iso(),
            "user": user,
        }
    )


# TODO: 仅允许更新白名单字段，校验邮箱/部门/角色变更规则，并记录修改前后的审计日志。
@router.patch("/users/{userId}", summary="编辑用户资料")
def update_admin_user(userId: str, payload: dict[str, Any] = Body(...)):
    user = _admin_user_from_payload(payload, user_id=userId)
    user["version"] = int(payload.get("version", 1)) + 1
    user["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"user": user})


@router.put("/users/{userId}", summary="更新用户")
def replace_admin_user(userId: str, payload: dict[str, Any] = Body(...)):
    return update_admin_user(userId, payload)


# TODO: 实现 pending/active/disabled 状态机，停用用户时同步失效会话和项目权限缓存。
@router.patch("/users/{userId}/status", summary="激活/停用用户")
def update_admin_user_status(userId: str, payload: dict[str, Any] = Body(...)):
    status = payload.get("status", "active")
    return _mock.api_response(
        {
            "userId": userId,
            "status": status,
            "statusLabel": _status_label(status),
            "updatedAt": _mock.now_iso(),
        }
    )


@router.post("/users/{userId}/activate", summary="激活用户")
def activate_admin_user(userId: str):
    return update_admin_user_status(userId, {"status": "active"})


@router.post("/users/{userId}/disable", summary="停用用户")
def disable_admin_user(userId: str):
    return update_admin_user_status(userId, {"status": "disabled"})


# TODO: 返回真实模板文件或流式下载响应，模板字段需与导入解析器保持一致。
@router.get("/users/import/template", summary="下载导入模板")
def get_user_import_template():
    return _mock.api_response(
        {
            "fileName": "admin-users-import-template.xlsx",
            "downloadUrl": "https://example.com/templates/admin-users-import-template.xlsx",
        }
    )


@router.get("/users/import-template", summary="下载用户导入模板")
def get_user_import_template_compat():
    return get_user_import_template()


# TODO: 解析上传 Excel，逐行校验邮箱、角色、部门和重复数据，返回可确认导入的临时批次 ID。
@router.post("/users/import/preview", summary="上传并预览导入")
def preview_user_import(file: UploadFile = File(...)):
    return _mock.api_response(
        {
            "fileName": file.filename,
            "importTaskId": _mock.make_id("imp"),
            "totalCount": 1,
            "validCount": 1,
            "invalidCount": 0,
            "rows": [
                {
                    "rowNo": 2,
                    "name": "Zhao Manager",
                    "email": "zhao@example.com",
                    "department": "Product",
                    "departmentName": "Product",
                    "roleKey": "user",
                    "platformRole": "user",
                    "platformRoleLabel": "User",
                    "roleLabel": "普通用户",
                    "errors": [],
                }
            ],
        }
    )


# TODO: 根据预览批次落库用户数据，跳过无效行并返回创建、更新、失败明细。
@router.post("/users/import/commit", summary="确认导入")
def commit_user_import(payload: dict[str, Any] = Body(...)):
    rows = payload.get("rows", [])
    created_count = len(rows) if rows else 3
    return _mock.api_response({"createdCount": created_count, "updatedCount": 0, "skippedCount": 0, "failedCount": 0, "fileName": payload.get("fileName")})


@router.post("/users/import/confirm", summary="确认批量导入用户")
def confirm_user_import(payload: dict[str, Any] = Body(...)):
    return commit_user_import(payload)


@router.get("/ai-suggestions", summary="后台 AI 建议")
def get_admin_ai_suggestions():
    return get_ai_admin_suggestions()


@router.post("/ai-suggestions/{suggestionId}/apply", summary="应用 AI 管理建议")
def apply_admin_ai_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return apply_ai_admin_suggestion(suggestionId, payload)


@router.post("/ai-suggestions/{suggestionId}/defer", summary="稍后处理 AI 管理建议")
def defer_admin_ai_suggestion_admin(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"suggestionId": suggestionId, "deferred": True, "payload": payload or {}, "deferredAt": _mock.now_iso()})


# TODO: 汇总管理员待处理事项、权限异常和系统配置风险，调用 AI 服务生成可执行建议。
@ai_router.get("/admin-suggestions", summary="后台 AI 建议")
def get_ai_admin_suggestions():
    return _mock.api_response({"suggestions": _mock.ai_suggestions("admin")})


# TODO: 按 suggestionId 执行建议动作，例如跳转配置、创建审计任务或批量修复权限，并记录采纳结果。
@ai_router.post("/admin-suggestions/{suggestionId}/apply", summary="采纳后台 AI 建议")
def apply_ai_admin_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"suggestionId": suggestionId, "applied": True, "payload": payload or {}})


@ai_router.get("/ai-suggestions", summary="后台 AI 建议兼容")
def get_admin_ai_suggestions_compat():
    return get_ai_admin_suggestions()


@ai_router.post("/ai-suggestions/{suggestionId}/apply", summary="应用 AI 管理建议兼容")
def apply_admin_ai_suggestion_compat(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return apply_ai_admin_suggestion(suggestionId, payload)


@ai_router.post("/ai-suggestions/{suggestionId}/defer", summary="稍后处理 AI 管理建议")
def defer_admin_ai_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"suggestionId": suggestionId, "deferred": True, "payload": payload or {}, "deferredAt": _mock.now_iso()})


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


def _admin_user_item(user: dict[str, Any]) -> dict[str, Any]:
    role_key = user.get("platformRole", "user")
    status = user.get("status", "active")
    return {
        **user,
        "departmentId": user.get("departmentId") or _department_id(user.get("department")),
        "departmentName": user.get("department") or user.get("departmentName") or "未分配",
        "roleKey": role_key,
        "roleLabel": _role_label(role_key),
        "statusLabel": _status_label(status),
        "statusType": _status_type(status),
        "actions": _user_actions(status),
        "version": user.get("version", 1),
    }


def _admin_user_from_payload(payload: dict[str, Any], user_id: str) -> dict[str, Any]:
    role_key = payload.get("roleKey") or payload.get("platformRole") or "user"
    status = payload.get("status", "pending")
    department_name = payload.get("departmentName") or payload.get("department") or "未分配"
    return {
        "id": user_id,
        "name": payload.get("name", "未命名用户"),
        "email": payload.get("email", "user@example.com"),
        "departmentId": payload.get("departmentId") or _department_id(department_name),
        "departmentName": department_name,
        "department": department_name,
        "roleKey": role_key,
        "roleLabel": _role_label(role_key),
        "platformRole": role_key,
        "status": status,
        "statusLabel": _status_label(status),
        "statusType": _status_type(status),
        "joinDate": payload.get("joinDate", _mock.today()),
        "note": payload.get("note"),
        "actions": _user_actions(status),
        "version": int(payload.get("version", 1)),
    }


def _admin_user_options() -> dict[str, Any]:
    return {
        "roles": [
            {"key": "admin", "value": "admin", "label": "管理员"},
            {"key": "user", "value": "user", "label": "普通用户"},
            {"key": "developer", "value": "developer", "label": "研发"},
            {"key": "qa", "value": "qa", "label": "QA"},
        ],
        "statuses": [
            {"key": "active", "value": "active", "label": "正常"},
            {"key": "pending", "value": "pending", "label": "待激活"},
            {"key": "disabled", "value": "disabled", "label": "已停用"},
        ],
        "departments": [
            {"id": "dept_rd", "value": "dept_rd", "label": "R&D Center"},
            {"id": "dept_material", "value": "dept_material", "label": "Material Science"},
            {"id": "dept_quality", "value": "dept_quality", "label": "Quality Lab"},
            {"id": "dept_product", "value": "dept_product", "label": "Product"},
        ],
    }


def _role_label(role_key: str) -> str:
    return {"admin": "管理员", "user": "普通用户", "developer": "研发", "qa": "QA"}.get(role_key, role_key)


def _status_label(status: str) -> str:
    return {"active": "正常", "pending": "待激活", "disabled": "已停用"}.get(status, status)


def _status_type(status: str) -> str:
    return {"active": "success", "pending": "warning", "disabled": "danger"}.get(status, "neutral")


def _department_id(department: str | None) -> str:
    mapping = {"R&D Center": "dept_rd", "Material Science": "dept_material", "Quality Lab": "dept_quality", "Product": "dept_product"}
    return mapping.get(department or "", "dept_unknown")


def _user_actions(status: str) -> list[dict[str, Any]]:
    actions = [{"key": "edit", "label": "编辑", "enabled": True}]
    if status == "disabled":
        actions.append({"key": "activate", "label": "激活", "enabled": True})
    else:
        actions.append({"key": "disable", "label": "停用", "enabled": True})
    return actions


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
