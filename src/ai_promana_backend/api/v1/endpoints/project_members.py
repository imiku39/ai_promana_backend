# TODO: 项目成员接口当前为首版联调实现，后续接入成员关系表、邀请流程、角色变更和权限校验。
from typing import Any

from fastapi import APIRouter, Body, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()

ROLE_LABELS = {
    "owner": ("pm", "PM", "负责人"),
    "pm": ("pm", "PM", "负责人"),
    "developer": ("dev", "研发", "研发成员"),
    "dev": ("dev", "研发", "研发成员"),
    "qa": ("qa", "QA", "质量保障"),
    "product": ("product", "产品", "产品协作"),
    "collaborator": ("collaborator", "协作", "协作成员"),
}

JOIN_STATUS_LABELS = {
    "active": ("joined", "已加入"),
    "joined": ("joined", "已加入"),
    "pending": ("pending", "待接受"),
    "disabled": ("rejected", "已拒绝"),
    "rejected": ("rejected", "已拒绝"),
}


# TODO: 查询项目成员、角色分布、工作负载热力图和邀请配置，校验 project:member:read。
@router.get("/{projectId}/members/page-data", summary="成员页聚合数据")
def get_project_members_page(projectId: str):
    members = [_member_item(item) for item in _mock.members()]
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "summary": _member_summary(members),
            "members": members,
            "pagination": {"page": 1, "pageSize": len(members), "total": len(members)},
            "inviteFlow": {
                "steps": ["select-user", "assign-role", "send-notice"],
                "defaultRole": "dev",
                "notifyChannels": ["in_app", "wecom", "email"],
            },
            "heatmap": _workload_heatmap_rows(members)["rows"],
            "workloadHeatmap": _workload_heatmap_rows(members),
            "filters": {
                "roles": [
                    {"value": "pm", "label": "PM"},
                    {"value": "dev", "label": "研发"},
                    {"value": "qa", "label": "QA"},
                    {"value": "product", "label": "产品"},
                    {"value": "collaborator", "label": "协作"},
                ],
                "statuses": [
                    {"value": "joined", "label": "已加入"},
                    {"value": "pending", "label": "待接受"},
                    {"value": "rejected", "label": "已拒绝"},
                ],
                "loadLevels": ["neutral", "success", "warning", "danger"],
            },
            "aiSuggestions": _mock.ai_suggestions("members"),
        }
    )


@router.get("/{projectId}/members/summary", summary="成员统计")
def get_project_members_summary(projectId: str):
    members = [_member_item(item) for item in _mock.members()]
    return _mock.api_response(_member_summary(members))


@router.get("/{projectId}/members", summary="成员列表")
def list_project_members(
    projectId: str,
    keyword: str | None = Query(default=None),
    role: str | None = Query(default=None),
    joinStatus: str | None = Query(default=None),
    loadLevel: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    members = [_member_item(item) for item in _mock.members()]
    if keyword:
        lowered = keyword.lower()
        members = [
            item
            for item in members
            if lowered in item["name"].lower()
            or lowered in item["department"].lower()
            or lowered in item["roleLabel"].lower()
        ]
    if role:
        members = [item for item in members if item["projectRole"] == role]
    if joinStatus:
        members = [item for item in members if item["joinStatus"] == joinStatus]
    if loadLevel:
        members = [item for item in members if item["loadLevel"] == loadLevel]

    members.sort(key=lambda item: (_role_weight(item["projectRole"]), item["joinStatus"], -item["loadRate"]))
    data = _mock.paged(members, page, pageSize)
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    return _mock.api_response(data)


@router.get("/{projectId}/members/workload-heatmap", summary="成员负载热力图")
def get_project_members_workload_heatmap(
    projectId: str,
    startDate: str | None = Query(default=None),
    days: int = Query(default=7, ge=1, le=14),
):
    members = [_member_item(item) for item in _mock.members()]
    return _mock.api_response(_workload_heatmap_rows(members, startDate, days))


# TODO: 搜索可邀请用户时排除已在项目内成员，并支持部门、角色、关键字过滤。
@router.get("/{projectId}/member-candidates", summary="可邀请成员搜索")
def search_member_candidates(
    projectId: str,
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    candidates = _candidate_users()
    if keyword:
        lowered = keyword.lower()
        candidates = [
            item
            for item in candidates
            if lowered in item["name"].lower() or lowered in item["email"].lower()
            or lowered in item["department"].lower()
        ]
    data = _mock.paged(candidates, page, pageSize)
    data["pagination"] = {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]}
    return _mock.api_response(data)


# TODO: 创建成员邀请记录，校验角色模板和重复邀请，并发送站内/企业微信通知。
@router.post("/{projectId}/member-invitations", summary="邀请成员")
def invite_project_members(projectId: str, payload: dict[str, Any] = Body(...)):
    user_ids = payload.get("userIds") or payload.get("memberIds") or []
    project_role = payload.get("projectRole") or payload.get("role") or "dev"
    return _mock.api_response(
        {
            "projectId": projectId,
            "invitationId": _mock.make_id("member_invitation"),
            "invitationIds": [_mock.make_id("invite") for _ in user_ids] or [_mock.make_id("invite")],
            "userIds": user_ids,
            "memberIds": user_ids,
            "projectRole": project_role,
            "role": project_role,
            "message": payload.get("message"),
            "notifyChannels": payload.get("notifyChannels", ["in_app"]),
            "status": "sent",
            "createdAt": _mock.now_iso(),
        }
    )


# TODO: 更新成员项目角色或状态，防止移除唯一项目负责人，并刷新项目权限缓存。
@router.patch("/{projectId}/members/{memberId}", summary="调整成员角色/状态")
def update_project_member(projectId: str, memberId: str, payload: dict[str, Any] = Body(...)):
    project_role = payload.get("projectRole") or payload.get("role") or "dev"
    _, role_label, role_name = ROLE_LABELS.get(project_role, (project_role, project_role, project_role))
    return _mock.api_response(
        {
            "projectId": projectId,
            "memberId": memberId,
            "role": role_name,
            "projectRole": project_role,
            "roleLabel": role_label,
            "status": payload.get("status", "active"),
            "joinStatus": payload.get("joinStatus", "joined"),
            "version": payload.get("version", 1) + 1,
            "updatedAt": _mock.now_iso(),
        }
    )


# TODO: 移除成员前检查未完成任务和负责人职责，执行软删除并转移或清空相关分配。
@router.delete("/{projectId}/members/{memberId}", summary="移除成员")
def remove_project_member(projectId: str, memberId: str):
    return _mock.api_response(
        {
            "projectId": projectId,
            "memberId": memberId,
            "removed": True,
            "reassignmentRequired": False,
            "removedAt": _mock.now_iso(),
        }
    )


@ai_router.get("/project-member-suggestions", summary="AI 成员建议")
def get_project_member_suggestions(projectId: str | None = Query(default=None)):
    return _mock.api_response({"projectId": projectId, "suggestions": _mock.ai_suggestions("project_member")})


@ai_router.post("/project-member-suggestions/{suggestionId}/apply", summary="采纳 AI 成员建议")
def apply_project_member_suggestion(suggestionId: str, payload: dict[str, Any] | None = Body(default=None)):
    return _mock.api_response(
        {
            "suggestionId": suggestionId,
            "applied": True,
            "adjustments": (payload or {}).get("adjustments", []),
            "resultMessage": "已生成成员负载调整建议，并同步到项目成员页。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _member_item(member: dict[str, Any]) -> dict[str, Any]:
    project_role, role_label, role_name = ROLE_LABELS.get(member.get("role", "collaborator"), ("collaborator", "协作", "协作成员"))
    join_status, join_status_label = JOIN_STATUS_LABELS.get(member.get("status", "active"), ("joined", "已加入"))
    load_rate = int(member.get("workload", 0))
    estimate_hours = max(1, int(member.get("taskCount", 0)) * 6)
    return {
        "memberId": member["id"],
        "id": member["id"],
        "userId": member["userId"],
        "name": member["name"],
        "avatar": member.get("avatar"),
        "department": member.get("department", "R&D Center"),
        "role": role_name,
        "projectRole": project_role,
        "roleLabel": role_label,
        "joinStatus": join_status,
        "joinStatusLabel": join_status_label,
        "taskCount": member.get("taskCount", 0),
        "estimateHours": estimate_hours,
        "estimateDisplay": f"{round(estimate_hours / 8, 1)}d",
        "loadRate": load_rate,
        "loadLevel": _load_level(load_rate),
        "permissions": ["role:update", "remove"] if project_role != "pm" else ["role:update"],
        "updatedAt": _mock.now_iso(),
    }


def _member_summary(members: list[dict[str, Any]]) -> dict[str, Any]:
    overloaded = [item for item in members if item["loadRate"] > 80]
    return {
        "memberTotal": len(members),
        "totalMembers": len(members),
        "activeMembers": len([item for item in members if item["joinStatus"] == "joined"]),
        "pendingInviteCount": len([item for item in members if item["joinStatus"] == "pending"]) or 2,
        "overloadedCount": len(overloaded),
        "overloadThreshold": 80,
        "averageWorkload": round(sum(item["loadRate"] for item in members) / max(len(members), 1), 1),
        "aiSuggestionAdoptionRate": 67,
        "weeklyAdoptionCount": 6,
        "updatedAt": _mock.now_iso(),
    }


def _load_level(load_rate: int) -> str:
    if load_rate > 90:
        return "danger"
    if load_rate >= 70:
        return "warning"
    if load_rate >= 50:
        return "success"
    return "neutral"


def _role_weight(project_role: str) -> int:
    return {"pm": 0, "dev": 1, "qa": 2, "product": 3, "collaborator": 4}.get(project_role, 5)


def _workload_heatmap_rows(members: list[dict[str, Any]], start_date: str | None = None, days: int = 7) -> dict[str, Any]:
    day_labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][:days]
    base_date = start_date or _mock.today()
    rows = []
    for index, member in enumerate(members):
        daily_loads = []
        cells = []
        for day in range(days):
            load_rate = min(100, max(0, member["loadRate"] + (day - 3) * 3 - index * 2))
            level = min(5, max(0, round(load_rate / 20)))
            cells.append(level)
            daily_loads.append({"date": base_date, "loadRate": load_rate, "level": level})
        rows.append({"userId": member["userId"], "name": member["name"], "cells": cells, "dailyLoads": daily_loads})
    return {"days": day_labels, "rows": rows, "startDate": base_date}


def _candidate_users() -> list[dict[str, Any]]:
    existing_user_ids = {member["userId"] for member in _mock.members()}
    candidates = [
        {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "department": user["department"],
            "platformRole": user["platformRole"],
            "avatar": user.get("avatar"),
            "eligible": True,
        }
        for user in _mock.users()
        if user["id"] not in existing_user_ids
    ]
    if candidates:
        return candidates
    return [
        {
            "id": "u_10004",
            "name": "Liu Ming",
            "email": "liu@example.com",
            "department": "Platform Engineering",
            "platformRole": "developer",
            "avatar": None,
            "eligible": True,
        }
    ]
