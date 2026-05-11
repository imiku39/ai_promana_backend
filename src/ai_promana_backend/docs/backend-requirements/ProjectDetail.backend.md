# 项目详情后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/ProjectDetail.vue`  
> 页面定位：项目模块详情承载页，负责项目概览、子页面导航、编辑项目弹窗和项目上下文 AI 助手。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目详情 / 项目概览 |
| 前端路由 | `/project/:id`、`/project/:id/:tab` |
| 前端文件 | `src/views/ProjectDetail.vue` |
| 所属模块 | 项目管理 / 项目详情 / 项目概览 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 作为单个项目的总工作区入口，展示项目基础信息、状态、负责人、周期、进度、健康度和成员数。
- 通过二级导航切换概览、成员、项目看板、甘特图、风险看板、报表、文档。
- 概览页展示里程碑、基线偏差预警、本周任务、成员负载和风险摘要。
- 支持编辑项目基础信息、计划状态、成员说明、订阅人和同步开关。
- 根据当前 tab 展示项目上下文 AI 建议。

### 2.2 对接范围

- 项目详情头部信息和可用 tab。
- 项目概览聚合数据：里程碑、本周任务、基线偏差、成员负载、风险摘要、AI 建议。
- 编辑项目弹窗的详情查询、草稿保存和正式保存。
- 项目归档、设置基线、通知未读数、当前用户信息。
- AI 助手上下文建议、采纳 AI 动作、AI 反馈。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Projects.vue` | 从项目矩阵点击项目进入详情 |
| `ProjectMembers.vue` | 成员子页面，当前路由主要由 `ProjectDetail.vue` tab 承载 |
| `ProjectKanban.vue` | 看板子页面，当前路由主要由 `ProjectDetail.vue` tab 承载 |
| `ProjectGantt.vue` | 甘特图子页面，当前路由主要由 `ProjectDetail.vue` tab 承载 |
| `ProjectRisk.vue` | 风险子页面，当前路由主要由 `ProjectDetail.vue` tab 承载 |
| `ProjectReports.vue` | 报表子页面，当前路由主要由 `ProjectDetail.vue` tab 承载 |
| `ProjectDocs.vue` | 文档子页面，当前路由主要由 `ProjectDetail.vue` tab 承载 |
| `Notifications.vue` | 顶部通知入口 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全量项目权限 |
| 管理员 | 是 | 视权限 | 是 | 视权限 | 是 | 按组织范围 |
| 项目负责人 | 是 | 是 | 是 | 否 | 是 | 可编辑本人负责项目 |
| 项目成员 | 是 | 否 | 视权限 | 否 | 视权限 | 按项目角色控制 |
| 访客 / 协作者 | 是 | 否 | 否 | 否 | 否 | 只读授权数据 |

### 3.1 权限规则

- 页面入口权限：访问 `/project/:id` 需要登录态和 `project:read`。
- 数据范围权限：只能查看当前用户可见项目；无权项目返回 `403 PROJECT_FORBIDDEN`，不存在返回 `404 PROJECT_NOT_FOUND`。
- 按钮级权限：
  - “编辑项目”需要 `project:update`。
  - “归档项目”需要 `project:archive`，建议二次确认。
  - “设置基线”需要 `project:baseline:update`。
  - “保存草稿”需要 `project:draft:update`。
  - “保存变更”需要 `project:update`。
  - AI 采纳动作需要 `ai:project-suggestion:apply`，并校验实际业务写权限。
- 敏感字段脱敏规则：无权限用户不返回预算明细、成员联系方式、审计备注、内部风险根因原始记录。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 可由全局状态提供 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 当前静态为 5 |
| 项目详情头部 | 页面标题、摘要、KPI | 是 | `GET /api/projects/{projectId}` | 当前为 `project` mock |
| 项目可用 tab | 子导航权限控制 | 是 | `GET /api/projects/{projectId}/entry` | 也可随详情返回 |
| 概览聚合数据 | 概览 tab 主体 | 是 | `GET /api/projects/{projectId}/overview` | 里程碑、任务、负载、风险 |
| 编辑项目详情 | 编辑弹窗表单 | 否 | `GET /api/projects/{projectId}/edit-form` | 打开弹窗时加载 |
| AI 助手建议 | AI 抽屉 | 否 | `GET /api/ai/project-suggestions` | 按 tab 上下文获取 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 页面骨架 / 局部加载 | 请求处理中 | 加载动画当前保留但注释 |
| empty | 无项目或无概览数据 | 数据为空 | 按区块展示空状态 |
| error | Toast / 错误占位 | 接口异常或无权限 | 需返回标准错误结构 |
| readonly | 按钮隐藏或禁用 | 用户无写权限 | 后端返回 permissions |
| editing | 编辑弹窗打开 | 查询编辑表单 | 弹窗数据可局部加载 |

## 5. 字段模型

### 5.1 项目详情字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 路由参数、接口参数 | `project_001` | 项目 ID |
| name | string | 是 | 标题、面包屑 | `纳米晶体结构优化` | 项目名称 |
| code | string | 是 | 编辑弹窗 | `MAT-2026-0414` | 项目编号 |
| description | string | 否 | 项目摘要 | `聚焦晶体结构...` | 项目说明 |
| owner.id | string | 是 | 负责人 | `u_10001` | 负责人 ID |
| owner.name | string | 是 | 负责人 | `王志强` | 负责人名称 |
| department | string | 否 | 编辑弹窗 | `材料科学部` | 归属团队 |
| templateId | string | 否 | 模板标签 | `requirement_iteration` | 项目模板 |
| templateName | string | 否 | 模板标签 | `需求迭代模板` | 模板名称 |
| status | string | 是 | 状态标签 | `in_progress` | 项目状态 |
| health | string | 是 | 健康度 | `good` | 健康度枚举 |
| progress | number | 是 | 进度 KPI | `72` | 0-100 |
| startDate | string | 是 | 时间范围 | `2026-04-14` | 开始日期 |
| endDate | string | 是 | 时间范围 | `2026-05-16` | 结束日期 |
| currentStage | string | 否 | 编辑弹窗 | `integration` | 当前阶段 |
| memberCount | number | 是 | 成员数 | `12` | 成员数 |
| baselineVersion | string | 否 | 编辑弹窗 / 甘特 | `V2` | 当前基线 |
| permissions | string[] | 是 | 按钮控制 | `["project:update"]` | 当前用户权限 |
| enabledTabs | string[] | 是 | 子导航 | `["overview","members"]` | 可见 tab |
| version | number | 是 | 保存编辑 | `7` | 乐观锁版本 |

### 5.2 概览聚合字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| milestones | array | 是 | 里程碑时间线 | `[]` | 项目里程碑 |
| baselineWarning | object | 否 | 基线偏差预警 | `{ "delayDays": 2 }` | 基线偏差 |
| weeklyTasks | array | 是 | 本周任务进展 | `[]` | 任务摘要 |
| workloadGroups | array | 是 | 成员负载概览 | `[]` | 按组或成员 |
| riskSummary | array | 是 | 风险摘要标签 | `[]` | 风险文案 |
| aiSuggestion | object | 否 | AI 项目建议 | `{}` | 概览页 AI 卡片 |

### 5.3 编辑项目表单字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | string | 是 | 项目名称 | `纳米晶体结构优化` | 2-80 字 |
| code | string | 是 | 项目编号 | `MAT-2026-0414` | 唯一 |
| templateId | string | 是 | 项目模板 | `requirement_iteration` | 模板 ID |
| ownerId | string | 是 | 项目负责人 | `u_10001` | 用户 ID |
| teamId | string | 是 | 归属团队 | `team_material` | 团队 ID |
| startDate | string | 是 | 开始日期 | `2026-04-14` | 日期 |
| endDate | string | 是 | 结束日期 | `2026-05-16` | 日期 |
| currentStage | string | 是 | 当前阶段 | `integration` | 枚举 |
| health | string | 是 | 健康度 | `good` | 枚举 |
| progress | number | 是 | 进度百分比 | `72` | 0-100 |
| stageNote | string | 否 | 阶段说明 | `当前阶段...` | 最长 1000 字 |
| memberIds | string[] | 否 | 核心成员 | `["u_1"]` | 成员 ID |
| subscriberIds | string[] | 否 | 报告订阅人 | `["role_pm"]` | 用户或角色 |
| bio | string | 否 | 项目简介 | `聚焦晶体结构...` | 最长 2000 字 |
| syncOptions | object | 否 | 同步开关 | `{ "kanban": true }` | 是否同步子页 |
| version | number | 是 | 隐藏字段 | `7` | 乐观锁 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| tab | `overview` | 概览 | active | 默认 tab |
| tab | `members` | 成员 | active | 成员子页 |
| tab | `kanban` | 项目看板 | active | 看板子页 |
| tab | `gantt` | 项目甘特图 | active | 甘特子页 |
| tab | `risk` | 风险看板 | active | 风险子页 |
| tab | `reports` | 报表 | active | 报表子页 |
| tab | `docs` | 文档 | active | 文档子页 |
| projectStatus | `in_progress` | 进行中 | success | 正在推进 |
| projectStatus | `archived` | 已归档 | neutral | 归档 |
| health | `good` | 良好 | success | 正常 |
| health | `warning` | 需关注 | warning | 轻度风险 |
| health | `critical` | 高风险 | danger | 严重风险 |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| progress | number | 已完成任务权重 / 全部任务权重 | 头部 KPI | 需确认权重口径 |
| memberCount | number | 当前有效项目成员数 | 头部 KPI | 是否含待接受需确认 |
| delayDays | number | 当前计划结束日期 - 基线结束日期 | 基线偏差预警 | 正数为延期 |
| recoverableDays | number | AI 或排期服务估算可追回时间 | 预警卡片 | P1 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取项目详情 | GET | `/api/projects/{projectId}` | 详情头部、权限、tab | P0 |
| API-002 | 获取项目概览聚合 | GET | `/api/projects/{projectId}/overview` | 概览 tab 数据 | P0 |
| API-003 | 获取项目编辑表单 | GET | `/api/projects/{projectId}/edit-form` | 编辑弹窗初始化 | P0 |
| API-004 | 保存项目编辑草稿 | POST | `/api/projects/{projectId}/draft` | 保存草稿 | P1 |
| API-005 | 更新项目配置 | PUT | `/api/projects/{projectId}` | 保存变更 | P0 |
| API-006 | 归档项目 | POST | `/api/projects/{projectId}/archive` | 归档项目 | P1 |
| API-007 | 设置项目基线 | POST | `/api/projects/{projectId}/baseline` | 设置基线 | P1 |
| API-008 | 获取项目 AI 建议 | GET | `/api/ai/project-suggestions` | AI 抽屉 | P1 |
| API-009 | 采纳项目 AI 建议 | POST | `/api/ai/project-suggestions/{suggestionId}/apply` | AI 动作 | P1 |
| API-010 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部角标 | P0 |

## 7. 接口详情

### API-001 获取项目详情

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | path | string | 是 | `project_001` | 项目 ID |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "project_001",
    "name": "纳米晶体结构优化",
    "code": "MAT-2026-0414",
    "description": "聚焦晶体结构稳定性与模型预测精度提升。",
    "owner": { "id": "u_10001", "name": "王志强", "avatar": "https://example.com/u.png" },
    "team": { "id": "team_material", "name": "材料科学部" },
    "template": { "id": "requirement_iteration", "name": "需求迭代模板" },
    "status": "in_progress",
    "health": "good",
    "progress": 72,
    "startDate": "2026-04-14",
    "endDate": "2026-05-16",
    "currentStage": "integration",
    "memberCount": 12,
    "baselineVersion": "V2",
    "enabledTabs": ["overview", "members", "kanban", "gantt", "risk", "reports", "docs"],
    "permissions": ["project:read", "project:update", "project:baseline:update"],
    "version": 7
  }
}
```

### API-002 获取项目概览聚合

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/overview`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | path | string | 是 | `project_001` | 项目 ID |
| date | query | string | 否 | `2026-05-11` | 统计日期 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "milestones": [
      {
        "id": "m_1",
        "title": "需求评审",
        "description": "已完成，结论已沉淀到项目文档。",
        "status": "completed",
        "plannedDate": "2026-04-18",
        "actualDate": "2026-04-18"
      }
    ],
    "baselineWarning": {
      "status": "warning",
      "delayDays": 2,
      "progressDeviationRate": 6,
      "recoverableDays": 0.8,
      "description": "当前实际进度较最新基线落后 6%。"
    },
    "weeklyTasks": [
      {
        "id": "task_1",
        "title": "完成回归样本对齐与误差校验",
        "ownerName": "韩诚",
        "status": "in_progress",
        "deadlineText": "今天完成",
        "blockedReason": null
      }
    ],
    "workloadGroups": [
      { "name": "平台组", "loadRate": 86, "level": "warning" }
    ],
    "riskSummary": [
      { "label": "资源调度冲突", "level": "warning" },
      { "label": "联调节点延后 2 天", "level": "danger" }
    ],
    "aiSuggestion": {
      "id": "sug_overview_001",
      "title": "AI 项目建议",
      "content": "建议将数据回灌校验拆分为独立子任务。"
    }
  }
}
```

### API-003 获取项目编辑表单

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/edit-form`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "form": {
      "name": "纳米晶体结构优化",
      "code": "MAT-2026-0414",
      "templateId": "requirement_iteration",
      "ownerId": "u_10001",
      "teamId": "team_material",
      "startDate": "2026-04-14",
      "endDate": "2026-05-16",
      "currentStage": "integration",
      "health": "good",
      "progress": 72,
      "stageNote": "当前阶段集中处理联调验证中的时间偏差。",
      "memberIds": ["u_10001", "u_10002"],
      "subscriberIds": ["role_pm", "role_qa"],
      "bio": "聚焦晶体结构稳定性与模型预测精度提升。",
      "syncOptions": {
        "highlightOverview": true,
        "syncKanban": true,
        "syncGantt": true,
        "syncRisk": true,
        "notifyMembers": false
      },
      "version": 7
    },
    "options": {
      "templates": [],
      "owners": [],
      "teams": [],
      "stages": [],
      "healthOptions": []
    },
    "editSuggestions": [
      {
        "title": "优先同步基线与时间窗",
        "content": "建议将联调验证偏差写入项目摘要。"
      }
    ]
  }
}
```

### API-005 更新项目配置

**请求方式**

- Method: `PUT`
- Path: `/api/projects/{projectId}`
- Auth: 是

**请求参数**

请求 body 使用“5.3 编辑项目表单字段”。

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "projectId": "project_001",
    "version": 8,
    "updatedAt": "2026-05-11T10:30:00+08:00",
    "changedFields": ["health", "stageNote", "syncOptions"]
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 项目不存在 | `404 PROJECT_NOT_FOUND` | 返回项目列表或展示不存在 |
| 无编辑权限 | `403 PROJECT_UPDATE_FORBIDDEN` | 隐藏按钮或 Toast |
| 编号重复 | `409 PROJECT_CODE_EXISTS` | 表单字段错误 |
| 版本冲突 | `409 PROJECT_VERSION_CONFLICT` | 提示刷新后重试 |
| 日期错误 | `400 PROJECT_DATE_INVALID` | 字段错误 |

### API-008 获取项目 AI 建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/project-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | query | string | 是 | `project_001` | 项目 ID |
| context | query | string | 是 | `overview` | 当前 tab |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "context": "overview",
    "card": {
      "id": "sug_overview_001",
      "title": "根因分析",
      "content": "联调验证延期的主要原因是测试环境准备与数据回灌窗口重叠。",
      "primaryAction": { "key": "create_task", "label": "生成子任务" },
      "secondaryAction": { "key": "view_baseline", "label": "查看基线对比" }
    },
    "list": [
      {
        "id": "sug_overview_002",
        "title": "项目健康预测",
        "content": "若本周三前恢复联调，项目健康度仍可维持良好。",
        "confidence": 0.88
      }
    ]
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入项目详情 | 路由加载 | `GET /api/projects/{id}`、`GET /api/projects/{id}/overview` | route.params.id | 渲染头部和概览 | 错误占位 |
| 切换 tab | 子导航 | 子页面对应接口 | route.params.tab | 渲染子页 | Toast / 空状态 |
| 点击返回 | 顶部返回 | 无 | - | 跳转 `/projects` | - |
| 打开编辑项目 | 侧边按钮 | `GET /api/projects/{id}/edit-form` | projectId | 打开弹窗 | Toast |
| 保存草稿 | 编辑弹窗 | `POST /api/projects/{id}/draft` | 表单 | Toast | 表单错误 |
| 保存变更 | 编辑弹窗 | `PUT /api/projects/{id}` | 表单 | Toast，刷新详情 | 表单错误 |
| 归档项目 | 页面按钮 | `POST /api/projects/{id}/archive` | projectId | Toast，返回列表 | Toast |
| 设置基线 | 页面按钮 | `POST /api/projects/{id}/baseline` | projectId、版本 | Toast，刷新甘特/概览 | Toast |
| 打开 AI 助手 | 顶部/悬浮按钮 | `GET /api/ai/project-suggestions` | projectId、currentTab | 渲染建议 | Toast |
| 采纳 AI 建议 | AI 抽屉 | `POST /api/ai/project-suggestions/{id}/apply` | suggestionId、actionKey | Toast，刷新关联区块 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| name | input | 是 | 2-80 字 | 名称合法 | 请输入项目名称 |
| code | input | 是 | 字母、数字、短横线 | 唯一性 | 项目编号已存在 |
| templateId | select | 是 | 选项内 | 模板可用 | 请选择项目模板 |
| ownerId | select | 是 | 用户存在 | 用户可成为负责人 | 请选择负责人 |
| teamId | select | 是 | 团队存在 | 用户有团队权限 | 请选择归属团队 |
| startDate | date/input | 是 | 日期格式 | 日期合法 | 请选择开始日期 |
| endDate | date/input | 是 | 晚于开始日期 | 日期范围合法 | 结束日期需晚于开始日期 |
| health | select | 是 | 枚举 | 枚举合法 | 请选择健康度 |
| progress | input | 是 | 0-100 | 数值合法 | 进度需为 0-100 |
| stageNote | textarea | 否 | 最长 1000 字 | 长度合法 | 阶段说明过长 |
| memberIds | selector | 否 | 用户数组 | 成员可加入 | 成员信息无效 |
| subscriberIds | selector | 否 | 用户/角色数组 | 对象存在 | 订阅人无效 |
| bio | textarea | 否 | 最长 2000 字 | 长度合法 | 项目简介过长 |

### 9.1 提交规则

- 是否允许重复提交：不允许，保存中禁用按钮。
- 是否需要二次确认：归档项目、通知成员、AI 批量生成任务需要二次确认。
- 是否需要审计日志：需要，覆盖编辑、草稿、归档、基线、AI 采纳。
- 是否需要乐观锁或版本号：需要，使用 `version` 防止覆盖他人编辑。

## 10. 列表、筛选、分页与排序

项目详情概览无分页列表；本周任务、里程碑、风险摘要为聚合接口返回。若任务数量较多，可由任务子页面承接分页。

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 里程碑标题 | milestones.title | string | 否 | 按计划时间排序 |
| 任务标题 | weeklyTasks.title | string | 否 | 当前只展示摘要 |
| 负责人 | weeklyTasks.ownerName | string | 否 | 任务负责人 |
| 状态 | weeklyTasks.status | string | 否 | 任务状态 |
| 负载名称 | workloadGroups.name | string | 否 | 组或成员 |
| 负载率 | workloadGroups.loadRate | number | 否 | 0-100 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 统计日期 | date | string | 当天 | 概览统计口径 |
| 当前 tab | context | string | overview | AI 建议上下文 |

### 10.3 分页规则

- 概览聚合接口不分页。
- 本周任务建议最多返回 5-10 条摘要，完整任务列表由看板接口分页或按列返回。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出风险摘要 | `POST /api/projects/{projectId}/risk-summary/export` | md / pdf | 不适用 | 异步任务 | AI 抽屉预留 |
| 导出项目概览 | `POST /api/projects/{projectId}/overview/export` | pdf | 不适用 | 异步任务 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 顶部未读数、编辑通知、基线通知 |
| AI 建议 | 是 | AI 项目助手 | 根据 tab 返回上下文建议 |
| 审计日志 | 是 | 审计日志服务 | 编辑、归档、基线、AI 采纳 |
| WebSocket / SSE | 可选 | 项目事件流 | P2，用于实时任务/风险变更 |

## 13. 缓存与实时性

- 数据是否允许缓存：项目详情可短缓存 30 秒，编辑表单不建议缓存。
- 缓存时间：概览聚合 30-60 秒；AI 建议按上下文短缓存。
- 页面返回时是否刷新：建议刷新项目详情、概览、通知未读数。
- 是否需要轮询：当前不需要。
- 是否需要 WebSocket / SSE：首期可不接；后续任务和风险实时协同可接。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `PROJECT_VALIDATE_FAILED` | 字段校验失败 | 表单错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `PROJECT_FORBIDDEN` | 无项目访问权限 | 无权限提示 |
| 403 / `PROJECT_UPDATE_FORBIDDEN` | 无编辑权限 | 隐藏按钮或 Toast |
| 404 / `PROJECT_NOT_FOUND` | 项目不存在 | 返回列表或空状态 |
| 409 / `PROJECT_CODE_EXISTS` | 项目编号重复 | 字段错误 |
| 409 / `PROJECT_VERSION_CONFLICT` | 版本冲突 | 提示刷新 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast / 错误占位 |

## 15. 验收标准

- `/project/:id` 能通过接口完整渲染项目头部、概览数据和可用 tab。
- 无权限项目不可进入，项目不存在有明确错误态。
- 编辑项目弹窗能从后端加载表单、选项和建议，不再使用静态数据。
- 保存草稿、保存变更、归档项目、设置基线均有接口和错误码支撑。
- 当前用户权限能控制编辑、归档、基线、AI 采纳等按钮展示。
- AI 抽屉能按当前 tab 返回不同上下文建议，并支持采纳动作。
- 概览里程碑、任务、负载、风险摘要字段与前端展示一致。
- 所有写操作记录审计日志，版本冲突不会覆盖他人编辑。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | `/project/:id/:tab` 是否长期统一由 `ProjectDetail.vue` 承载，还是后续改为独立子页组件？ | 前端/产品 | 待确认 |
| Q2 | 项目进度计算口径是任务数量、工时、里程碑权重还是手动录入？ | 产品/后端 | 待确认 |
| Q3 | “设置基线”是生成新版本，还是覆盖当前版本？是否需要审批？ | 产品/后端 | 待确认 |
| Q4 | 编辑项目里的核心成员和报告订阅人是否必须使用组织选择器？ | 前后端 | 待确认 |
| Q5 | AI 建议采纳后的动作边界是生成任务、调整负责人、生成说明还是直接修改项目数据？ | 产品/AI/后端 | 待确认 |

## 17. 前端备注

- 当前 mock 数据位置：`src/views/ProjectDetail.vue` 中 `project`、`milestones`、`weekTasks`、`loads`、`memberList`、`kanbanCols`、`ganttData`、`riskTasks`、`docList`、`editForm`、`aiCards`。
- 当前路由中 `/project/:id` 和 `/project/:id/:tab` 均由 `ProjectDetail.vue` 承载。
- `ProjectMembers.vue`、`ProjectKanban.vue`、`ProjectGantt.vue`、`ProjectRisk.vue`、`ProjectReports.vue`、`ProjectDocs.vue` 文件存在，但当前不是主路由承载组件。
- 当前编辑弹窗保存草稿和保存变更只调用 `showToast`，未接接口。
- 当前 AI 抽屉按钮只展示文案，未接 AI 建议接口。
- 当前通知角标静态为 `5`。
