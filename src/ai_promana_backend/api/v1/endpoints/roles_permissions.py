# TODO: 角色权限接口当前为首版联调实现，后续接入权限矩阵、角色模板持久化和权限校验。
from typing import Any

from fastapi import APIRouter, Body

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 从权限配置表读取平台/项目权限矩阵，合并角色继承关系并标记不可编辑系统权限。
@router.get("/permission-matrix", summary="平台/项目权限矩阵")
def get_permission_matrix():
    return _mock.api_response(
        {
            "platformMatrix": _mock.platform_matrix(),
            "projectMatrix": _mock.project_matrix(),
            "roles": ["super_admin", "admin", "pm", "developer", "qa", "product", "collaborator", "user"],
            "projectRoles": ["owner", "developer", "qa", "product", "collaborator"],
        }
    )


# TODO: 生成权限矩阵导出任务，包含当前模板、权限说明和导出操作者信息。
@router.post("/permission-matrix/export", summary="导出矩阵")
def export_permission_matrix(payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("permission_matrix_export")
    task["filters"] = payload or {}
    return _mock.api_response(task)


# TODO: 查询角色模板列表、权限矩阵和可选页面/动作，用于角色管理页面初始化。
@router.get("/role-templates", summary="角色模板列表")
def list_role_templates():
    return _mock.api_response(
        {
            "templates": _mock.role_templates(),
            "platformMatrix": _mock.platform_matrix(),
            "projectMatrix": _mock.project_matrix(),
            "visiblePageOptions": [
                {"label": "Overview", "value": "overview"},
                {"label": "Kanban", "value": "kanban"},
                {"label": "Gantt", "value": "gantt"},
                {"label": "Risk", "value": "risk"},
                {"label": "Members", "value": "members"},
                {"label": "Reports", "value": "reports"},
                {"label": "Docs", "value": "docs"},
            ],
            "actionOptions": [
                {"label": "Create task", "value": "create-task"},
                {"label": "Assign owner", "value": "assign-owner"},
                {"label": "Edit milestone", "value": "edit-milestone"},
                {"label": "Set baseline", "value": "set-baseline"},
                {"label": "Drag gantt", "value": "drag-gantt"},
                {"label": "Invite member", "value": "invite-member"},
                {"label": "Export report", "value": "export-report"},
            ],
        }
    )


# TODO: 根据 templateId 查询模板详情，包含适用范围、可见页面、动作权限和引用项目数量。
@router.get("/role-templates/{templateId}", summary="角色模板详情")
def get_role_template(templateId: str):
    template = next((item for item in _mock.role_templates() if item["id"] == templateId), _mock.role_templates()[0])
    template["id"] = templateId
    return _mock.api_response({"template": template})


# TODO: 校验模板名称唯一、scope 合法和权限项有效，创建角色模板并记录创建人。
@router.post("/role-templates", summary="新建角色模板")
def create_role_template(payload: dict[str, Any] = Body(...)):
    payload["id"] = _mock.make_id("role_template")
    payload["createdAt"] = _mock.now_iso()
    return _mock.api_response({"template": payload})


# TODO: 更新模板前检查是否为系统内置模板，处理已引用项目的权限同步策略。
@router.put("/role-templates/{templateId}", summary="更新角色模板")
def update_role_template(templateId: str, payload: dict[str, Any] = Body(...)):
    payload["id"] = templateId
    payload["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"template": payload})


# TODO: 复制模板时生成新名称，保留权限配置但重置系统内置标识和引用关系。
@router.post("/role-templates/{templateId}/copy", summary="模板另存为")
def copy_role_template(templateId: str, payload: dict[str, Any] | None = Body(default=None)):
    copied = next((item for item in _mock.role_templates() if item["id"] == templateId), _mock.role_templates()[0])
    copied["id"] = _mock.make_id("role_template")
    copied["title"] = (payload or {}).get("title", f"{copied['title']} Copy")
    copied["createdAt"] = _mock.now_iso()
    return _mock.api_response({"template": copied})
