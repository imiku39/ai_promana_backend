# TODO: 文档接口当前为首版联调实现，后续接入文档存储、版本管理、附件上传和权限校验。
from typing import Any

from fastapi import APIRouter, Body, UploadFile, File

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 查询项目文档列表、文档类型筛选项和最近更新统计，并校验 project:doc:read 权限。
@router.get("/{projectId}/docs/page-data", summary="文档页聚合数据")
def get_project_docs_page(projectId: str):
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "summary": {
                "total": len(_mock.documents()),
                "recentUpdated": 2,
                "lastUpdatedAt": _mock.now_iso(),
            },
            "options": {
                "types": ["markdown", "spreadsheet", "pdf", "attachment"],
                "statuses": ["active", "archived"],
                "owners": _mock.users(),
            },
            "documents": _mock.documents(),
            "aiSuggestions": _mock.ai_suggestions("docs"),
        }
    )


# TODO: 根据 projectId/docId 查询文档正文、元数据和附件，处理 DOC_NOT_FOUND 与无权限场景。
@router.get("/{projectId}/docs/{docId}", summary="文档详情")
def get_project_doc(projectId: str, docId: str):
    doc = next((item for item in _mock.documents() if item["id"] == docId), _mock.documents()[0])
    doc["projectId"] = projectId
    doc["content"] = "# Project Document\n\nThis is a first-version backend placeholder document."
    return _mock.api_response({"document": doc})


# TODO: 从文档版本表读取历史版本，包含版本号、作者、变更摘要和回滚权限。
@router.get("/{projectId}/docs/{docId}/versions", summary="文档版本")
def list_project_doc_versions(projectId: str, docId: str):
    return _mock.api_response(
        {
            "projectId": projectId,
            "docId": docId,
            "versions": [
                {"id": "doc_version_001", "version": 1, "createdAt": "2026-05-10T10:00:00+08:00", "authorName": "Zhang Gong"},
                {"id": "doc_version_002", "version": 2, "createdAt": _mock.now_iso(), "authorName": "Wang Yating"},
            ],
        }
    )


# TODO: 校验标题/类型/内容，创建文档初始版本，并写入项目动态和操作日志。
@router.post("/{projectId}/docs", summary="新建文档")
def create_project_doc(projectId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "document": {
                "id": _mock.make_id("doc"),
                "projectId": projectId,
                "title": payload.get("title", "Untitled document"),
                "type": payload.get("type", "markdown"),
                "content": payload.get("content", ""),
                "createdAt": _mock.now_iso(),
            }
        }
    )


# TODO: 保存文档变更为新版本，处理并发版本冲突，返回最新版本号和更新时间。
@router.put("/{projectId}/docs/{docId}", summary="编辑文档")
def update_project_doc(projectId: str, docId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response({"projectId": projectId, "docId": docId, "document": payload, "updatedAt": _mock.now_iso()})


# TODO: 按业务要求执行软删除/归档，保留版本和附件引用，并记录删除人。
@router.delete("/{projectId}/docs/{docId}", summary="删除/归档文档")
def delete_project_doc(projectId: str, docId: str):
    return _mock.api_response({"projectId": projectId, "docId": docId, "archived": True, "updatedAt": _mock.now_iso()})


# TODO: 接入对象存储，校验文件大小/类型，保存附件记录并关联到指定文档版本。
@router.post("/{projectId}/docs/{docId}/attachments", summary="上传附件")
def upload_project_doc_attachment(projectId: str, docId: str, file: UploadFile = File(...)):
    return _mock.api_response(
        {
            "projectId": projectId,
            "docId": docId,
            "attachment": {
                "id": _mock.make_id("attachment"),
                "fileName": file.filename,
                "contentType": file.content_type,
                "url": f"https://example.com/files/{file.filename}",
                "uploadedAt": _mock.now_iso(),
            },
        }
    )
