# TODO: 任务接口当前为首版联调实现，后续接入任务 service、评论/子任务表、看板排序和状态机。
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from ai_promana_backend.api.v1.endpoints import _mock
from ai_promana_backend.api.v1.endpoints.projects import flow_rules, kanban_columns


router = APIRouter()
project_router = APIRouter()
ai_router = APIRouter()


# TODO: 将任务草稿保存到草稿表，支持按用户和项目恢复未提交任务。
@router.post("/drafts", summary="保存任务草稿")
def save_task_draft(payload: dict[str, Any] = Body(...)):
    return _mock.api_response({"draftId": _mock.make_id("task_draft"), "savedAt": _mock.now_iso(), "draft": payload})


# TODO: 校验项目、负责人、评审人、优先级和日期，创建任务并写入看板默认列。
@router.post("", summary="创建任务")
def create_task(payload: dict[str, Any] = Body(...)):
    task = _task_from_payload(payload)
    return _mock.api_response({"task": task})


# TODO: 查询任务详情、子任务、评论和 AI 建议；任务不存在返回 TASK_NOT_FOUND。
@router.get("/{taskId}", summary="任务详情")
def get_task_detail(taskId: str):
    task = _mock.task_lite(taskId)
    return _mock.api_response(
        {
            "task": task,
            "description": "This task is part of the first backend contract implementation.",
            "subtasks": [
                {"id": "subtask_001", "title": "Confirm acceptance criteria", "completed": True},
                {"id": "subtask_002", "title": "Sync with reviewer", "completed": False},
            ],
            "comments": [
                {
                    "id": "comment_001",
                    "authorId": "u_10001",
                    "authorName": "Zhang Gong",
                    "content": "Please keep the blocked reason visible on the kanban card.",
                    "createdAt": _mock.now_iso(),
                }
            ],
            "aiSuggestions": _mock.ai_suggestions("task"),
        }
    )


# TODO: 支持局部更新任务字段，校验字段白名单、版本冲突和状态流转限制。
@router.patch("/{taskId}", summary="更新任务字段")
def update_task(taskId: str, payload: dict[str, Any] = Body(...)):
    task = _mock.task_lite(taskId)
    task.update(payload)
    task["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"task": task})


# TODO: 保存任务评论，支持提及用户通知、附件扩展和空内容校验。
@router.post("/{taskId}/comments", summary="添加评论")
def add_task_comment(taskId: str, payload: dict[str, Any] = Body(...)):
    content = payload.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    return _mock.api_response(
        {
            "comment": {
                "id": _mock.make_id("comment"),
                "taskId": taskId,
                "content": content,
                "author": _mock.current_user(),
                "createdAt": _mock.now_iso(),
            }
        }
    )


# TODO: 更新子任务完成状态，完成度需反算到父任务进度并记录操作日志。
@router.patch("/{taskId}/subtasks/{subtaskId}", summary="勾选子任务")
def update_subtask(taskId: str, subtaskId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "taskId": taskId,
            "subtaskId": subtaskId,
            "completed": payload.get("completed", True),
            "updatedAt": _mock.now_iso(),
        }
    )


# TODO: 查询项目看板列、任务卡片、筛选项和流转规则，按用户任务权限过滤字段。
@project_router.get("/{projectId}/kanban/page-data", summary="看板聚合数据")
def get_project_kanban_page(projectId: str):
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "summary": {
                "totalTasks": len(_mock.tasks(projectId)),
                "blockedTasks": len([task for task in _mock.tasks(projectId) if task["status"] == "blocked"]),
                "updatedAt": _mock.now_iso(),
            },
            "columns": kanban_columns(projectId),
            "flowRules": flow_rules(),
            "filters": {
                "assignees": _mock.users(),
                "priorities": ["p0", "p1", "p2", "p3"],
                "statuses": ["pending", "in_progress", "review", "completed", "blocked"],
            },
            "aiSuggestions": _mock.ai_suggestions("kanban"),
        }
    )


# TODO: 在指定项目内创建任务，自动填充 projectId 并校验 project:task:create 或 task:create 权限。
@project_router.post("/{projectId}/tasks", summary="在项目内创建任务")
def create_project_task(projectId: str, payload: dict[str, Any] = Body(...)):
    payload["projectId"] = projectId
    return _mock.api_response({"task": _task_from_payload(payload)})


# TODO: 编辑项目任务时校验任务归属 projectId，避免跨项目越权更新。
@project_router.put("/{projectId}/tasks/{taskId}", summary="编辑任务")
def update_project_task(projectId: str, taskId: str, payload: dict[str, Any] = Body(...)):
    task = _mock.task_lite(taskId)
    task.update(payload)
    task["projectId"] = projectId
    task["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"task": task})


# TODO: 实现任务状态机，blocked 必填 blockedReason，非法流转返回 TASK_TRANSITION_INVALID。
@project_router.post("/{projectId}/tasks/{taskId}/transition", summary="任务状态流转")
def transition_project_task(projectId: str, taskId: str, payload: dict[str, Any] = Body(...)):
    to_status = payload.get("toStatus")
    if to_status == "blocked" and not payload.get("blockedReason"):
        raise HTTPException(status_code=400, detail={"code": "TASK_BLOCK_REASON_REQUIRED", "message": "blockedReason is required"})
    return _mock.api_response(
        {
            "projectId": projectId,
            "taskId": taskId,
            "status": to_status,
            "columnKey": payload.get("columnKey"),
            "blockedReason": payload.get("blockedReason"),
            "transitionedAt": _mock.now_iso(),
        }
    )


# TODO: 持久化看板列内和跨列排序，校验任务列表完整性并处理并发拖拽冲突。
@project_router.patch("/{projectId}/kanban/order", summary="调整看板顺序")
def update_kanban_order(projectId: str, payload: dict[str, Any] = Body(...)):
    return _mock.api_response({"projectId": projectId, "order": payload, "updatedAt": _mock.now_iso()})


# TODO: 基于任务描述、历史评论、阻塞原因和项目上下文生成任务 AI 建议。
@ai_router.get("/tasks/{taskId}/suggestions", summary="任务 AI 建议")
def get_task_ai_suggestions(taskId: str):
    return _mock.api_response({"taskId": taskId, "suggestions": _mock.ai_suggestions("task")})


# TODO: 采纳任务建议时执行更新字段、创建子任务或发送通知等动作，并写入采纳记录。
@ai_router.post("/tasks/{taskId}/suggestions/{suggestionId}/apply", summary="采纳任务 AI 建议")
def apply_task_ai_suggestion(taskId: str, suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response({"taskId": taskId, "suggestionId": suggestionId, "applied": True, "payload": payload or {}})


def _task_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": _mock.make_id("task"),
        "title": payload.get("title", "Untitled task"),
        "status": payload.get("status", "pending"),
        "columnKey": payload.get("columnKey", "todo"),
        "priority": payload.get("priority", "p2"),
        "projectId": payload.get("projectId", "project_001"),
        "assigneeId": payload.get("assigneeId"),
        "reviewerId": payload.get("reviewerId"),
        "progress": payload.get("progress", 0),
        "startDate": payload.get("startDate", _mock.today()),
        "dueAt": payload.get("dueAt", _mock.now_iso()),
        "estimatedHours": payload.get("estimatedHours"),
        "blockedReason": payload.get("blockedReason"),
        "description": payload.get("description"),
        "tags": payload.get("tags", []),
        "createdAt": _mock.now_iso(),
    }
