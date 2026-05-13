# TODO: 项目模板接口当前为首版联调实现，后续接入模板持久化、启停状态和模板唯一性校验。
from typing import Any

from fastapi import APIRouter, Body

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 从项目模板表查询模板列表、启用状态、默认阶段和可启用页面选项。
@router.get("/project-templates", summary="项目模板列表")
def list_project_templates():
    return _mock.api_response(
        {
            "templates": _mock.project_templates(),
            "pageOptions": ["overview", "members", "kanban", "gantt", "risk", "reports", "docs"],
            "stageOptions": ["Planning", "Validation", "Review", "Launch"],
        }
    )


# TODO: 校验模板名称唯一、页面配置和默认阶段，创建模板并记录创建人。
@router.post("/project-templates", summary="新建项目模板")
def create_project_template(payload: dict[str, Any] = Body(...)):
    payload["id"] = _mock.make_id("project_template")
    payload["createdAt"] = _mock.now_iso()
    return _mock.api_response({"template": payload})


# TODO: 更新模板时校验是否被项目引用，必要时只允许新版本生效而不影响历史项目。
@router.put("/project-templates/{templateId}", summary="编辑项目模板")
def update_project_template(templateId: str, payload: dict[str, Any] = Body(...)):
    payload["id"] = templateId
    payload["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"template": payload})


# TODO: 删除模板前检查项目引用数量，已引用模板应执行停用/归档而非硬删除。
@router.delete("/project-templates/{templateId}", summary="删除项目模板")
def delete_project_template(templateId: str):
    return _mock.api_response({"templateId": templateId, "deleted": True, "deletedAt": _mock.now_iso()})
