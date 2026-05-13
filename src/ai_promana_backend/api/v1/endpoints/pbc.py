# TODO: 工作台/PBC 接口当前为首版联调实现，后续接入任务、日报、PBC 目标和 AI 建议服务。
from typing import Any

from fastapi import APIRouter, Body

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 聚合当前用户今日日志、明日计划、阻塞任务、看板任务和 PBC 目标，按用户可见项目过滤。
@router.get("/overview", summary="工作台聚合数据")
def get_workbench_overview():
    return _mock.api_response(
        {
            "currentUser": _mock.current_user(),
            "unreadCount": len([item for item in _mock.notifications() if not item["read"]]),
            "todayLogs": [
                {
                    "id": "log_today_001",
                    "projectId": "project_001",
                    "taskId": "task_001",
                    "content": "Coordinated integration environment parameters.",
                    "hours": 2.5,
                    "createdAt": _mock.now_iso(),
                }
            ],
            "tomorrowPlans": [
                {
                    "id": "plan_001",
                    "title": "Confirm fallback lab slot",
                    "priority": "p1",
                    "projectId": "project_001",
                }
            ],
            "blockedItems": [task for task in _mock.tasks() if task["status"] == "blocked"],
            "kanbanTasks": _mock.tasks(),
            "pbcObjectives": [
                {
                    "id": "pbc_001",
                    "title": "Improve weekly delivery predictability",
                    "progress": 64,
                    "confidence": "medium",
                    "keyResults": [
                        {"id": "kr_001", "title": "Keep blocked tasks under 2", "progress": 75},
                        {"id": "kr_002", "title": "Review cycle under 24h", "progress": 58},
                    ],
                }
            ],
            "quickTaskDefaults": {
                "projectId": "project_001",
                "priority": "p2",
                "status": "pending",
                "startDate": _mock.today(),
            },
            "aiSuggestions": _mock.ai_suggestions("workbench"),
        }
    )


# TODO: 从 PBC 目标表查询当前周期目标，包含关键结果、负责人、进度和关联任务统计。
@router.get("/pbc-objectives", summary="PBC 目标列表")
def list_pbc_objectives():
    return _mock.api_response(
        [
            {
                "id": "pbc_001",
                "title": "Improve weekly delivery predictability",
                "progress": 64,
                "ownerId": "u_10001",
                "status": "active",
            }
        ]
    )


# TODO: 校验目标周期和 keyResults 后创建 PBC 目标，并关联当前用户或指定负责人。
@router.post("/pbc-objectives", summary="创建 PBC 目标")
def create_pbc_objective(payload: dict[str, Any] = Body(...)):
    return _mock.api_response(
        {
            "objective": {
                "id": _mock.make_id("pbc"),
                "title": payload.get("title", "Untitled objective"),
                "progress": payload.get("progress", 0),
                "status": payload.get("status", "active"),
                "createdAt": _mock.now_iso(),
            }
        }
    )
