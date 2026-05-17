# TODO: 文档接口当前为首版联调实现，后续接入 PyMySQL 文档元数据、对象存储、版本管理和权限校验。
from typing import Any

from fastapi import APIRouter, Body, File, HTTPException, Query, UploadFile

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()

STATUS_LABELS = {
    "latest": "最新版本",
    "ai_summary": "AI 摘要",
    "incomplete": "待补充",
    "archived": "已归档",
}

FILE_TYPE_LABELS = {
    "markdown": "Markdown",
    "spreadsheet": "表格",
    "pdf": "PDF",
    "docx": "Word",
    "attachment": "附件",
}


@router.get("/{projectId}/docs/summary", summary="文档统计")
def get_project_docs_summary(projectId: str):
    return _mock.api_response(_doc_summary(_doc_items(projectId)))


@router.get("/{projectId}/docs/options", summary="文档筛选和表单选项")
def get_project_docs_options(projectId: str):
    return _mock.api_response(_doc_options(projectId))


@router.get("/{projectId}/docs/page-data", summary="文档页聚合数据")
def get_project_docs_page(projectId: str):
    docs = _doc_items(projectId)
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "summary": _doc_summary(docs),
            "options": _doc_options(projectId),
            "documents": docs,
            "list": docs,
            "aiSuggestions": _doc_suggestions(projectId),
            "permissions": ["project:doc:read", "project:doc:create", "project:doc:update", "project:doc:download"],
            "updatedAt": _mock.now_iso(),
        }
    )


@router.get("/{projectId}/docs", summary="文档列表")
def list_project_docs(
    projectId: str,
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    ownerId: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    items = _doc_items(projectId)
    keyword_value = _plain_query_value(keyword)
    status_value = _plain_query_value(status)
    tag_value = _plain_query_value(tag)
    owner_value = _plain_query_value(ownerId)
    if keyword_value:
        lowered = str(keyword_value).lower()
        items = [
            item
            for item in items
            if lowered in item["title"].lower() or lowered in item.get("description", "").lower()
        ]
    if status_value and status_value != "all":
        items = [item for item in items if item["status"] == status_value]
    if tag_value:
        items = [item for item in items if tag_value in item.get("tags", [])]
    if owner_value:
        items = [item for item in items if item["owner"]["id"] == owner_value]
    items.sort(key=lambda item: item["updatedAt"], reverse=True)
    data = _mock.paged(items, int(_plain_query_value(page, 1) or 1), int(_plain_query_value(pageSize, 20) or 20))
    return _mock.api_response(
        {
            "list": data["list"],
            "pagination": {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]},
            "summary": _doc_summary(items),
            "filters": {
                "keyword": keyword_value,
                "status": status_value or "all",
                "tag": tag_value,
                "ownerId": owner_value,
            },
        }
    )


@router.get("/{projectId}/docs/{docId}", summary="文档详情")
def get_project_doc(projectId: str, docId: str):
    doc = next((item for item in _doc_items(projectId) if item["docId"] == docId), None)
    if not doc:
        raise HTTPException(status_code=404, detail={"code": "DOC_NOT_FOUND", "message": "文档不存在"})
    detail = {
        **doc,
        "content": "# 项目文档\n\n这里是首版联调用文档正文占位，后续会替换为文档存储内容。",
        "attachments": _doc_attachments(projectId, docId),
        "versions": _doc_versions(projectId, docId),
        "aiSummary": "本文档说明当前项目阶段的关键结论、风险和任务引用。",
    }
    return _mock.api_response({**detail, "document": detail})


@router.get("/{projectId}/docs/{docId}/versions", summary="文档版本")
def list_project_doc_versions(projectId: str, docId: str):
    return _mock.api_response({"projectId": projectId, "docId": docId, "versions": _doc_versions(projectId, docId)})


@router.post("/{projectId}/docs", summary="新建文档")
def create_project_doc(projectId: str, payload: dict[str, Any] = Body(...)):
    title = str(payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail={"code": "DOC_VALIDATE_FAILED", "message": "请输入文档标题"})
    document = _doc_from_payload(projectId, payload, doc_id=_mock.make_id("doc"))
    return _mock.api_response({"docId": document["docId"], "document": document, "targetPath": f"/project/{projectId}/docs"})


@router.put("/{projectId}/docs/{docId}", summary="编辑文档")
def update_project_doc(projectId: str, docId: str, payload: dict[str, Any] = Body(...)):
    document = _doc_from_payload(projectId, payload, doc_id=docId)
    document["version"] = int(payload.get("version", 1)) + 1
    document["latestVersion"] = f"v{document['version']}"
    document["updatedAt"] = _mock.now_iso()
    return _mock.api_response(
        {
            "docId": docId,
            "latestVersion": document["latestVersion"],
            "version": document["version"],
            "updatedAt": document["updatedAt"],
            "document": document,
        }
    )


@router.delete("/{projectId}/docs/{docId}", summary="删除/归档文档")
def delete_project_doc(projectId: str, docId: str):
    return _mock.api_response(
        {
            "projectId": projectId,
            "docId": docId,
            "archived": True,
            "status": "archived",
            "statusLabel": STATUS_LABELS["archived"],
            "updatedAt": _mock.now_iso(),
        }
    )


@router.post("/{projectId}/docs/{docId}/attachments", summary="上传附件")
def upload_project_doc_attachment(projectId: str, docId: str, file: UploadFile = File(...)):
    file_name = file.filename or "unnamed"
    return _mock.api_response(
        {
            "projectId": projectId,
            "docId": docId,
            "attachment": {
                "id": _mock.make_id("attachment"),
                "fileName": file_name,
                "contentType": file.content_type,
                "size": file.size,
                "url": f"https://example.com/files/{file_name}",
                "uploadedAt": _mock.now_iso(),
            },
        }
    )


@router.get("/{projectId}/docs/{docId}/download", summary="下载文档")
def download_project_doc(projectId: str, docId: str):
    return _mock.api_response(
        {
            "projectId": projectId,
            "docId": docId,
            "downloadUrl": f"https://example.com/projects/{projectId}/docs/{docId}/download",
            "expiresIn": 600,
        }
    )


@router.post("/{projectId}/docs/{docId}/export", summary="导出文档")
def export_project_doc(projectId: str, docId: str, payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("doc_export")
    task["projectId"] = projectId
    task["docId"] = docId
    task["fileType"] = (payload or {}).get("fileType", "pdf")
    return _mock.api_response(task)


@ai_router.post("/project-docs/{docId}/summary", summary="生成 AI 文档摘要")
def generate_project_doc_summary(docId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    return _mock.api_response(
        {
            "summaryId": _mock.make_id("summary"),
            "docId": docId,
            "summaryType": body.get("summaryType", "brief"),
            "summary": "本文档说明当前联调阶段的前置条件、关键风险和任务引用。",
            "saved": bool(body.get("saveToDoc", True)),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.get("/project-doc-suggestions", summary="AI 文档建议")
def get_project_doc_suggestions(
    projectId: str | None = Query(default=None),
    context: str | None = Query(default="project_docs"),
):
    return _mock.api_response(
        {
            "projectId": _plain_query_value(projectId),
            "context": _plain_query_value(context, "project_docs") or "project_docs",
            "suggestions": _doc_suggestions(_plain_query_value(projectId)),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/project-doc-suggestions/{suggestionId}/apply", summary="采纳 AI 文档建议")
def apply_project_doc_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "actionKey": body.get("actionKey", "generate_outline"),
            "applied": True,
            "createdDocId": body.get("createdDocId", _mock.make_id("doc")),
            "updatedDocIds": body.get("updatedDocIds", ["doc_003"]),
            "message": "已生成回归样本池说明提纲，并同步到项目文档列表。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _doc_items(project_id: str) -> list[dict[str, Any]]:
    users = _mock.users()
    base_docs = _mock.documents()
    extra_docs = [
        {
            "id": "doc_003",
            "title": "回归样本池说明",
            "type": "markdown",
            "status": "incomplete",
            "ownerId": "u_10002",
            "ownerName": "Chen Siyuan",
            "updatedAt": _mock.now_iso(),
            "tags": ["联调", "风险"],
        }
    ]
    docs = base_docs + extra_docs
    items = []
    for index, doc in enumerate(docs):
        status = _doc_status(doc, index)
        owner = next((item for item in users if item["id"] == doc.get("ownerId")), users[index % len(users)])
        items.append(
            {
                "docId": doc["id"],
                "id": doc["id"],
                "projectId": project_id,
                "title": doc["title"],
                "description": _doc_description(doc, status),
                "status": status,
                "statusLabel": STATUS_LABELS.get(status, status),
                "tags": doc.get("tags", []),
                "owner": {"id": owner["id"], "name": owner["name"], "avatar": owner.get("avatar")},
                "latestVersion": f"v{index + 2}",
                "updatedAt": doc.get("updatedAt", _mock.now_iso()),
                "updatedBy": {"id": owner["id"], "name": owner["name"]},
                "visibility": "project_members",
                "fileType": doc.get("type", "markdown"),
                "fileTypeLabel": FILE_TYPE_LABELS.get(doc.get("type", "markdown"), doc.get("type")),
                "hasAiSummary": status == "ai_summary",
                "linkedTaskIds": ["task_001"] if index == 0 else [],
                "linkedMilestoneIds": ["ms_001"] if index == 0 else [],
                "permissions": ["read", "edit", "download"],
                "version": index + 2,
            }
        )
    return items


def _doc_from_payload(project_id: str, payload: dict[str, Any], doc_id: str) -> dict[str, Any]:
    owner = _user_by_id(payload.get("ownerId"))
    status = payload.get("status", "latest")
    file_type = payload.get("fileType") or payload.get("type", "markdown")
    return {
        "docId": doc_id,
        "id": doc_id,
        "projectId": project_id,
        "title": payload.get("title", "未命名文档"),
        "description": payload.get("description", ""),
        "content": payload.get("content", ""),
        "status": status,
        "statusLabel": STATUS_LABELS.get(status, status),
        "tags": payload.get("tags", []),
        "owner": {"id": owner["id"], "name": owner["name"], "avatar": owner.get("avatar")},
        "latestVersion": f"v{int(payload.get('version', 1))}",
        "updatedAt": _mock.now_iso(),
        "updatedBy": {"id": owner["id"], "name": owner["name"]},
        "visibility": payload.get("visibility", "project_members"),
        "fileType": file_type,
        "fileTypeLabel": FILE_TYPE_LABELS.get(file_type, file_type),
        "hasAiSummary": bool(payload.get("hasAiSummary", False)),
        "linkedTaskIds": payload.get("linkedTaskIds", []),
        "linkedMilestoneIds": payload.get("linkedMilestoneIds", []),
        "permissions": ["read", "edit", "download"],
        "version": int(payload.get("version", 1)),
    }


def _doc_versions(project_id: str, doc_id: str) -> list[dict[str, Any]]:
    return [
        {
            "versionId": "docv_001",
            "id": "docv_001",
            "projectId": project_id,
            "docId": doc_id,
            "versionName": "v1",
            "version": 1,
            "changeSummary": "创建初始文档",
            "createdAt": "2026-05-10T10:00:00+08:00",
            "createdBy": {"id": "u_10001", "name": "Zhang Gong"},
            "authorName": "Zhang Gong",
            "downloadUrl": f"https://example.com/docs/{doc_id}/versions/1",
        },
        {
            "versionId": "docv_002",
            "id": "docv_002",
            "projectId": project_id,
            "docId": doc_id,
            "versionName": "v2",
            "version": 2,
            "changeSummary": "补充联调风险和样本说明",
            "createdAt": _mock.now_iso(),
            "createdBy": {"id": "u_10003", "name": "Wang Yating"},
            "authorName": "Wang Yating",
            "downloadUrl": f"https://example.com/docs/{doc_id}/versions/2",
        },
    ]


def _doc_attachments(project_id: str, doc_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "attachment_001",
            "projectId": project_id,
            "docId": doc_id,
            "fileName": "validation-checklist.xlsx",
            "contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "url": "https://example.com/files/validation-checklist.xlsx",
            "uploadedAt": _mock.now_iso(),
        }
    ]


def _doc_summary(docs: list[dict[str, Any]]) -> dict[str, Any]:
    latest_updated = max([item["updatedAt"] for item in docs], default=_mock.now_iso())
    return {
        "docTotal": len(docs),
        "total": len(docs),
        "incompleteCount": len([item for item in docs if item["status"] == "incomplete"]),
        "aiSummaryCount": len([item for item in docs if item["hasAiSummary"]]),
        "recentUpdated": len(docs[:2]),
        "latestUpdatedAt": latest_updated,
        "lastUpdatedAt": latest_updated,
    }


def _doc_options(project_id: str) -> dict[str, Any]:
    docs = _doc_items(project_id)
    tags = sorted({tag for item in docs for tag in item.get("tags", [])})
    return {
        "types": [{"value": key, "label": value} for key, value in FILE_TYPE_LABELS.items()],
        "statuses": [{"value": key, "label": value} for key, value in STATUS_LABELS.items()],
        "owners": [
            {"id": item["id"], "name": item["name"], "label": item["name"], "value": item["id"]}
            for item in _mock.users()
        ],
        "tags": [{"label": tag, "value": tag} for tag in tags],
        "visibility": [
            {"value": "project_members", "label": "项目成员"},
            {"value": "owners_only", "label": "负责人可见"},
            {"value": "public", "label": "公开"},
        ],
    }


def _doc_suggestions(project_id: str | None) -> list[dict[str, Any]]:
    return [
        {
            "suggestionId": "doc_sug_001",
            "id": "doc_sug_001",
            "projectId": project_id,
            "title": "文档建议",
            "content": "建议优先补齐回归样本池说明，并关联当前阻塞任务。",
            "targetDocId": "doc_003",
            "actions": [
                {"key": "generate_outline", "label": "生成提纲"},
                {"key": "generate_summary", "label": "生成摘要"},
            ],
        },
        {
            "suggestionId": "doc_sug_002",
            "id": "doc_sug_002",
            "projectId": project_id,
            "title": "摘要建议",
            "content": "已有验证清单可生成 AI 摘要，供项目报表引用。",
            "targetDocId": "doc_002",
            "actions": [{"key": "generate_summary", "label": "生成摘要"}],
        },
    ]


def _doc_status(doc: dict[str, Any], index: int) -> str:
    if doc.get("status") == "archived":
        return "archived"
    if doc.get("status") == "incomplete":
        return "incomplete"
    if index == 1:
        return "ai_summary"
    return "latest"


def _doc_description(doc: dict[str, Any], status: str) -> str:
    if status == "incomplete":
        return "该文档缺少回归样本池和风险说明，需要补齐后再进入评审。"
    if doc.get("type") == "spreadsheet":
        return "项目验证清单，包含样本、负责人、状态和风险备注。"
    return "记录需求边界、时间计划和依赖说明，供 PM、研发与 QA 对齐使用。"


def _user_by_id(user_id: str | None) -> dict[str, Any]:
    users = _mock.users()
    return next((item for item in users if item["id"] == user_id), users[0])


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
