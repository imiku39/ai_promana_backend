from typing import Any

from pydantic import BaseModel, Field


def body_to_dict(payload: BaseModel | dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, BaseModel):
        return payload.model_dump(exclude_none=True)
    return dict(payload)


class RefreshSessionRequest(BaseModel):
    refreshToken: str | None = Field(None, description="登录响应返回的 refreshToken")

    model_config = {"json_schema_extra": {"example": {"refreshToken": "jwt_refresh_token"}}}


class UserSettingsUpdateRequest(BaseModel):
    profile: dict[str, Any] | None = Field(None, description="个人资料，如姓名、部门和头像")
    notifications: dict[str, bool] | None = Field(None, description="通知偏好开关")
    aiPrefs: dict[str, bool] | None = Field(None, description="AI 偏好开关")
    version: int | None = Field(None, description="设置版本号")

    model_config = {
        "json_schema_extra": {
            "example": {
                "profile": {"name": "张工", "department": "研发中心"},
                "notifications": {"taskStatus": True, "logFeedback": True, "reportSubscription": False},
                "aiPrefs": {"autoSummary": True, "scheduling": True, "riskAlert": False},
                "version": 3,
            }
        }
    }


class SettingsResetRequest(BaseModel):
    sections: list[str] | None = Field(None, description="需要恢复默认的设置分组，如 notifications、aiPrefs、profile")
    version: int | None = Field(None, description="当前设置版本号")

    model_config = {"json_schema_extra": {"example": {"sections": ["notifications", "aiPrefs"], "version": 3}}}


class ChangePasswordRequest(BaseModel):
    oldPassword: str = Field(..., description="原密码")
    newPassword: str = Field(..., min_length=8, description="新密码")
    confirmPassword: str | None = Field(None, description="确认新密码")
    revokeOtherSessions: bool = Field(True, description="是否下线其他设备")

    model_config = {"json_schema_extra": {"example": {"oldPassword": "OldPassword123", "newPassword": "NewPassword123", "confirmPassword": "NewPassword123", "revokeOtherSessions": True}}}


class SystemConfigUpdateRequest(BaseModel):
    config: dict[str, Any] | None = Field(None, description="系统配置对象")
    settings: dict[str, Any] | None = Field(None, description="兼容字段，等同 config")
    version: int | None = Field(None, description="配置版本号")
    remark: str | None = Field(None, description="修改说明")

    model_config = {"json_schema_extra": {"example": {"settings": {"siteNotice": True, "wecomPush": True, "auditTrail": True}, "version": 3, "remark": "更新通知配置"}}}


class SystemConfigResetRequest(BaseModel):
    keys: list[str] | None = Field(None, description="需要恢复默认的配置 key")
    config: dict[str, Any] | None = Field(None, description="当前配置对象")
    settings: dict[str, Any] | None = Field(None, description="兼容字段，等同 config")
    version: int | None = Field(None, description="配置版本号")

    model_config = {"json_schema_extra": {"example": {"keys": ["siteNotice"], "version": 3}}}


class NotificationChannelsUpdateRequest(BaseModel):
    channels: list[dict[str, Any]] | None = Field(None, description="通知通道配置列表")
    version: int | None = Field(None, description="配置版本号")

    model_config = {"json_schema_extra": {"example": {"channels": [{"channel": "in_app", "enabled": True}, {"channel": "wecom", "enabled": False}], "version": 2}}}


class ExportRequest(BaseModel):
    fileType: str | None = Field(None, description="导出文件类型，如 xlsx、csv、pdf")
    filters: dict[str, Any] | None = Field(None, description="导出筛选条件")
    columns: list[str] | None = Field(None, description="需要导出的字段")

    model_config = {"json_schema_extra": {"example": {"fileType": "xlsx", "filters": {"status": "active"}, "columns": ["name", "status", "createdAt"]}}}


class AiApplyRequest(BaseModel):
    actionKey: str | None = Field(None, description="采纳动作 key")
    projectIds: list[str] | None = Field(None, description="相关项目 ID")
    notificationIds: list[str] | None = Field(None, description="相关通知 ID")
    taskIds: list[str] | None = Field(None, description="相关任务 ID")
    adjustments: list[dict[str, Any]] | None = Field(None, description="调整明细")
    payload: dict[str, Any] | None = Field(None, description="扩展参数")

    model_config = {"json_schema_extra": {"example": {"actionKey": "apply", "projectIds": ["project_001"], "payload": {"source": "ai_drawer"}}}}


class ProjectWriteRequest(BaseModel):
    code: str | None = Field(None, description="项目编号")
    name: str | None = Field(None, description="项目名称")
    description: str | None = Field(None, description="项目描述")
    projectType: str | None = Field(None, description="项目类型")
    status: str | None = Field(None, description="项目状态")
    priority: str | None = Field(None, description="优先级")
    startDate: str | None = Field(None, description="开始日期")
    endDate: str | None = Field(None, description="结束日期")
    ownerId: str | None = Field(None, description="负责人 ID")
    memberIds: list[str] | None = Field(None, description="初始成员 ID")
    enabledPages: list[str] | None = Field(None, description="启用子页面")
    templateId: str | None = Field(None, description="项目模板 ID")
    version: int | None = Field(None, description="项目版本号")

    model_config = {"json_schema_extra": {"example": {"code": "RD-2026-001", "name": "材料稳定性验证", "description": "验证样品热稳定性", "projectType": "research", "priority": "P1", "startDate": "2026-05-01", "endDate": "2026-06-30", "ownerId": "u_10001", "memberIds": ["u_10002"], "enabledPages": ["overview", "kanban", "docs"], "templateId": "tpl_research", "version": 1}}}


class ProjectArchiveRequest(BaseModel):
    reason: str | None = Field(None, description="归档原因")

    model_config = {"json_schema_extra": {"example": {"reason": "项目已完成并验收"}}}


class ProjectBaselineRequest(BaseModel):
    name: str | None = Field(None, description="基线名称")
    remark: str | None = Field(None, description="基线说明")

    model_config = {"json_schema_extra": {"example": {"name": "联调前基线", "remark": "用于对比后续排期偏移"}}}


class MemberInviteRequest(BaseModel):
    userIds: list[str] | None = Field(None, description="被邀请用户 ID")
    memberIds: list[str] | None = Field(None, description="兼容字段，成员 ID")
    projectRole: str | None = Field(None, description="项目角色")
    role: str | None = Field(None, description="兼容字段，项目角色")
    message: str | None = Field(None, description="邀请备注")
    notifyChannels: list[str] | None = Field(None, description="通知通道")

    model_config = {"json_schema_extra": {"example": {"userIds": ["u_10002", "u_10003"], "projectRole": "dev", "message": "邀请加入项目", "notifyChannels": ["in_app", "wecom"]}}}


class MemberUpdateRequest(BaseModel):
    projectRole: str | None = Field(None, description="项目角色")
    role: str | None = Field(None, description="兼容字段，项目角色")
    status: str | None = Field(None, description="成员状态")
    joinStatus: str | None = Field(None, description="加入状态")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"projectRole": "reviewer", "status": "active", "joinStatus": "joined", "version": 1}}}


class ScheduleItemUpdateRequest(BaseModel):
    plannedStart: str | None = Field(None, description="计划开始日期")
    plannedEnd: str | None = Field(None, description="计划结束日期")
    startDate: str | None = Field(None, description="兼容字段，开始日期")
    endDate: str | None = Field(None, description="兼容字段，结束日期")
    ownerId: str | None = Field(None, description="负责人 ID")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"plannedStart": "2026-05-20", "plannedEnd": "2026-05-28", "ownerId": "u_10001", "version": 1}}}


class DependenciesSaveRequest(BaseModel):
    dependencies: list[dict[str, Any]] = Field(default_factory=list, description="任务依赖关系列表")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"dependencies": [{"sourceTaskId": "task_001", "targetTaskId": "task_002", "type": "finish_to_start"}], "version": 1}}}


class TaskWriteRequest(BaseModel):
    title: str | None = Field(None, description="任务标题")
    description: str | None = Field(None, description="任务描述")
    projectId: str | None = Field(None, description="所属项目 ID")
    assigneeId: str | None = Field(None, description="负责人 ID")
    priority: str | None = Field(None, description="优先级")
    status: str | None = Field(None, description="任务状态")
    columnKey: str | None = Field(None, description="看板列 key")
    dueAt: str | None = Field(None, description="截止时间")
    startDate: str | None = Field(None, description="开始日期")
    tags: list[str] | None = Field(None, description="标签")
    estimateHours: float | None = Field(None, description="预估工时")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"title": "完成接口联调", "description": "补齐注册登录接口", "projectId": "project_001", "assigneeId": "u_10001", "priority": "P1", "status": "todo", "dueAt": "2026-05-25T18:00:00+08:00", "tags": ["backend"], "estimateHours": 6, "version": 1}}}


class TaskTransitionRequest(BaseModel):
    status: str | None = Field(None, description="目标状态")
    columnKey: str | None = Field(None, description="目标看板列")
    reason: str | None = Field(None, description="流转原因")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"status": "doing", "columnKey": "doing", "reason": "开始处理", "version": 1}}}


class TaskCommentRequest(BaseModel):
    content: str = Field(..., description="评论内容")
    mentionedUserIds: list[str] | None = Field(None, description="被提及用户 ID")

    model_config = {"json_schema_extra": {"example": {"content": "接口字段已补齐，请协助联调。", "mentionedUserIds": ["u_10002"]}}}


class SubtaskCreateRequest(BaseModel):
    title: str = Field(..., description="子任务标题")
    assigneeId: str | None = Field(None, description="负责人 ID")
    sortOrder: int | None = Field(None, description="排序值")

    model_config = {"json_schema_extra": {"example": {"title": "整理 Swagger 示例", "assigneeId": "u_10001", "sortOrder": 6000}}}


class SubtaskUpdateRequest(BaseModel):
    completed: bool = Field(True, description="是否完成")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"completed": True, "version": 1}}}


class KanbanOrderRequest(BaseModel):
    taskId: str | None = Field(None, description="任务 ID")
    fromColumn: str | None = Field(None, description="原看板列")
    toColumn: str | None = Field(None, description="目标看板列")
    orderedTaskIds: list[str] | None = Field(None, description="排序后的任务 ID")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"taskId": "task_001", "fromColumn": "todo", "toColumn": "doing", "orderedTaskIds": ["task_002", "task_001"], "version": 1}}}


class RiskWriteRequest(BaseModel):
    title: str | None = Field(None, description="风险标题")
    description: str | None = Field(None, description="风险描述")
    level: str | None = Field(None, description="风险等级")
    probability: str | None = Field(None, description="发生概率")
    impact: str | None = Field(None, description="影响程度")
    ownerId: str | None = Field(None, description="负责人 ID")
    dueDate: str | None = Field(None, description="处理截止日期")
    mitigation: str | None = Field(None, description="缓解措施")
    status: str | None = Field(None, description="风险状态")
    relatedTaskIds: list[str] | None = Field(None, description="关联任务 ID")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"title": "接口联调延期", "description": "登录接口字段需补充", "level": "high", "probability": "medium", "impact": "high", "ownerId": "u_10001", "dueDate": "2026-05-28", "mitigation": "优先补齐 Swagger 入参", "status": "open", "relatedTaskIds": ["task_001"], "version": 1}}}


class RiskTransitionRequest(BaseModel):
    status: str = Field(..., description="目标风险状态")
    reason: str | None = Field(None, description="状态变更原因")
    resolution: str | None = Field(None, description="解决说明")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"status": "resolved", "reason": "接口已补齐", "resolution": "测试通过", "version": 1}}}


class RiskBatchResolveRequest(BaseModel):
    riskIds: list[str] = Field(default_factory=list, description="风险 ID 列表")
    resolution: str | None = Field(None, description="批量处理说明")
    status: str = Field("resolved", description="处理后的状态")

    model_config = {"json_schema_extra": {"example": {"riskIds": ["risk_001", "risk_002"], "resolution": "已统一处理", "status": "resolved"}}}


class DocumentWriteRequest(BaseModel):
    title: str | None = Field(None, description="文档标题")
    content: str | None = Field(None, description="文档正文")
    category: str | None = Field(None, description="文档分类")
    tags: list[str] | None = Field(None, description="标签")
    status: str | None = Field(None, description="文档状态")
    ownerId: str | None = Field(None, description="负责人 ID")
    summary: str | None = Field(None, description="摘要")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"title": "接口联调说明", "content": "本文档记录登录注册接口字段。", "category": "api", "tags": ["backend", "swagger"], "status": "draft", "ownerId": "u_10001", "summary": "接口字段说明", "version": 1}}}


class DocumentSummaryRequest(BaseModel):
    summaryType: str = Field("brief", description="摘要类型")
    saveToDoc: bool = Field(True, description="是否保存回文档")

    model_config = {"json_schema_extra": {"example": {"summaryType": "brief", "saveToDoc": True}}}


class NotificationReadBatchRequest(BaseModel):
    notificationIds: list[str] | None = Field(None, description="通知 ID 列表")
    scope: str | None = Field(None, description="批量范围，如 all、current_filter")

    model_config = {"json_schema_extra": {"example": {"notificationIds": ["notice-role-change"], "scope": "current_filter"}}}


class NotificationHandleRequest(BaseModel):
    actionKey: str | None = Field(None, description="处理动作 key")
    action: str | None = Field(None, description="兼容字段，处理动作")
    remark: str | None = Field(None, description="处理备注")

    model_config = {"json_schema_extra": {"example": {"actionKey": "view_detail", "remark": "已处理"}}}


class NotificationPreferencesUpdateRequest(BaseModel):
    inApp: bool | None = Field(None, description="是否启用站内通知")
    wecom: bool | None = Field(None, description="是否启用企业微信通知")
    categories: dict[str, bool] | None = Field(None, description="分类通知偏好")
    quietHours: dict[str, Any] | None = Field(None, description="免打扰时间")

    model_config = {"json_schema_extra": {"example": {"inApp": True, "wecom": True, "categories": {"task": True, "risk": True, "report": False}, "quietHours": {"enabled": True, "start": "22:00", "end": "08:00"}}}}


class WorkbenchLogRequest(BaseModel):
    content: str | None = Field(None, description="今日日志内容")
    blockers: list[str] | None = Field(None, description="阻塞项")
    nextPlan: str | None = Field(None, description="下一步计划")
    taskIds: list[str] | None = Field(None, description="关联任务 ID")
    mood: str | None = Field(None, description="工作状态")

    model_config = {"json_schema_extra": {"example": {"content": "完成登录注册接口模型补齐", "blockers": ["等待数据库账号"], "nextPlan": "继续补项目接口", "taskIds": ["task_001"], "mood": "focused"}}}


class PbcBindTasksRequest(BaseModel):
    taskIds: list[str] = Field(default_factory=list, description="绑定到目标的任务 ID")
    replace: bool = Field(False, description="是否替换已有绑定")

    model_config = {"json_schema_extra": {"example": {"taskIds": ["task_001", "task_002"], "replace": False}}}


class PbcObjectiveRequest(BaseModel):
    title: str | None = Field(None, description="PBC 目标标题")
    description: str | None = Field(None, description="目标说明")
    metric: str | None = Field(None, description="衡量指标")
    targetValue: str | None = Field(None, description="目标值")
    weight: int | None = Field(None, description="权重")
    dueDate: str | None = Field(None, description="截止日期")

    model_config = {"json_schema_extra": {"example": {"title": "提升接口可测性", "description": "补齐 Swagger 请求体", "metric": "泛型 body 数量", "targetValue": "0", "weight": 30, "dueDate": "2026-05-31"}}}


class AdminUserRequest(BaseModel):
    name: str | None = Field(None, description="姓名")
    phone: str | None = Field(None, description="手机号")
    department: str | None = Field(None, description="部门")
    departmentName: str | None = Field(None, description="部门名称")
    departmentId: str | None = Field(None, description="部门 ID")
    roleKey: str | None = Field(None, description="角色 key")
    platformRole: str | None = Field(None, description="平台角色")
    status: str | None = Field(None, description="用户状态")
    joinDate: str | None = Field(None, description="加入日期")
    sendInvite: bool | None = Field(None, description="是否发送邀请")
    version: int | None = Field(None, description="版本号")
    note: str | None = Field(None, description="备注")

    model_config = {"json_schema_extra": {"example": {"name": "赵经理", "phone": "13800138000", "department": "产品中心", "departmentName": "产品中心", "departmentId": "dept_product", "roleKey": "user", "status": "pending", "joinDate": "2026-05-19", "sendInvite": True, "version": 1}}}


class UserImportCommitRequest(BaseModel):
    importTaskId: str | None = Field(None, description="导入预览任务 ID")
    fileName: str | None = Field(None, description="导入文件名")
    rows: list[dict[str, Any]] | None = Field(None, description="确认导入的行数据")

    model_config = {"json_schema_extra": {"example": {"importTaskId": "imp_001", "fileName": "users.xlsx", "rows": [{"name": "赵经理", "roleKey": "user"}]}}}


class RoleTemplateRequest(BaseModel):
    name: str | None = Field(None, description="角色模板名称")
    description: str | None = Field(None, description="模板说明")
    permissions: list[str] | None = Field(None, description="权限 key 列表")
    scope: str | None = Field(None, description="适用范围")
    builtIn: bool | None = Field(None, description="是否内置")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"name": "项目评审员", "description": "可查看并评审项目", "permissions": ["project:read", "task:update"], "scope": "project", "builtIn": False, "version": 1}}}


class RoleTemplateCopyRequest(BaseModel):
    sourceTemplateId: str | None = Field(None, description="源模板 ID")
    name: str | None = Field(None, description="新模板名称")

    model_config = {"json_schema_extra": {"example": {"sourceTemplateId": "role_tpl_001", "name": "项目评审员副本"}}}


class ProjectTemplateRequest(BaseModel):
    name: str | None = Field(None, description="项目模板名称")
    description: str | None = Field(None, description="模板说明")
    projectType: str | None = Field(None, description="项目类型")
    enabledPages: list[str] | None = Field(None, description="默认启用页面")
    stages: list[dict[str, Any]] | None = Field(None, description="阶段配置")
    taskTemplates: list[dict[str, Any]] | None = Field(None, description="任务模板")
    version: int | None = Field(None, description="版本号")

    model_config = {"json_schema_extra": {"example": {"name": "研发项目模板", "description": "适用于研发验证项目", "projectType": "research", "enabledPages": ["overview", "kanban", "docs"], "stages": [{"name": "启动", "days": 3}], "taskTemplates": [{"title": "需求确认"}], "version": 1}}}


class ReportSubscriptionRequest(BaseModel):
    reportType: str | None = Field(None, description="报表类型")
    cycle: str | None = Field(None, description="订阅周期")
    receiverIds: list[str] | None = Field(None, description="接收人 ID")
    channels: list[str] | None = Field(None, description="通知通道")
    enabled: bool = Field(True, description="是否启用")

    model_config = {"json_schema_extra": {"example": {"reportType": "weekly", "cycle": "weekly_monday", "receiverIds": ["u_10001"], "channels": ["in_app", "wecom"], "enabled": True}}}


class AiFeedbackRequest(BaseModel):
    targetType: str | None = Field(None, description="反馈目标类型")
    targetId: str | None = Field(None, description="反馈目标 ID")
    rating: int | None = Field(None, description="评分")
    content: str | None = Field(None, description="反馈内容")

    model_config = {"json_schema_extra": {"example": {"targetType": "daily_report", "targetId": "report_001", "rating": 5, "content": "建议准确"}}}
