# TODO: 管理端通用选项当前为首版联调实现，后续接入统一字典/配置服务。
from fastapi import APIRouter

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 从统一字典/配置表读取角色、状态、健康度和团队选项，替换当前硬编码列表。
@router.get("/options", summary="管理端通用选项")
def get_management_options():
    return _mock.api_response(
        {
            "roles": ["super_admin", "admin", "pm", "developer", "qa", "product", "collaborator", "user"],
            "userStatuses": ["pending", "active", "disabled"],
            "projectStatuses": ["pending", "active", "paused", "completed", "archived"],
            "projectHealth": ["good", "attention", "risk", "completed"],
            "teams": _mock.option_items()["teams"],
        }
    )
