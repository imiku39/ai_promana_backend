# TODO: 角色权限接口当前为首版联调实现，后续接入权限矩阵、角色模板持久化和权限校验。
from typing import Any

from fastapi import APIRouter, Body, File, Query, UploadFile

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


PLATFORM_ROLES: list[dict[str, str]] = [
    {"roleKey": "super_admin", "roleName": "超级管理员"},
    {"roleKey": "admin", "roleName": "系统管理员"},
    {"roleKey": "user", "roleName": "普通用户"},
]

PROJECT_ROLES: list[dict[str, str]] = [
    {"roleKey": "owner", "roleName": "项目负责人"},
    {"roleKey": "developer", "roleName": "研发"},
    {"roleKey": "qa", "roleName": "QA"},
    {"roleKey": "product", "roleName": "产品"},
    {"roleKey": "collaborator", "roleName": "协作者"},
]


# TODO: 汇总角色卡片、模板数量和待处理权限变更，接入真实权限 service 后按管理员数据域过滤。
@router.get("/roles/overview", summary="角色管理概览")
def get_roles_overview():
    templates = [_role_template_item(item) for item in _mock.role_templates()]
    return _mock.api_response(
        {
            "cards": [
                {
                    "key": "platformRoles",
                    "title": "平台角色",
                    "description": "超级管理员、系统管理员、普通用户三类平台身份控制后台入口。",
                    "buttonLabel": "查看矩阵",
                    "action": "matrix",
                    "count": len(PLATFORM_ROLES),
                },
                {
                    "key": "projectTemplates",
                    "title": "项目角色模板",
                    "description": "PM、研发、QA、协作者等项目内权限可通过模板复用。",
                    "buttonLabel": "编辑模板",
                    "action": "edit",
                    "count": len(templates),
                },
            ],
            "platformRoleCount": len(PLATFORM_ROLES),
            "projectTemplateCount": len(templates),
            "pendingChangeCount": 2,
            "updatedAt": _mock.now_iso(),
        }
    )


# TODO: 从权限配置表读取摘要权限，用于首屏快速对比平台角色和项目角色模板。
@router.get("/roles/summary-permissions", summary="权限摘要")
def get_summary_permissions():
    rows = [
        {
            "permissionKey": "admin:access",
            "permissionName": "后台入口",
            "platform": {"super_admin": "allow", "admin": "allow", "user": "deny"},
            "project": {"owner": "limited", "developer": "deny", "qa": "deny"},
        },
        {
            "permissionKey": "task:create",
            "permissionName": "创建任务",
            "platform": {"super_admin": "allow", "admin": "allow", "user": "limited"},
            "project": {"owner": "allow", "developer": "allow", "qa": "allow"},
        },
        {
            "permissionKey": "report:export",
            "permissionName": "导出报表",
            "platform": {"super_admin": "allow", "admin": "allow", "user": "deny"},
            "project": {"owner": "allow", "developer": "deny", "qa": "limited"},
        },
    ]
    return _mock.api_response({"list": rows, "rows": rows, "updatedAt": _mock.now_iso()})


# TODO: 从权限配置表读取平台/项目权限矩阵，合并角色继承关系并标记不可编辑系统权限。
@router.get("/permission-matrix", summary="平台/项目权限矩阵")
def get_permission_matrix(matrixType: str | None = Query(default="all")):
    matrix_type = _plain_query_value(matrixType, "all") or "all"
    platform_matrix = _mock.platform_matrix()
    project_matrix = _mock.project_matrix()
    data = {
        "matrixType": matrix_type,
        "platform": _build_matrix("platform", platform_matrix, PLATFORM_ROLES),
        "project": _build_matrix("project", project_matrix, PROJECT_ROLES),
        "platformMatrix": platform_matrix,
        "projectMatrix": project_matrix,
        "roles": [item["roleKey"] for item in PLATFORM_ROLES],
        "projectRoles": [item["roleKey"] for item in PROJECT_ROLES],
        "updatedAt": _mock.now_iso(),
    }
    if matrix_type == "platform":
        data["project"] = {"columns": [], "rows": []}
    elif matrix_type == "project":
        data["platform"] = {"columns": [], "rows": []}
    return _mock.api_response(data)


# TODO: 生成权限矩阵导出任务，包含当前模板、权限说明和导出操作者信息。
@router.post("/permission-matrix/export", summary="导出矩阵")
def export_permission_matrix(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("permission_matrix_export")
    task.update(
        {
            "filters": payload or {},
            "fileName": "permission-matrix.xlsx",
            "message": "权限矩阵导出任务已创建",
            "createdAt": _mock.now_iso(),
        }
    )
    return _mock.api_response(task)


# TODO: 查询角色模板列表、权限矩阵和可选页面/动作，用于角色管理页面初始化。
@router.get("/role-templates", summary="角色模板列表")
def list_role_templates(
    keyword: str | None = Query(default=None),
    scope: str | None = Query(default=None),
    isBuiltin: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=100, ge=1, le=100),
):
    keyword = _plain_query_value(keyword)
    scope = _plain_query_value(scope)
    is_builtin = _plain_query_value(isBuiltin)
    page = _plain_query_value(page, 1) or 1
    page_size = _plain_query_value(pageSize, 100) or 100
    templates = [_role_template_item(item) for item in _mock.role_templates()]
    if keyword:
        lowered = str(keyword).lower()
        templates = [
            item
            for item in templates
            if lowered in item["title"].lower() or lowered in item.get("description", "").lower()
        ]
    if scope and scope != "all":
        templates = [item for item in templates if item["scope"] == scope]
    if is_builtin is not None:
        templates = [item for item in templates if item["isBuiltin"] is bool(is_builtin)]
    data = _mock.paged(templates, int(page), int(page_size))
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    data["templates"] = data["list"]
    data["platformMatrix"] = _mock.platform_matrix()
    data["projectMatrix"] = _mock.project_matrix()
    data.update(_role_template_options())
    return _mock.api_response(data)


@router.get("/role-templates/options", summary="角色模板选项")
def get_role_template_options():
    return _mock.api_response(_role_template_options())


@router.get("/role-templates/export", summary="导出角色模板")
def export_role_templates(
    scope: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
):
    return _mock.api_response(
        {
            **_mock.export_task("role_template_export"),
            "fileName": "role-templates.xlsx",
            "filters": {
                "scope": _plain_query_value(scope),
                "keyword": _plain_query_value(keyword),
            },
        }
    )


@router.post("/role-templates/import", summary="导入角色模板")
def import_role_templates(file: UploadFile = File(...)):
    return _mock.api_response(
        {
            "fileName": file.filename,
            "importTaskId": _mock.make_id("role_template_import"),
            "validCount": 1,
            "invalidCount": 0,
            "rows": [
                {
                    "rowNo": 2,
                    "templateKey": "integration_owner",
                    "title": "联调负责人模板",
                    "errors": [],
                }
            ],
        }
    )


# TODO: 根据 templateId 查询模板详情，包含适用范围、可见页面、动作权限和引用项目数量。
@router.get("/role-templates/{templateId}", summary="角色模板详情")
def get_role_template(templateId: str):
    template = _find_role_template(templateId)
    return _mock.api_response({"template": template, **template})


# TODO: 校验模板名称唯一、scope 合法和权限项有效，创建角色模板并记录创建人。
@router.post("/role-templates", summary="新建角色模板")
def create_role_template(payload: dict[str, Any] = Body(...)):
    template = _role_template_from_payload(payload, _mock.make_id("role_template"))
    template["createdAt"] = _mock.now_iso()
    return _mock.api_response({"template": template, **_role_template_result(template, "created")})


# TODO: 更新模板前检查是否为系统内置模板，处理已引用项目的权限同步策略。
@router.put("/role-templates/{templateId}", summary="更新角色模板")
def update_role_template(templateId: str, payload: dict[str, Any] = Body(...)):
    base = _find_role_template(templateId)
    template = {**base, **_role_template_from_payload(payload, templateId)}
    template["updatedAt"] = _mock.now_iso()
    template["version"] = int(payload.get("version", base.get("version", 1))) + 1
    return _mock.api_response({"template": template, **_role_template_result(template, "updated")})


# TODO: 首页新建模板弹窗可直接基于 sourceTemplateKey 另存为，不一定传路径 templateId。
@router.post("/role-templates/copy", summary="模板另存为")
def copy_role_template_from_payload(payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    source_id = body.get("templateId") or body.get("sourceTemplateId") or body.get("sourceTemplateKey")
    return _copy_role_template(source_id, body)


# TODO: 复制模板时生成新名称，保留权限配置但重置系统内置标识和引用关系。
@router.post("/role-templates/{templateId}/copy", summary="模板另存为")
def copy_role_template(templateId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _copy_role_template(templateId, payload or {})


def _build_matrix(matrix_type: str, raw_rows: list[dict[str, Any]], roles: list[dict[str, str]]) -> dict[str, Any]:
    columns = [
        {
            "key": row["permission"],
            "label": _permission_label(row["permission"]),
            "permissionKey": row["permission"],
        }
        for row in raw_rows
    ]
    rows = []
    for role in roles:
        role_key = role["roleKey"]
        cells = []
        for permission_row in raw_rows:
            allowed = bool(permission_row.get(role_key))
            state = "allow" if allowed else "deny"
            cells.append(
                {
                    "permissionKey": permission_row["permission"],
                    "state": state,
                    "label": "允许" if allowed else "禁止",
                    "icon": "check_circle" if allowed else "block",
                    "scope": "all" if allowed else "none",
                }
            )
        rows.append({**role, "matrixType": matrix_type, "cells": cells})
    return {"columns": columns, "rows": rows}


def _role_template_item(template: dict[str, Any]) -> dict[str, Any]:
    template_id = template.get("templateId") or template.get("id") or _mock.make_id("role_template")
    template_key = template.get("templateKey") or template_id.replace("role_template_", "").replace("tpl_", "")
    visible_modules = template.get("visibleModules") or template.get("visiblePages") or []
    action_permissions = template.get("actionPermissions") or template.get("actions") or []
    return {
        **template,
        "id": template_id,
        "templateId": template_id,
        "templateKey": template_key,
        "title": template.get("title") or template.get("name") or "未命名模板",
        "scope": template.get("scope", "project"),
        "scopeLabel": _scope_label(template.get("scope", "project")),
        "description": template.get("description", ""),
        "visibleModules": visible_modules,
        "visiblePages": visible_modules,
        "actionPermissions": action_permissions,
        "actions": action_permissions,
        "isBuiltin": bool(template.get("isBuiltin", template_id in {"role_template_pm", "role_template_member"})),
        "version": int(template.get("version", 1)),
        "updatedAt": template.get("updatedAt") or _mock.now_iso(),
        "referenceCount": int(template.get("referenceCount", 0 if template_id.endswith("member") else 3)),
    }


def _find_role_template(template_id: str | None) -> dict[str, Any]:
    templates = [_role_template_item(item) for item in _mock.role_templates()]
    if template_id:
        found = next(
            (
                item
                for item in templates
                if item["templateId"] == template_id
                or item["id"] == template_id
                or item["templateKey"] == template_id
            ),
            None,
        )
        if found:
            return found
    return templates[0]


def _role_template_from_payload(payload: dict[str, Any], template_id: str) -> dict[str, Any]:
    template_key = payload.get("templateKey") or payload.get("sourceTemplateKey") or template_id.replace("role_template_", "")
    visible_modules = payload.get("visibleModules") or payload.get("visiblePages") or []
    action_permissions = payload.get("actionPermissions") or payload.get("actions") or []
    return _role_template_item(
        {
            "id": template_id,
            "templateId": template_id,
            "templateKey": template_key,
            "title": payload.get("title", "未命名模板"),
            "scope": payload.get("scope", "project"),
            "description": payload.get("description", ""),
            "visibleModules": visible_modules,
            "actionPermissions": action_permissions,
            "isBuiltin": False,
            "version": int(payload.get("version", 0)) or 1,
        }
    )


def _copy_role_template(template_id: str | None, payload: dict[str, Any]) -> dict[str, Any]:
    source = _find_role_template(template_id)
    copied = {
        **source,
        "id": _mock.make_id("role_template"),
        "templateId": _mock.make_id("role_template"),
        "templateKey": payload.get("templateKey") or f"{source['templateKey']}_copy",
        "title": payload.get("title") or f"{source['title']} 副本",
        "description": payload.get("description", source.get("description", "")),
        "isBuiltin": False,
        "version": 1,
        "sourceTemplateKey": source["templateKey"],
        "createdAt": _mock.now_iso(),
        "updatedAt": _mock.now_iso(),
    }
    return _mock.api_response({"template": copied, **_role_template_result(copied, "copied")})


def _role_template_result(template: dict[str, Any], action: str) -> dict[str, Any]:
    return {
        "templateId": template["templateId"],
        "templateKey": template["templateKey"],
        "version": template["version"],
        "action": action,
        "updatedAt": template.get("updatedAt") or _mock.now_iso(),
        "createdAt": template.get("createdAt"),
    }


def _role_template_options() -> dict[str, Any]:
    visible_modules = [
        {"key": "overview", "value": "overview", "label": "项目详情"},
        {"key": "kanban", "value": "kanban", "label": "项目看板"},
        {"key": "gantt", "value": "gantt", "label": "项目甘特图"},
        {"key": "risk", "value": "risk", "label": "风险看板"},
        {"key": "members", "value": "members", "label": "成员管理"},
        {"key": "reports", "value": "reports", "label": "项目报表"},
        {"key": "docs", "value": "docs", "label": "项目文档"},
        {"key": "admin", "value": "admin", "label": "后台管理"},
    ]
    action_permissions = [
        {"key": "create-task", "value": "create-task", "label": "创建任务"},
        {"key": "assign-owner", "value": "assign-owner", "label": "分配负责人"},
        {"key": "edit-milestone", "value": "edit-milestone", "label": "编辑里程碑"},
        {"key": "set-baseline", "value": "set-baseline", "label": "设置基线"},
        {"key": "drag-gantt", "value": "drag-gantt", "label": "调整甘特图"},
        {"key": "invite-member", "value": "invite-member", "label": "邀请成员"},
        {"key": "export-report", "value": "export-report", "label": "导出报表"},
        {"key": "comment-task", "value": "comment-task", "label": "评论任务"},
    ]
    scopes = [
        {"key": "project", "value": "project", "label": "项目内身份"},
        {"key": "platform", "value": "platform", "label": "平台身份"},
    ]
    return {
        "visibleModules": visible_modules,
        "visiblePageOptions": visible_modules,
        "actionPermissions": action_permissions,
        "actionOptions": action_permissions,
        "scopes": scopes,
    }


def _permission_label(permission: str) -> str:
    labels = {
        "admin:access": "后台入口",
        "project:create": "新建项目",
        "report:export": "导出报表",
        "task:create": "创建任务",
        "task:update": "更新任务",
        "project:baseline": "项目基线",
    }
    return labels.get(permission, permission)


def _scope_label(scope: str) -> str:
    return {"project": "项目内身份", "platform": "平台身份", "org": "组织身份"}.get(scope, scope)


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
