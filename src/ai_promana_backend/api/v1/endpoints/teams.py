# TODO: 团队接口当前为首版联调实现，后续接入团队组织架构、成员查询和权限过滤。
from fastapi import APIRouter, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()


# TODO: 从组织架构表查询团队列表，支持 keyword 和启用状态过滤。
@router.get("", summary="团队列表")
def list_teams(keyword: str | None = Query(default=None)):
    teams = _mock.option_items()["teams"]
    if keyword:
        lowered = keyword.lower()
        teams = [item for item in teams if lowered in item["label"].lower()]
    return _mock.api_response(teams)


# TODO: 查询团队成员并补充角色、邮箱、状态，必要时按当前用户权限隐藏敏感字段。
@router.get("/{teamId}/members", summary="团队成员")
def list_team_members(teamId: str):
    return _mock.api_response({"teamId": teamId, "members": _mock.users()})
