# 全局工作台后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Dashboard.vue`

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 全局工作台 |
| 前端路由 | `/dashboard` |
| 前端文件 | `src/views/Dashboard.vue` |
| 所属模块 | 全局工作台 / 项目协同入口 / AI 简报 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 作为研发管理系统登录后的主入口，聚合用户待办、AI 智能简报、团队效率、最近动态、项目健康度和环境运行指标。
- 支持从工作台快速跳转项目列表、个人工作台、全局报表、系统设置、后台管理和通知中心。
- 支持生成 / 查看 / 导出 AI 晨报。
- 支持通过弹窗快速创建项目草稿或正式项目。
- 支持打开全局 AI 助手，查看建议、风险提示、日报摘要和 PBC 对齐提醒。

### 2.2 对接范围

- 工作台首屏聚合数据接口。
- 当前登录用户信息和顶部通知未读数。
- 全局搜索接口。
- 我的待办列表接口。
- 最近动态列表接口。
- 项目健康度接口。
- 平台运行指标接口。
- AI 智能简报、AI 晨报生成、晨报导出接口。
- 新建项目弹窗中的基础字段、选项字典、模板、AI 创建建议、保存草稿、创建项目接口。
- AI 助手建议获取与采纳接口。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Projects.vue` | 工作台新建项目后可进入项目列表或项目详情 |
| `Workbench.vue` | “进入个人工作台”“查看全部待办”跳转目标 |
| `Reports.vue` | 全局报表入口和晨报导出相关 |
| `Notifications.vue` | 顶部通知中心入口，依赖未读数 |
| `Settings.vue` | 系统设置入口 |
| `admin/AdminHome.vue` | 后台管理入口，依赖管理权限 |
| `UserProfileHoverCard.vue` | 当前登录用户信息展示 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增项目 | 可编辑 | 可删除 | 可导出晨报 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全量工作台能力 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 可进入后台管理 |
| 项目负责人 | 是 | 是 | 是 | 否 | 是 | 可创建和管理本人项目 |
| 研发 / QA / 产品 | 是 | 视权限 | 否 | 否 | 视权限 | 主要查看待办与动态 |
| 协作者 | 是 | 否 | 否 | 否 | 否 | 仅查看授权范围内数据 |

### 3.1 权限规则

- 页面入口权限：访问 `/dashboard` 需要有效登录态。
- 按钮级权限：
  - “新建项目”“快速创建任务/项目”需要 `project:create`。
  - “导出晨报”需要 `dashboard:briefing:export`。
  - “生成 AI 日报”需要 `ai:briefing:generate`。
  - “后台管理”入口需要 `admin:access`。
  - “AI 建议一键采纳”需要对应业务写权限，例如 `task:update`、`project:risk:update`。
- 数据范围权限：
  - 普通成员仅返回与本人相关的待办、动态、项目健康度。
  - PM 返回本人负责项目及参与项目。
  - 管理员可查看组织或租户范围数据。
- 敏感字段脱敏规则：工作台不得返回密码、token、密钥、隐私手机号完整值等敏感信息。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片、智能问候 | 是 | `GET /api/auth/me` | 也可包含在聚合接口中 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 当前静态为 5 |
| AI 智能简报 | 首屏核心摘要 | 是 | `GET /api/dashboard/overview` | 包含标题、摘要、更新时间 |
| KPI 汇总 | 完成率、阻塞任务、PBC、活跃项目 | 是 | `GET /api/dashboard/overview` | 工作台主指标 |
| 团队效率趋势 | 右侧趋势卡 | 是 | `GET /api/dashboard/overview` | 含趋势、说明、标签 |
| 我的待办 | 待办卡片列表 | 是 | `GET /api/dashboard/overview` 或 `GET /api/tasks/my-todos` | 首页只展示 Top 3 |
| 最近动态 | 时间线 | 是 | `GET /api/dashboard/overview` 或 `GET /api/activities/recent` | 首页只展示 Top 3 |
| 项目健康度 | 项目健康进度 | 是 | `GET /api/dashboard/overview` | 首页展示关键项目 |
| 平台运行指标 | 温湿度、算力在线率、安全运行天数 | 是 | `GET /api/dashboard/overview` | 可来自监控系统 |
| 项目创建选项 | 弹窗下拉、模板、推荐负责人 | 否 | `GET /api/projects/create-options` | 打开弹窗时加载 |
| AI 助手建议 | 抽屉建议列表 | 否 | `GET /api/ai/dashboard-suggestions` | 打开抽屉时加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 页面骨架 / 局部加载 | 聚合数据请求中 | 当前加载动画已注释，后续可补局部状态 |
| empty | 空卡片 | 无待办、无动态或无项目 | 各数据块分别处理 |
| error | Toast 或错误占位 | 接口异常或无权限 | 首屏聚合接口失败时展示兜底 |
| partial | 局部缺失 | 部分数据源失败 | 建议聚合接口返回 `warnings` |
| success | 正常渲染 | 数据返回成功 | 默认状态 |

## 5. 字段模型

### 5.1 工作台聚合主对象字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| greeting.title | string | 是 | AI 智能简报标题 | `早上好，张工。今天有 4 个关键事项需要优先关注。` | 个性化问候 |
| greeting.summary | string | 是 | AI 智能简报正文 | `纳米材料项目 A...` | 首页核心摘要 |
| greeting.updatedAt | string | 是 | 更新时间 | `2026-05-11T09:30:00+08:00` | ISO 时间 |
| kpis.todoCompletionRate | number | 是 | 个人待办完成率 | `73` | 百分比，不带 `%` |
| kpis.blockedTaskCount | number | 是 | 阻塞任务 | `2` | 单位：项 |
| kpis.pbcCompletionRate | number | 是 | PBC 达成率 | `64` | 百分比 |
| kpis.activeProjectCount | number | 是 | 活跃项目 | `16` | 单位：个 |
| teamEfficiency.value | number | 是 | 团队效率趋势 | `142` | 百分比 |
| teamEfficiency.progress | number | 是 | 趋势进度条 | `72` | 0-100 |
| teamEfficiency.description | string | 是 | 趋势说明 | `高于近 30 天平均水平...` | 说明文案 |
| teamEfficiency.tags | array | 否 | 标签组 | `["高增长", "低风险"]` | 影响标签展示 |
| todos | array | 是 | 我的待办 | `[]` | 首页 Top N |
| activities | array | 是 | 最近动态 | `[]` | 首页 Top N |
| projectHealth | array | 是 | 项目健康度 | `[]` | 项目健康进度 |
| deliveryConfidence | object | 否 | 整体交付信心 | `{ level: "very_high" }` | 项目健康卡底部 |
| operationMetrics | array | 是 | 底部运行指标 | `[]` | 温湿度、算力、安全天数 |

### 5.2 待办字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 待办项 | `task_001` | 唯一标识 |
| title | string | 是 | 待办标题 | `完成 Q3 实验室能效评估报告` | 任务标题 |
| note | string | 是 | 待办说明 | `截止日期：今天 18:00 · 关联项目：实验基座升级` | 二级说明 |
| status | string | 是 | 图标状态 | `in_progress` | 进行中 / 待审 / 已完成 |
| priority | string | 否 | 标签 | `urgent` | 紧急、待审等 |
| dueAt | string | 否 | 说明或排序 | `2026-05-11T18:00:00+08:00` | 截止时间 |
| projectId | string | 否 | 跳转关联项目 | `project_001` | 关联项目 |
| actionPath | string | 否 | 点击跳转 | `/workbench?tab=kanban` | 后续可支持点击待办 |

### 5.3 最近动态字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 动态项 | `act_001` | 唯一标识 |
| type | string | 是 | 动态类型 | `document_uploaded` | 决定图标和颜色 |
| title | string | 是 | 动态标题 | `新文档上传` | 标题 |
| content | string | 是 | 动态内容 | `碳纳米管合成工艺已存入...` | 描述 |
| occurredAt | string | 是 | 时间 | `2026-05-11T09:20:00+08:00` | 后端返回真实时间，前端转相对时间 |
| color | string | 否 | 时间线圆点颜色 | `primary` | 可由前端按 type 映射 |
| targetPath | string | 否 | 点击跳转 | `/project/1/docs` | 关联目标 |

### 5.4 项目健康度字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | string | 是 | 项目健康项 | `project_001` | 项目 ID |
| projectName | string | 是 | 项目名称 | `核心实验室` | 展示名称 |
| progress | number | 是 | 进度条 | `85` | 0-100 |
| health | string | 是 | 颜色语义 | `good` | 良好 / 风险 / 严重 |
| note | string | 否 | 项目说明 | `进度稳步推进` | 二级说明 |

### 5.5 新建项目字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | string | 是 | 项目名称 | `新型复合材料热稳定性验证` | 项目主标题 |
| code | string | 是 | 项目编号 | `RD-2026-318` | 需唯一 |
| teamId | string | 是 | 归属团队 | `team_material` | 从团队字典选择 |
| ownerId | string | 是 | 项目负责人 | `u_10001` | 从用户列表选择 |
| estimatedMemberCount | number | 否 | 预计成员数 | `8` | 数字，不带单位 |
| templateId | string | 是 | 项目模板 | `requirement_iteration` | 模板 ID |
| startDate | string | 是 | 开始日期 | `2026-05-06` | 日期 |
| deadline | string | 是 | 截止日期 | `2026-06-20` | 日期 |
| status | string | 是 | 项目状态 | `in_progress` | 默认进行中 |
| health | string | 是 | 健康度 | `good` | 默认良好 |
| initialProgress | number | 是 | 初始完成度 | `0` | 0-100 |
| priority | string | 否 | 项目优先级 | `P1` | P0-P3 |
| riskSyncEnabled | boolean | 否 | 风险同步 | `true` | 是否开启 |
| reportSubscriptionCycle | string | 否 | 报告订阅 | `weekly_monday` | 订阅频率 |
| defaultView | string | 否 | 默认详情入口 | `overview` | 概览、看板、甘特 |
| summary | string | 否 | 项目摘要 | `围绕新型复合材料...` | 多行文本 |
| tags | string[] | 否 | 项目标签 | `["结构迭代", "性能验证"]` | 标签数组 |
| memberIds | string[] | 否 | 核心成员 | `["u_1", "u_2"]` | 用户 ID 数组 |
| subscriberIds | string[] | 否 | 报告订阅人 | `["role_pm", "role_qa"]` | 用户或角色 |
| riskReminderFrequency | string | 否 | 风险提醒频率 | `daily` | 每日 / 每周 / 异常 |
| initMode | string | 否 | 模板初始化 | `auto_structure` | 自动结构 / 空白 / 复制 |
| enabledPages | string[] | 否 | 启用详情页 | `["overview","kanban","gantt","risk","reports"]` | 详情页入口 |
| notifyAllMembers | boolean | 否 | 通知全员 | `false` | 创建后是否通知 |

### 5.6 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| taskStatus | `in_progress` | 进行中 | primary | 待办进行中 |
| taskStatus | `pending_review` | 待审 | warning | 审批或评审中 |
| taskStatus | `done` | 已完成 | success | 已完成 |
| priority | `P0` | P0 | danger | 最高优先级 |
| priority | `P1` | P1 | warning | 高优先级 |
| priority | `P2` | P2 | primary | 中优先级 |
| priority | `P3` | P3 | neutral | 低优先级 |
| projectStatus | `in_progress` | 进行中 | success | 默认 |
| projectStatus | `pending` | 待启动 | neutral | 未开始 |
| projectStatus | `paused` | 已暂停 | warning | 暂停 |
| health | `good` | 良好 | success | 健康 |
| health | `risk` | 风险 | warning | 存在风险 |
| health | `critical` | 严重 | danger | 严重 |
| reportSubscriptionCycle | `weekly_monday` | 每周一 | neutral | 周报订阅 |
| riskReminderFrequency | `daily` | 每日同步 | neutral | 风险提醒 |
| riskReminderFrequency | `weekly` | 每周同步 | neutral | 风险提醒 |
| riskReminderFrequency | `exception_only` | 仅异常提醒 | warning | 风险提醒 |

### 5.7 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| todoCompletionRate | number | 本人今日或本周期已完成待办 / 总待办 | AI 简报 KPI | 口径需确认 |
| blockedTaskCount | number | 当前用户可见阻塞任务数 | AI 简报 KPI | 包含项目范围待办 |
| pbcCompletionRate | number | 当前用户 PBC 目标完成度 | AI 简报 KPI | PBC 系统提供 |
| activeProjectCount | number | 当前用户可见活跃项目数 | AI 简报 KPI | 状态为进行中或待启动 |
| teamEfficiency.value | number | 团队效率指数 | 团队效率趋势 | 算法口径需后端/数据确认 |
| computeNodeOnlineRate | number | 在线算力节点 / 总节点 | 运行指标 | 来自监控 |
| safeRunningDays | number | 距最近 P1 安全事件天数 | 运行指标 | 来自安全事件系统 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取工作台聚合数据 | GET | `/api/dashboard/overview` | 首屏所有卡片数据 | P0 |
| API-002 | 全局搜索 | GET | `/api/search` | 搜索项目、任务、成员、报表 | P1 |
| API-003 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部通知角标 | P0 |
| API-004 | 生成 AI 日报 | POST | `/api/ai/daily-report/generate` | 点击生成 AI 日报 | P0 |
| API-005 | 获取 AI 日报详情 | GET | `/api/ai/daily-report/latest` | 点击查看 AI 日报 | P1 |
| API-006 | 导出晨报 | POST | `/api/dashboard/morning-report/export` | 导出晨报文件 | P0 |
| API-007 | 获取项目创建选项 | GET | `/api/projects/create-options` | 新建项目弹窗字典、模板、推荐人 | P0 |
| API-008 | 保存项目草稿 | POST | `/api/projects/drafts` | 弹窗保存草稿 | P0 |
| API-009 | 创建项目 | POST | `/api/projects` | 弹窗正式创建项目 | P0 |
| API-010 | 获取 AI 助手建议 | GET | `/api/ai/dashboard-suggestions` | AI 抽屉内容 | P1 |
| API-011 | 采纳 AI 建议 | POST | `/api/ai/suggestions/{suggestionId}/apply` | 一键采纳建议 | P1 |

## 7. 接口详情

### API-001 获取工作台聚合数据

**请求方式**

- Method: `GET`
- Path: `/api/dashboard/overview`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | query | string | 否 | `2026-05-11` | 工作台日期，默认当天 |
| scope | query | string | 否 | `mine` | `mine` / `team` / `org`，按权限生效 |
| timezone | query | string | 否 | `Asia/Shanghai` | 时间区 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user": {
      "id": "u_10001",
      "name": "张工",
      "roleName": "研发总监",
      "avatar": "https://example.com/avatar.png"
    },
    "greeting": {
      "title": "早上好，张工。今天有 4 个关键事项需要优先关注。",
      "summary": "纳米材料项目 A 的合成实验成功率本周提升 12%，但“联调验证”里程碑相对基线已延后 2 天。",
      "updatedAt": "2026-05-11T09:30:00+08:00"
    },
    "kpis": {
      "todoCompletionRate": 73,
      "blockedTaskCount": 2,
      "pbcCompletionRate": 64,
      "activeProjectCount": 16
    },
    "teamEfficiency": {
      "value": 142,
      "progress": 72,
      "description": "高于近 30 天平均水平 15.4%，AI 判断主要受自动化测试改造和日报生成效率提升影响。",
      "tags": [
        { "label": "高增长", "type": "primary" },
        { "label": "低风险", "type": "tertiary" },
        { "label": "AI 推荐保持", "type": "success" }
      ]
    },
    "todos": [
      {
        "id": "task_001",
        "title": "完成 Q3 实验室能效评估报告",
        "note": "截止日期：今天 18:00 · 关联项目：实验基座升级",
        "status": "in_progress",
        "priority": "urgent",
        "dueAt": "2026-05-11T18:00:00+08:00",
        "actionPath": "/workbench?tab=kanban"
      }
    ],
    "activities": [
      {
        "id": "act_001",
        "type": "document_uploaded",
        "title": "新文档上传",
        "content": "碳纳米管合成工艺已存入项目文档库，关联至项目 A 的第三阶段验证。",
        "occurredAt": "2026-05-11T09:20:00+08:00",
        "targetPath": "/project/1/docs"
      }
    ],
    "projectHealth": [
      {
        "projectId": "project_001",
        "projectName": "核心实验室",
        "progress": 85,
        "health": "good",
        "note": "进度稳步推进"
      }
    ],
    "deliveryConfidence": {
      "level": "very_high",
      "label": "极高",
      "score": 4
    },
    "operationMetrics": [
      {
        "key": "environment",
        "title": "实验室平均温湿度",
        "value": "22.4°C / 45%",
        "description": "关键环境稳定，暂无异常波动。",
        "icon": "thermostat"
      },
      {
        "key": "compute_online_rate",
        "title": "算力节点在线率",
        "value": "99.98%",
        "description": "GPU 集群状态良好，周三夜间有高峰负载。",
        "icon": "memory"
      }
    ],
    "warnings": []
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 未登录 | `401` | 跳转登录 |
| 无权限 | `403` | 展示无权限提示 |
| 部分数据源失败 | `200` + `warnings` | 正常渲染可用数据，局部展示降级 |
| 服务异常 | `500` | 展示错误占位或 Toast |

### API-002 全局搜索

**请求方式**

- Method: `GET`
- Path: `/api/search`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 是 | `纳米材料` | 搜索项目、任务、成员、报表 |
| types | query | string | 否 | `project,task,user,report` | 限定搜索类型 |
| limit | query | number | 否 | `10` | 默认 10 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": "project_001",
      "type": "project",
      "title": "纳米材料项目 A",
      "description": "进行中 · 材料科学部",
      "targetPath": "/project/1"
    }
  ]
}
```

### API-003 获取通知未读数

**请求方式**

- Method: `GET`
- Path: `/api/notifications/unread-count`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "unreadCount": 5
  }
}
```

### API-004 生成 AI 日报

**请求方式**

- Method: `POST`
- Path: `/api/ai/daily-report/generate`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | body | string | 否 | `2026-05-11` | 生成日期 |
| scope | body | string | 否 | `mine` | mine / team / org |
| includeRisk | body | boolean | 否 | `true` | 是否包含风险 |
| includePbc | body | boolean | 否 | `true` | 是否包含 PBC |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reportId": "daily_20260511_001",
    "status": "generated",
    "title": "2026-05-11 AI 晨报",
    "summary": "包含 3 个重点风险、2 个关键进展和 1 个负载建议。",
    "targetPath": "/reports?dailyReportId=daily_20260511_001"
  }
}
```

### API-005 获取 AI 日报详情

**请求方式**

- Method: `GET`
- Path: `/api/ai/daily-report/latest`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | query | string | 否 | `2026-05-11` | 默认当天 |
| scope | query | string | 否 | `mine` | mine / team / org |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reportId": "daily_20260511_001",
    "title": "2026-05-11 AI 晨报",
    "content": "Markdown 或结构化日报内容",
    "generatedAt": "2026-05-11T09:30:00+08:00"
  }
}
```

### API-006 导出晨报

**请求方式**

- Method: `POST`
- Path: `/api/dashboard/morning-report/export`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | body | string | 否 | `2026-05-11` | 导出日期 |
| format | body | string | 否 | `pdf` | `pdf` / `docx` / `markdown` |
| scope | body | string | 否 | `mine` | 数据范围 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "taskId": "export_001",
    "status": "processing",
    "downloadUrl": null
  }
}
```

### API-007 获取项目创建选项

**请求方式**

- Method: `GET`
- Path: `/api/projects/create-options`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "teams": [
      { "id": "team_material", "name": "材料科学部" },
      { "id": "team_platform", "name": "平台组" },
      { "id": "team_physics", "name": "计算物理组" }
    ],
    "owners": [
      { "id": "u_10001", "name": "王志强", "avatar": "https://example.com/a.png" },
      { "id": "u_10002", "name": "陈思远", "avatar": "https://example.com/b.png" }
    ],
    "templates": [
      {
        "id": "requirement_iteration",
        "name": "需求迭代模板",
        "description": "适合需要概览、项目看板、甘特、风险和报表全链路协同的研发项目。",
        "recommended": true
      }
    ],
    "defaultValues": {
      "status": "in_progress",
      "health": "good",
      "priority": "P1",
      "riskSyncEnabled": true,
      "reportSubscriptionCycle": "weekly_monday",
      "defaultView": "overview",
      "enabledPages": ["overview", "kanban", "gantt", "risk", "reports"]
    },
    "aiSuggestions": [
      {
        "title": "优先选择模板",
        "content": "如果是需求迭代类项目，建议优先使用需求评审到验收模板。"
      }
    ]
  }
}
```

### API-008 保存项目草稿

**请求方式**

- Method: `POST`
- Path: `/api/projects/drafts`
- Auth: 是

**请求参数**

请求 body 使用“5.5 新建项目字段”。

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "draftId": "project_draft_001",
    "savedAt": "2026-05-11T10:20:00+08:00"
  }
}
```

### API-009 创建项目

**请求方式**

- Method: `POST`
- Path: `/api/projects`
- Auth: 是

**请求参数**

请求 body 使用“5.5 新建项目字段”。

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "projectId": "project_318",
    "name": "新型复合材料热稳定性验证",
    "code": "RD-2026-318",
    "status": "in_progress",
    "targetPath": "/project/project_318"
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 项目编号重复 | `409 PROJECT_CODE_EXISTS` | 表单提示编号已存在 |
| 日期范围错误 | `400 PROJECT_DATE_INVALID` | 提示截止日期需晚于开始日期 |
| 无创建权限 | `403 PROJECT_CREATE_FORBIDDEN` | 提示无权限 |
| 成员不存在 | `400 PROJECT_MEMBER_INVALID` | 提示成员信息失效 |

### API-010 获取 AI 助手建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/dashboard-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| context | query | string | 否 | `dashboard` | 当前上下文 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "primarySuggestion": {
      "id": "sug_001",
      "title": "今日建议",
      "content": "建议先处理联调验证延期 2 天的里程碑，再安排实验二组负载均衡。",
      "confidence": 0.92,
      "actions": [
        { "key": "apply", "label": "一键采纳" },
        { "key": "manual", "label": "手动调整" }
      ]
    },
    "items": [
      {
        "id": "sug_002",
        "title": "风险提示",
        "subtitle": "92% 置信度",
        "content": "项目 A 的联调节点和材料组算力申请集中在周三，建议提前协调资源窗口。"
      }
    ]
  }
}
```

### API-011 采纳 AI 建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/suggestions/{suggestionId}/apply`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| suggestionId | path | string | 是 | `sug_001` | 建议 ID |
| actionKey | body | string | 是 | `apply` | 动作 |
| context | body | string | 否 | `dashboard` | 来源上下文 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "resultMessage": "已生成资源协调建议，并同步到个人工作台待办。"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入 `/dashboard` | 页面加载 | `GET /api/dashboard/overview` | 当前用户、日期 | 渲染所有卡片 | 错误占位 / Toast |
| 顶部搜索 | 搜索框 | `GET /api/search` | `keyword` | 展示搜索结果 | Toast |
| 点击通知 | 顶部通知按钮 | `GET /api/notifications/unread-count` / 跳转 | 当前用户 | 跳转通知中心 | 无 |
| 点击导出晨报 | 页面头部 | `POST /api/dashboard/morning-report/export` | 日期、范围、格式 | 返回下载任务 | Toast |
| 点击生成 AI 日报 | 页面头部 | `POST /api/ai/daily-report/generate` | 日期、范围 | 生成日报并跳转或 Toast | Toast |
| 点击查看 AI 日报 | 简报按钮 | `GET /api/ai/daily-report/latest` | 日期、范围 | 跳转报表或打开详情 | Toast |
| 点击进入个人工作台 | 简报按钮 | 无 | 固定路由 | 跳转 `/workbench` | 无 |
| 点击查看全部待办 | 待办卡 | 无 | 固定路由 | 跳转 `/workbench?tab=kanban` | 无 |
| 打开新建项目弹窗 | 侧栏按钮 / 快捷按钮 | `GET /api/projects/create-options` | 当前用户 | 渲染弹窗选项 | Toast |
| 保存草稿 | 弹窗按钮 | `POST /api/projects/drafts` | 表单 | Toast 提示已保存 | 表单错误 / Toast |
| 创建项目 | 弹窗按钮 | `POST /api/projects` | 表单 | Toast，跳转项目详情或刷新项目列表 | 表单错误 / Toast |
| 打开 AI 助手 | 悬浮按钮 / 顶部按钮 | `GET /api/ai/dashboard-suggestions` | 当前上下文 | 渲染建议列表 | Toast |
| 一键采纳 AI 建议 | AI 抽屉 | `POST /api/ai/suggestions/{id}/apply` | 建议 ID | Toast，刷新相关数据 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| name | input | 是 | 2-80 字 | 名称非空、长度合法 | 请输入项目名称 |
| code | input | 是 | 仅字母、数字、短横线，最长 64 | 全局唯一 | 项目编号已存在 |
| teamId | select | 是 | 必须在团队列表中 | 团队存在且用户有权限 | 请选择归属团队 |
| ownerId | select | 是 | 必须在负责人列表中 | 用户存在且可成为负责人 | 请选择项目负责人 |
| estimatedMemberCount | input | 否 | 正整数，1-999 | 数值范围合法 | 请输入正确成员数 |
| templateId | card/select | 是 | 必须在模板列表中 | 模板存在且可用 | 请选择项目模板 |
| startDate | date/input | 是 | 日期格式 | 日期合法 | 请选择开始日期 |
| deadline | date/input | 是 | 日期格式，晚于开始日期 | 日期范围合法 | 截止日期需晚于开始日期 |
| status | select | 是 | 枚举值 | 枚举合法 | 请选择项目状态 |
| health | select | 是 | 枚举值 | 枚举合法 | 请选择健康度 |
| initialProgress | input | 是 | 0-100 | 数值范围合法 | 完成度需为 0-100 |
| priority | select/card | 否 | P0-P3 | 枚举合法 | 优先级不合法 |
| summary | textarea | 否 | 最长 1000 字 | 长度合法 | 摘要过长 |
| tags | chip | 否 | 标签数量 0-20 | 标签存在或可创建 | 标签不合法 |
| memberIds | input/select | 否 | 用户 ID 数组 | 成员存在且可加入 | 成员信息无效 |
| subscriberIds | input/select | 否 | 用户或角色 ID 数组 | 订阅对象合法 | 订阅人无效 |
| enabledPages | chip | 否 | 页面枚举数组 | 枚举合法 | 启用页面不合法 |

### 9.1 提交规则

- 是否允许重复提交：不允许，保存草稿和创建项目请求期间按钮应禁用。
- 是否需要二次确认：正式创建项目可不需要；若通知全员为 true，建议二次确认。
- 是否需要审计日志：需要。保存草稿、创建项目、采纳 AI 建议、导出晨报都应记录审计。
- 是否需要乐观锁或版本号：草稿编辑后续若支持更新，建议使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 首页列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 我的待办 | todos | array | 是 | 按优先级和截止时间排序 |
| 最近动态 | activities | array | 是 | 按发生时间倒序 |
| 项目健康度 | projectHealth | array | 是 | 按风险等级或进度排序 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 日期 | date | string | 当天 | 聚合数据日期 |
| 范围 | scope | string | `mine` | mine / team / org |
| 搜索关键词 | keyword | string | 空 | 全局搜索 |
| 搜索类型 | types | string | 全部 | project / task / user / report |

### 10.3 分页规则

- 工作台首屏聚合接口不分页，后端只返回每个卡片的 Top N 数据。
- 我的待办首页建议返回 3-5 条，更多数据跳转个人工作台。
- 最近动态首页建议返回 3-5 条，更多数据后续可接动态中心。
- 全局搜索建议支持 `limit`，默认 10，最大 50。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出晨报 | `POST /api/dashboard/morning-report/export` | pdf / docx / markdown | 不适用 | 异步任务优先 | 返回任务 ID 和下载链接 |
| 下载导出结果 | 待补充：`GET /api/export-tasks/{taskId}` | pdf / docx / markdown | 不适用 | 轮询任务状态 | 可统一复用全局导出任务接口 |
| 新建项目 | 无文件 | 无 | 无 | 同步提交 | 当前弹窗不涉及附件 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 顶部未读数和创建项目通知 |
| AI 智能简报 | 是 | AI 简报服务 | 工作台首屏摘要 |
| AI 日报生成 | 是 | AI 日报服务 | 生成 / 查看 / 导出 |
| AI 创建建议 | 是 | AI 建议服务 | 新建项目弹窗模板和负责人建议 |
| AI 助手抽屉 | 是 | AI 建议服务 | 获取建议列表和采纳 |
| 审计日志 | 是 | 审计日志服务 | 创建项目、导出晨报、采纳 AI 建议 |
| WebSocket / SSE | 否 | 暂无 | 工作台当前不需要实时流式响应 |

## 13. 缓存与实时性

- 数据是否允许缓存：工作台聚合数据可短缓存，建议 30-60 秒。
- 缓存时间：AI 简报可缓存到下一次生成；运行指标建议 1-5 分钟。
- 页面返回时是否刷新：建议刷新工作台聚合数据和通知未读数。
- 是否需要轮询：导出晨报如为异步任务，需要轮询导出任务状态。
- 是否需要 WebSocket / SSE：当前不需要；后续 AI 生成日报若改为流式，可使用 SSE。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `DASHBOARD_PARAM_INVALID` | 参数错误 | Toast 或回退默认参数 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录或 token 过期 | 跳转登录 |
| 403 / `DASHBOARD_FORBIDDEN` | 无工作台权限 | 展示无权限 |
| 403 / `PROJECT_CREATE_FORBIDDEN` | 无项目创建权限 | 隐藏按钮或 Toast |
| 409 / `PROJECT_CODE_EXISTS` | 项目编号重复 | 表单字段错误 |
| 422 / `PROJECT_VALIDATE_FAILED` | 项目表单校验失败 | 展示字段错误 |
| 429 / `AI_RATE_LIMITED` | AI 生成过于频繁 | 提示稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | 展示失败提示 |

## 15. 验收标准

- 进入 `/dashboard` 后，工作台首屏所有静态 mock 数据均可由 `GET /api/dashboard/overview` 或拆分接口真实渲染。
- 顶部用户信息不再硬编码 `张工 / 研发总监`，改为登录态用户信息。
- 通知角标不再硬编码 `5`，改为通知未读数接口。
- “导出晨报”“生成 AI 日报”“查看 AI 日报”均有明确接口和成功 / 失败反馈。
- 新建项目弹窗中的团队、负责人、模板、默认值和 AI 建议可从后端获取。
- 保存草稿和创建项目可以提交完整表单，后端返回项目 ID 或草稿 ID。
- 项目编号重复、日期错误、无权限等情况有明确错误码。
- AI 助手抽屉可获取建议列表，一键采纳后能返回明确结果。
- 后端按当前用户权限返回数据范围，普通成员不可看到未授权项目数据。
- 导出、创建、AI 采纳等关键操作写入审计日志。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | Dashboard 首屏使用一个聚合接口，还是按待办、动态、项目健康度拆分多个接口？ | 前后端 | 待确认 |
| Q2 | “快速创建任务”按钮当前打开的是“新建项目”弹窗，产品语义是否改为“快速创建项目”？ | 产品/前端 | 待确认 |
| Q3 | 团队效率趋势 `142%` 的计算口径由哪个服务提供？ | 后端/数据 | 待确认 |
| Q4 | 实验室温湿度、算力在线率、安全运行天数是否来自真实监控系统？ | 后端/运维 | 待确认 |
| Q5 | AI 日报生成是同步返回结果，还是异步任务/流式生成？ | 后端/AI | 待确认 |
| Q6 | 新建项目时 `核心成员`、`报告订阅人` 输入框后续是自由文本还是选择用户/角色？ | 产品/前后端 | 待确认 |
| Q7 | 创建项目后是否自动跳转项目详情，还是留在工作台并 Toast 提示？ | 产品/前端 | 待确认 |
| Q8 | AI 建议“一键采纳”具体落哪些业务动作：创建待办、调整排期、发送通知还是生成草稿？ | 产品/后端/AI | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`src/views/Dashboard.vue` 模板内大量静态文案与数值。
- 当前用户信息 mock：`currentUser = { name: '张工', role: '研发总监', avatar: ... }`。
- 当前通知未读数：顶部角标静态写死为 `5`。
- 当前“新建项目”弹窗字段使用 HTML `value` 静态值，暂未绑定响应式表单对象。
- 当前“保存草稿”“创建项目”仅调用 `showToast`，未提交接口。
- 当前 AI 助手抽屉为静态文案，“一键采纳”“手动调整”未绑定业务接口。
- 当前搜索框仅展示输入框，未绑定搜索接口。
- 当前“导出晨报”“生成 AI 日报”“查看 AI 日报”按钮未绑定接口。
- 建议后续前端接入时先将静态卡片数据抽象为 `dashboardData`，再替换为接口响应。
