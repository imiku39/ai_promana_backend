# TODO: 接入真实搜索服务后，改为查询项目、任务、用户和报表索引，并按当前用户权限过滤结果。
from fastapi import APIRouter, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


@router.get("/search", summary="全局搜索")
def global_search(
    keyword: str = Query(default="", description="搜索项目、任务、成员、报表"),
    types: str | None = Query(default=None, description="逗号分隔类型：project,task,user,report,document"),
    limit: int = Query(default=10, ge=1, le=50),
):
    allowed_types = _parse_types(types)
    normalized_keyword = keyword.strip().lower()
    items = _search_items(allowed_types)

    if normalized_keyword:
        items = [
            item
            for item in items
            if normalized_keyword in item["title"].lower()
            or normalized_keyword in item.get("description", "").lower()
        ]

    return _mock.api_response(items[:limit])


def _parse_types(types: str | None) -> set[str]:
    if not types:
        return {"project", "task", "user", "report", "document"}
    return {item.strip() for item in types.split(",") if item.strip()}


def _search_items(allowed_types: set[str]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    if "project" in allowed_types:
        results.extend(
            {
                "id": project["id"],
                "type": "project",
                "title": project["name"],
                "description": f"{project['status']} · {project['teamName']}",
                "targetPath": f"/project/{project['id']}",
            }
            for project in _mock.projects()
        )

    if "task" in allowed_types:
        results.extend(
            {
                "id": task["id"],
                "type": "task",
                "title": task["title"],
                "description": f"{task['status']} · {task['projectName']}",
                "targetPath": f"/task/{task['id']}",
            }
            for task in _mock.tasks()
        )

    if "user" in allowed_types:
        results.extend(
            {
                "id": user["id"],
                "type": "user",
                "title": user["name"],
                "description": f"{user['department']} · {user['platformRoleLabel']}",
                "targetPath": f"/admin/users?userId={user['id']}",
            }
            for user in _mock.users()
        )

    if "document" in allowed_types:
        results.extend(
            {
                "id": document["id"],
                "type": "document",
                "title": document["title"],
                "description": f"{document['type']} · {document['ownerName']}",
                "targetPath": f"/project/{document['projectId']}/docs?docId={document['id']}",
            }
            for document in _mock.documents()
        )

    if "report" in allowed_types:
        results.append(
            {
                "id": "report_global_overview",
                "type": "report",
                "title": "Global delivery overview",
                "description": "Project trend, risk and member workload report",
                "targetPath": "/reports",
            }
        )

    return results
