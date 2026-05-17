# TODO: 风险接口当前为首版联调实现，后续接入 PyMySQL 风险台账、状态流转、批量处理和导出任务。
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from ai_promana_backend.api.v1.endpoints import _mock


router = APIRouter()
ai_router = APIRouter()

LEVEL_LABELS = {"low": "低", "medium": "中等", "high": "高危", "critical": "极高"}
LEVEL_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}
STATUS_LABELS = {"open": "待处理", "processing": "处理中", "mitigated": "已缓解", "closed": "已关闭"}


@router.get("/{projectId}/risks/summary", summary="风险统计")
def get_project_risk_summary(projectId: str):
    risks = _risk_items(projectId)
    return _mock.api_response(_risk_summary(risks))


@router.get("/{projectId}/risks/resource-heatmap", summary="资源冲突热力图")
def get_project_risk_resource_heatmap(
    projectId: str,
    startDate: str | None = Query(default=None),
    days: int = Query(default=21, ge=1, le=60),
):
    days_value = int(_plain_query_value(days, 21) or 21)
    return _mock.api_response(
        {
            "projectId": projectId,
            "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "cells": _resource_heatmap(_plain_query_value(startDate) or _mock.today(), days_value),
            "updatedAt": _mock.now_iso(),
        }
    )


@router.get("/{projectId}/risks/options", summary="风险筛选和表单选项")
def get_project_risk_options(projectId: str):
    return _mock.api_response(
        {
            "projectId": projectId,
            "levels": [{"value": key, "label": value} for key, value in LEVEL_LABELS.items()],
            "statuses": [{"value": key, "label": value} for key, value in STATUS_LABELS.items()],
            "owners": [
                {"id": item["id"], "name": item["name"], "label": item["name"], "value": item["id"]}
                for item in _mock.users()
            ],
            "sources": [
                {"value": "kanban_blocked", "label": "看板阻塞"},
                {"value": "gantt_delay", "label": "甘特延期"},
                {"value": "manual", "label": "手动创建"},
                {"value": "ai_detected", "label": "AI 识别"},
            ],
        }
    )


@router.get("/{projectId}/risks", summary="风险列表")
def list_project_risks(
    projectId: str,
    level: str | None = Query(default=None),
    status: str | None = Query(default=None),
    ownerId: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
):
    items = _risk_items(projectId)
    level_value = _plain_query_value(level)
    status_value = _plain_query_value(status)
    owner_value = _plain_query_value(ownerId)
    keyword_value = _plain_query_value(keyword)
    if level_value and level_value != "all":
        items = [item for item in items if item["level"] == level_value]
    if status_value and status_value != "all":
        items = [item for item in items if item["status"] == status_value]
    if owner_value:
        items = [item for item in items if item["owner"]["id"] == owner_value]
    if keyword_value:
        lowered = str(keyword_value).lower()
        items = [
            item
            for item in items
            if lowered in item["name"].lower()
            or lowered in item.get("factor", "").lower()
            or lowered in item.get("mitigationPlan", "").lower()
        ]
    items.sort(key=lambda item: (LEVEL_WEIGHT.get(item["level"], 0), item["blockRate"]), reverse=True)
    page_value = int(_plain_query_value(page, 1) or 1)
    page_size_value = int(_plain_query_value(pageSize, 20) or 20)
    data = _mock.paged(items, page_value, page_size_value)
    return _mock.api_response(
        {
            "list": data["list"],
            "pagination": {"page": data["page"], "pageSize": data["pageSize"], "total": data["total"]},
            "summary": _risk_summary(items),
            "filters": {
                "level": level_value or "all",
                "status": status_value or "all",
                "ownerId": owner_value,
                "keyword": keyword_value,
            },
        }
    )


@router.get("/{projectId}/risks/page-data", summary="风险页聚合数据")
def get_project_risks_page(projectId: str):
    risks = _risk_items(projectId)
    return _mock.api_response(
        {
            "project": _mock.project_lite(projectId),
            "summary": _risk_summary(risks),
            "resourceHeatmap": _resource_heatmap(_mock.today(), 21),
            "risks": risks,
            "filters": get_project_risk_options(projectId)["data"],
            "aiInsights": _risk_insights(projectId),
            "permissions": ["project:risk:read", "project:risk:update", "project:risk:resolve", "project:risk:export"],
            "updatedAt": _mock.now_iso(),
        }
    )


@router.post("/{projectId}/risks", summary="新建风险")
def create_project_risk(projectId: str, payload: dict[str, Any] = Body(...)):
    name = str(payload.get("name") or payload.get("title") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail={"code": "RISK_VALIDATE_FAILED", "message": "请输入风险名称"})
    risk = _risk_from_payload(projectId, payload, risk_id=_mock.make_id("risk"))
    return _mock.api_response({"riskId": risk["riskId"], "risk": risk})


@router.put("/{projectId}/risks/{riskId}", summary="更新风险")
def update_project_risk(projectId: str, riskId: str, payload: dict[str, Any] = Body(...)):
    risk = _risk_from_payload(projectId, payload, risk_id=riskId)
    risk["version"] = int(payload.get("version", 1)) + 1
    risk["updatedAt"] = _mock.now_iso()
    return _mock.api_response({"projectId": projectId, "riskId": riskId, "risk": risk, "updatedAt": risk["updatedAt"]})


@router.post("/{projectId}/risks/{riskId}/transition", summary="风险状态流转")
def transition_project_risk(projectId: str, riskId: str, payload: dict[str, Any] = Body(...)):
    to_status = payload.get("toStatus") or payload.get("status") or "processing"
    if to_status in {"mitigated", "closed"} and not str(payload.get("mitigationPlan") or "").strip():
        raise HTTPException(status_code=400, detail={"code": "RISK_MITIGATION_REQUIRED", "message": "请填写处理方案"})
    return _mock.api_response(
        {
            "projectId": projectId,
            "riskId": riskId,
            "status": to_status,
            "statusLabel": STATUS_LABELS.get(to_status, to_status),
            "mitigationPlan": payload.get("mitigationPlan"),
            "ownerId": payload.get("ownerId"),
            "version": int(payload.get("version", 1)) + 1,
            "updatedAt": _mock.now_iso(),
            "handledAt": _mock.now_iso(),
        }
    )


@router.post("/{projectId}/risks/batch-resolve", summary="批量处理风险")
def batch_resolve_project_risks(projectId: str, payload: dict[str, Any] = Body(...)):
    risk_ids = payload.get("riskIds", [])
    if not isinstance(risk_ids, list) or not risk_ids:
        raise HTTPException(status_code=400, detail={"code": "RISK_IDS_REQUIRED", "message": "请选择风险项"})
    status = payload.get("status", "mitigated")
    return _mock.api_response(
        {
            "projectId": projectId,
            "riskIds": risk_ids,
            "status": status,
            "statusLabel": STATUS_LABELS.get(status, status),
            "successCount": len(risk_ids),
            "failed": [],
            "skipped": [],
            "resolvedAt": _mock.now_iso(),
        }
    )


@router.post("/{projectId}/risks/export", summary="导出风险清单")
def export_project_risks(projectId: str, payload: dict[str, Any] | None = Body(default=None)):
    task = _mock.export_task("risk_export")
    task["projectId"] = projectId
    task["filters"] = payload or {}
    task["fileType"] = (payload or {}).get("fileType", "xlsx")
    return _mock.api_response(task)


@ai_router.get("/project-risk-insights", summary="AI 风险洞察")
def get_project_risk_insights(
    projectId: str | None = Query(default=None),
    context: str | None = Query(default="risk"),
):
    return _mock.api_response(
        {
            "projectId": _plain_query_value(projectId),
            "context": _plain_query_value(context, "risk") or "risk",
            "insights": _risk_insights(_plain_query_value(projectId)),
            "generatedAt": _mock.now_iso(),
        }
    )


@ai_router.post("/project-risk-insights/{insightId}/apply", summary="采纳 AI 风险建议")
def apply_project_risk_insight(insightId: str, payload: dict[str, Any] | None = Body(default=None)):
    body = payload or {}
    action_key = body.get("actionKey", "coordinate_resource")
    return _mock.api_response(
        {
            "insightId": insightId,
            "actionKey": action_key,
            "applied": True,
            "createdReportTaskId": _mock.make_id("risk_report") if action_key == "generate_report" else None,
            "updatedRiskIds": body.get("riskIds", ["risk_001"]),
            "message": "已采纳风险洞察，并同步风险看板刷新标记。",
            "appliedAt": _mock.now_iso(),
        }
    )


def _risk_items(project_id: str) -> list[dict[str, Any]]:
    users = _mock.users()
    items = []
    for index, risk in enumerate(_mock.risks()):
        level = "critical" if risk["id"] == "risk_001" else risk.get("level", "medium")
        owner = next((item for item in users if item["id"] == risk.get("ownerId")), users[index % len(users)])
        task_id = risk.get("relatedTaskId") or f"task_{index + 1:03d}"
        block_rate = 68 if level in {"critical", "high"} else 42
        items.append(
            {
                "riskId": risk["id"],
                "id": risk["id"],
                "taskId": task_id,
                "projectId": project_id,
                "name": risk.get("title", "未命名风险"),
                "title": risk.get("title", "未命名风险"),
                "level": level,
                "levelLabel": LEVEL_LABELS.get(level, level),
                "factor": "环境准备冲突" if index == 0 else "样本数据不完整",
                "blockRate": block_rate,
                "owner": {"id": owner["id"], "name": owner["name"], "avatar": owner.get("avatar")},
                "ownerId": owner["id"],
                "ownerName": owner["name"],
                "status": risk.get("status", "open"),
                "statusLabel": STATUS_LABELS.get(risk.get("status", "open"), risk.get("status", "open")),
                "dueDate": (_safe_date(_mock.today()) + timedelta(days=index + 1)).isoformat(),
                "mitigationPlan": risk.get("mitigation") or "协调测试窗口并拆分回灌任务",
                "impact": risk.get("impact"),
                "source": "kanban_blocked" if index == 0 else "gantt_delay",
                "version": index + 2,
                "createdAt": risk.get("createdAt", _mock.now_iso()),
                "updatedAt": _mock.now_iso(),
            }
        )
    return items


def _risk_from_payload(project_id: str, payload: dict[str, Any], risk_id: str) -> dict[str, Any]:
    level = payload.get("level", "medium")
    owner = _user_by_id(payload.get("ownerId"))
    return {
        "riskId": risk_id,
        "id": risk_id,
        "projectId": project_id,
        "taskId": payload.get("taskId"),
        "name": payload.get("name") or payload.get("title") or "未命名风险",
        "title": payload.get("title") or payload.get("name") or "未命名风险",
        "level": level,
        "levelLabel": LEVEL_LABELS.get(level, level),
        "factor": payload.get("factor", "人工标记风险"),
        "blockRate": int(payload.get("blockRate", 30) or 0),
        "owner": {"id": owner["id"], "name": owner["name"], "avatar": owner.get("avatar")},
        "ownerId": owner["id"],
        "status": payload.get("status", "open"),
        "statusLabel": STATUS_LABELS.get(payload.get("status", "open"), payload.get("status", "open")),
        "dueDate": payload.get("dueDate"),
        "mitigationPlan": payload.get("mitigationPlan") or payload.get("mitigation"),
        "impact": payload.get("impact"),
        "source": payload.get("source", "manual"),
        "version": int(payload.get("version", 1)),
        "createdAt": _mock.now_iso(),
    }


def _risk_summary(risks: list[dict[str, Any]]) -> dict[str, Any]:
    high_count = len([item for item in risks if item["level"] in {"high", "critical"}])
    medium_count = len([item for item in risks if item["level"] == "medium"])
    open_count = len([item for item in risks if item["status"] == "open"])
    processing_count = len([item for item in risks if item["status"] == "processing"])
    stability_rate = max(0, 100 - high_count * 9 - medium_count * 4 - processing_count * 3)
    return {
        "highRiskTaskCount": high_count,
        "highRiskDelta": 2,
        "mediumWarningCount": medium_count,
        "stabilityRate": stability_rate,
        "open": open_count,
        "processing": processing_count,
        "highOrCritical": high_count,
        "updatedAt": _mock.now_iso(),
    }


def _resource_heatmap(start_date: str, days: int) -> list[dict[str, Any]]:
    base = _safe_date(start_date)
    labels = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    cells = []
    for index in range(days):
        day = base + timedelta(days=index)
        conflict_rate = [34, 48, 86, 57, 72, 21, 18][index % 7]
        level = min(5, max(1, round(conflict_rate / 20)))
        cells.append(
            {
                "date": day.isoformat(),
                "dayLabel": labels[day.weekday()],
                "conflictRate": conflict_rate,
                "level": level,
                "sourceCount": max(1, level - 1),
                "description": "测试窗口冲突" if conflict_rate >= 70 else "低负载" if conflict_rate < 40 else "资源存在交叉",
            }
        )
    return cells


def _risk_insights(project_id: str | None) -> list[dict[str, Any]]:
    return [
        {
            "insightId": "insight_001",
            "id": "insight_001",
            "projectId": project_id,
            "title": "预测 · 概率 92%",
            "content": "由于联调环境参数回灌与样本误差回归验证共用同一测试窗口，周三将出现成员冲突。",
            "confidence": 0.92,
            "actions": [
                {"key": "coordinate_resource", "label": "一键协调资源"},
                {"key": "generate_report", "label": "生成完整风险报告"},
            ],
        },
        {
            "insightId": "insight_002",
            "id": "insight_002",
            "projectId": project_id,
            "title": "根因 · 阻塞链路集中",
            "content": "阻塞主要集中在环境窗口和评审资源，建议同步甘特排期和看板负责人。",
            "confidence": 0.84,
            "actions": [{"key": "sync_schedule", "label": "同步排期风险"}],
        },
    ]


def _user_by_id(user_id: str | None) -> dict[str, Any]:
    users = _mock.users()
    return next((item for item in users if item["id"] == user_id), users[0])


def _safe_date(value: Any) -> date:
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return date.fromisoformat(_mock.today())


def _plain_query_value(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if value.__class__.__module__.startswith("fastapi.params"):
        return default
    return value
