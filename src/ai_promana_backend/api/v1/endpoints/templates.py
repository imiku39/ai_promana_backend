# TODO: 项目模板接口当前为首版联调实现，后续接入模板持久化、启停状态和模板唯一性校验。
from typing import Any

from fastapi import APIRouter, Body, File, Query, UploadFile

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 从项目模板表查询模板列表、启用状态、默认阶段和可启用页面选项。
@router.get("/project-templates", summary="项目模板列表")
def list_project_templates(
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    sortBy: str | None = Query(default="createTime"),
    sortOrder: str | None = Query(default="desc"),
):
    keyword = _plain_query_value(keyword)
    status = _plain_query_value(status)
    page = _plain_query_value(page, 1) or 1
    page_size = _plain_query_value(pageSize, 20) or 20
    sort_by = _plain_query_value(sortBy, "createTime") or "createTime"
    sort_order = _plain_query_value(sortOrder, "desc") or "desc"
    templates = [_project_template_item(item) for item in _mock.project_templates()]
    if keyword:
        lowered = str(keyword).lower()
        templates = [
            item
            for item in templates
            if lowered in item["name"].lower() or lowered in item.get("description", "").lower()
        ]
    if status and status != "all":
        templates = [item for item in templates if item["status"] == status]
    templates.sort(key=lambda item: item.get(sort_by) or "", reverse=sort_order != "asc")
    data = _mock.paged(templates, int(page), int(page_size))
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    data["templates"] = data["list"]
    data.update(_project_template_options())
    return _mock.api_response(data)


@router.get("/project-templates/options", summary="项目模板配置选项")
def get_project_template_options():
    return _mock.api_response(_project_template_options())


@router.get("/project-templates/export", summary="导出项目模板")
def export_project_templates(
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    return _mock.api_response(
        {
            **_mock.export_task("project_template_export"),
            "fileName": "project-templates.xlsx",
            "filters": {
                "keyword": _plain_query_value(keyword),
                "status": _plain_query_value(status),
            },
        }
    )


@router.post("/project-templates/import", summary="导入项目模板")
def import_project_templates(file: UploadFile = File(...)):
    return _mock.api_response(
        {
            "fileName": file.filename,
            "importTaskId": _mock.make_id("project_template_import"),
            "validCount": 1,
            "invalidCount": 0,
            "rows": [
                {
                    "rowNo": 2,
                    "name": "联调项目模板",
                    "milestoneCount": 4,
                    "errors": [],
                }
            ],
        }
    )


@router.get("/project-templates/{templateId}/delete-check", summary="项目模板删除影响校验")
def check_project_template_delete(templateId: str):
    template = _find_project_template(templateId)
    used_count = int(template.get("usedProjectCount", 0))
    can_delete = used_count == 0
    return _mock.api_response(
        {
            "templateId": templateId,
            "canDelete": can_delete,
            "usedProjectCount": used_count,
            "message": "当前模板可删除。" if can_delete else f"当前模板已被 {used_count} 个项目使用，建议停用而不是删除。",
        }
    )


@router.get("/project-templates/{templateId}", summary="项目模板详情")
def get_project_template(templateId: str):
    template = _find_project_template(templateId)
    return _mock.api_response({"template": template, **template})


# TODO: 校验模板名称唯一、页面配置和默认阶段，创建模板并记录创建人。
@router.post("/project-templates", summary="新建项目模板")
def create_project_template(payload: dict[str, Any] = Body(...)):
    template = _project_template_from_payload(payload, _mock.make_id("project_template"))
    template["createdAt"] = _mock.now_iso()
    template["createTime"] = _mock.today()
    return _mock.api_response({"template": template, **_project_template_result(template, "created")})


# TODO: 更新模板时校验是否被项目引用，必要时只允许新版本生效而不影响历史项目。
@router.put("/project-templates/{templateId}", summary="编辑项目模板")
def update_project_template(templateId: str, payload: dict[str, Any] = Body(...)):
    base = _find_project_template(templateId)
    template = {**base, **_project_template_from_payload(payload, templateId)}
    template["updatedAt"] = _mock.now_iso()
    template["version"] = int(payload.get("version", base.get("version", 1))) + 1
    return _mock.api_response({"template": template, **_project_template_result(template, "updated")})


# TODO: 删除模板前检查项目引用数量，已引用模板应执行停用/归档而非硬删除。
@router.delete("/project-templates/{templateId}", summary="删除项目模板")
def delete_project_template(templateId: str):
    check = check_project_template_delete(templateId)["data"]
    return _mock.api_response(
        {
            "templateId": templateId,
            "deleted": bool(check["canDelete"]),
            "archived": not bool(check["canDelete"]),
            "usedProjectCount": check["usedProjectCount"],
            "deletedAt": _mock.now_iso(),
            "message": "模板已删除。" if check["canDelete"] else "模板已被项目使用，已模拟归档处理。",
        }
    )


def _project_template_item(template: dict[str, Any]) -> dict[str, Any]:
    template_id = template.get("id") or template.get("templateId") or _mock.make_id("project_template")
    stages = template.get("defaultStages") or [item.get("name") for item in template.get("milestones", [])] or []
    milestones = template.get("milestones") or _milestones_from_stages(stages)
    enabled_pages = template.get("enabledPages") or template.get("pageKeys") or []
    status = template.get("status") or ("enabled" if template.get("active", True) else "disabled")
    return {
        **template,
        "id": template_id,
        "templateId": template_id,
        "name": template.get("name", "未命名项目模板"),
        "description": template.get("description", ""),
        "enabledPages": enabled_pages,
        "pageKeys": enabled_pages,
        "defaultStages": stages,
        "milestones": milestones,
        "milestoneCount": int(template.get("milestoneCount", len(milestones))),
        "createTime": template.get("createTime") or template.get("createdAt") or "2026-04-01",
        "creatorId": template.get("creatorId", "u_10001"),
        "creatorName": template.get("creatorName", "系统管理员"),
        "status": status,
        "statusLabel": _status_label(status),
        "active": status == "enabled",
        "usedProjectCount": int(template.get("usedProjectCount", 12 if template_id.endswith("requirement_iteration") else 0)),
        "version": int(template.get("version", 1)),
        "defaultRoleTemplateIds": template.get("defaultRoleTemplateIds", ["role_template_pm"]),
        "taskPresets": template.get("taskPresets", []),
    }


def _find_project_template(template_id: str) -> dict[str, Any]:
    templates = [_project_template_item(item) for item in _mock.project_templates()]
    found = next((item for item in templates if item["id"] == template_id or item["templateId"] == template_id), None)
    if found:
        return found
    template = templates[0]
    template["id"] = template_id
    template["templateId"] = template_id
    return template


def _project_template_from_payload(payload: dict[str, Any], template_id: str) -> dict[str, Any]:
    milestones = payload.get("milestones") or _milestones_from_stages(payload.get("defaultStages") or [])
    return _project_template_item(
        {
            "id": template_id,
            "name": payload.get("name", "未命名项目模板"),
            "description": payload.get("description", ""),
            "milestones": milestones,
            "defaultStages": payload.get("defaultStages") or [item.get("name") for item in milestones],
            "enabledPages": payload.get("enabledPages") or payload.get("pageKeys") or [],
            "defaultRoleTemplateIds": payload.get("defaultRoleTemplateIds", []),
            "status": payload.get("status", "enabled"),
            "version": int(payload.get("version", 0)) or 1,
            "usedProjectCount": int(payload.get("usedProjectCount", 0)),
        }
    )


def _project_template_result(template: dict[str, Any], action: str) -> dict[str, Any]:
    return {
        "id": template["id"],
        "templateId": template["templateId"],
        "version": template["version"],
        "action": action,
        "createdAt": template.get("createdAt"),
        "updatedAt": template.get("updatedAt") or _mock.now_iso(),
    }


def _project_template_options() -> dict[str, Any]:
    page_options = [
        {"key": "overview", "value": "overview", "label": "项目详情"},
        {"key": "members", "value": "members", "label": "成员管理"},
        {"key": "kanban", "value": "kanban", "label": "项目看板"},
        {"key": "gantt", "value": "gantt", "label": "项目甘特图"},
        {"key": "risk", "value": "risk", "label": "风险看板"},
        {"key": "reports", "value": "reports", "label": "项目报表"},
        {"key": "docs", "value": "docs", "label": "项目文档"},
    ]
    stage_options = [
        {"key": "planning", "value": "Planning", "label": "规划"},
        {"key": "validation", "value": "Validation", "label": "验证"},
        {"key": "review", "value": "Review", "label": "评审"},
        {"key": "launch", "value": "Launch", "label": "上线"},
    ]
    status_options = [
        {"key": "enabled", "value": "enabled", "label": "启用"},
        {"key": "disabled", "value": "disabled", "label": "停用"},
        {"key": "archived", "value": "archived", "label": "已归档"},
    ]
    return {
        "pageOptions": page_options,
        "stageOptions": stage_options,
        "statusOptions": status_options,
        "roleTemplateOptions": [
            {"key": "role_template_pm", "value": "role_template_pm", "label": "PM 模板"},
            {"key": "role_template_member", "value": "role_template_member", "label": "成员模板"},
        ],
    }


def _milestones_from_stages(stages: list[Any]) -> list[dict[str, Any]]:
    names = [str(item) for item in stages] or ["Planning", "Validation", "Review"]
    return [
        {
            "id": f"ms_{index + 1:03d}",
            "name": name,
            "offsetDays": index * 7,
            "deliverables": [f"{name} 交付物"],
        }
        for index, name in enumerate(names)
    ]


def _status_label(status: str) -> str:
    return {"enabled": "启用", "disabled": "停用", "archived": "已归档"}.get(status, status)


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
