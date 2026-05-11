# 项目矩阵后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Projects.vue`  
> 页面定位：项目模块主页面，负责项目列表、搜索筛选排序、项目创建入口和进入项目子页面。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目矩阵 / 项目列表 |
| 前端路由 | `/projects` |
| 前端文件 | `src/views/Projects.vue` |
| 所属模块 | 项目管理 / 项目矩阵 / 项目创建 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示当前用户有权限查看的项目矩阵。
- 支持按项目名称、负责人搜索项目。
- 支持按负责人、健康度、截止日期排序。
- 预留全部状态筛选和权重排序能力。
- 展示项目核心摘要：项目名称、部门、编号、标签、完成度、健康度、状态、负责人、截止日期、成员数。
- 展示项目整体统计指标：研发预算、本月新启动实验、累计专利申请量、活跃成员。
- 支持新建项目草稿和创建项目。
- 支持从项目矩阵进入项目详情及 Project 子页面。
- 支持项目矩阵上下文的 AI 助手建议。

### 2.2 对接范围

- 项目列表查询、搜索、筛选、排序、分页。
- 项目矩阵统计指标。
- 顶部当前用户信息和通知未读数。
- 新建项目弹窗所需的团队、负责人、模板、默认值、AI 创建建议。
- 保存项目草稿、创建项目。
- AI 项目矩阵建议获取与采纳。
- 项目主页面到子页面的路由和数据边界。

### 2.3 Project 子页面边界

`Projects.vue` 是项目模块主页面。它只负责展示项目摘要并跳转到项目详情，不负责加载项目详情深层数据。

| 子页面 | 当前路由 | 当前前端承载 | 本页关系 | 后续文档建议 |
| --- | --- | --- | --- | --- |
| 项目概览 | `/project/:id` | `ProjectDetail.vue` | 点击项目行进入 | 单独生成 `ProjectDetail.backend.md` |
| 项目成员 | `/project/:id/members` | `ProjectDetail.vue` tab / 存在 `ProjectMembers.vue` | 子页面入口 | 单独生成 `ProjectMembers.backend.md` |
| 项目看板 | `/project/:id/kanban` | `ProjectDetail.vue` tab / 存在 `ProjectKanban.vue` | 子页面入口 | 单独生成 `ProjectKanban.backend.md` |
| 项目甘特图 | `/project/:id/gantt` | `ProjectDetail.vue` tab / 存在 `ProjectGantt.vue` | 子页面入口 | 单独生成 `ProjectGantt.backend.md` |
| 项目风险 | `/project/:id/risk` | `ProjectDetail.vue` tab / 存在 `ProjectRisk.vue` | 子页面入口 | 单独生成 `ProjectRisk.backend.md` |
| 项目报表 | `/project/:id/reports` | `ProjectDetail.vue` tab / 存在 `ProjectReports.vue` | 子页面入口 | 单独生成 `ProjectReports.backend.md` |
| 项目文档 | `/project/:id/docs` | `ProjectDetail.vue` tab / 存在 `ProjectDocs.vue` | 子页面入口 | 单独生成 `ProjectDocs.backend.md` |

### 2.4 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Dashboard.vue` | 工作台可跳转项目矩阵，也有新建项目入口 |
| `ProjectDetail.vue` | 项目详情和项目子页面当前主要承载组件 |
| `ProjectMembers.vue` | 项目成员子页面文件，当前未在路由中单独挂载 |
| `ProjectKanban.vue` | 项目看板子页面文件，当前未在路由中单独挂载 |
| `ProjectGantt.vue` | 项目甘特子页面文件，当前未在路由中单独挂载 |
| `ProjectRisk.vue` | 项目风险子页面文件，当前未在路由中单独挂载 |
| `ProjectReports.vue` | 项目报表子页面文件，当前未在路由中单独挂载 |
| `ProjectDocs.vue` | 项目文档子页面文件，当前未在路由中单独挂载 |
| `Notifications.vue` | 顶部通知入口 |
| `UserProfileHoverCard.vue` | 当前用户信息展示 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 可查看全部项目 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 按组织范围查看 |
| 项目负责人 | 是 | 是 | 是 | 否 | 是 | 查看本人负责及参与项目 |
| 研发 / QA / 产品 | 是 | 视权限 | 否 | 否 | 否 | 查看参与项目 |
| 协作者 | 是 | 否 | 否 | 否 | 否 | 仅查看授权项目 |

### 3.1 权限规则

- 页面入口权限：访问 `/projects` 需要有效登录态。
- 数据范围权限：
  - 超级管理员可查看全量项目。
  - 管理员按组织、部门或租户范围查看。
  - 项目负责人可查看本人负责和参与的项目。
  - 普通成员只查看参与或被授权的项目。
- 按钮级权限：
  - “新建项目”需要 `project:create`。
  - “保存草稿”需要 `project:draft:create`。
  - “创建项目”需要 `project:create`。
  - 项目行更多菜单后续如接入编辑、归档、删除，分别需要 `project:update`、`project:archive`、`project:delete`。
  - AI 建议采纳需要 `ai:project-suggestion:apply`，如建议会改动项目数据，还需要对应业务写权限。
- 敏感字段脱敏规则：列表不返回未授权项目预算明细、敏感文档、审批密钥、成员隐私信息等。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 可由全局状态提供 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 当前静态为 5 |
| 活跃成员摘要 | 页面头部头像栈和人数 | 是 | `GET /api/projects/summary` | 当前静态为 12 位活跃成员 |
| 项目列表 | 项目矩阵主体 | 是 | `GET /api/projects` | 支持搜索、筛选、排序、分页 |
| 项目统计指标 | 预算、新启动实验、专利申请量 | 是 | `GET /api/projects/summary` | 当前静态展示 |
| 创建项目选项 | 弹窗下拉、模板、推荐负责人 | 否 | `GET /api/projects/create-options` | 打开弹窗时加载 |
| AI 助手建议 | AI 抽屉内容 | 否 | `GET /api/ai/project-matrix-suggestions` | 打开抽屉时加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 列表加载中 / 局部骨架 | 请求处理中 | 当前页面未接入 loading |
| empty | 项目列表为空 | 无可见项目或筛选无结果 | 后续需补空状态 |
| error | Toast 或错误占位 | 接口异常或无权限 | 后续接入 |
| searching | 搜索结果 | keyword 生效 | 当前为本地 computed |
| sorted | 排序结果 | sortField / sortOrder 生效 | 后续可服务端排序 |
| modalOpen | 新建项目弹窗打开 | 加载创建选项 | 当前为静态字段 |

## 5. 字段模型

### 5.1 项目列表字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string / number | 是 | 项目行 key、详情跳转 | `1` | 项目唯一 ID |
| name | string | 是 | 项目名称 | `纳米晶体结构优化` | 项目名称 |
| department | string | 是 | 项目副信息 | `材料科学部` | 归属部门 |
| code | string | 是 | 项目编号 | `RD-2026-089` | 项目编号，需唯一 |
| tags | string[] | 是 | 项目标签 | `["结构迭代", "AI 预测"]` | 标签列表 |
| progress | number | 是 | 完成度进度条 | `72` | 0-100 |
| health | string | 是 | 健康度标签 | `good` | 建议返回枚举，前端映射中文 |
| healthLabel | string | 是 | 健康度中文 | `良好` | 展示文案 |
| status | string | 是 | 项目状态 | `in_progress` | 进行中、暂停、归档等 |
| statusLabel | string | 是 | 状态中文 | `进行中` | 展示文案 |
| owner.id | string | 是 | 负责人 | `u_10001` | 用户 ID |
| owner.name | string | 是 | 负责人姓名 | `王志强` | 展示 |
| owner.avatar | string | 否 | 负责人头像 | `https://...` | 头像 |
| deadline | string | 是 | 截止日期 | `2026-05-16` | 日期 |
| memberCount | number | 是 | 成员数 | `12` | 项目成员数 |
| colorSemantic | string | 否 | 色彩语义 | `primary` | 前端按健康度或项目色映射 |
| detailPath | string | 否 | 点击跳转 | `/project/1` | 可由前端拼接 |

### 5.2 项目统计字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| activeMemberCount | number | 是 | 头部活跃成员 | `12` | 活跃成员数 |
| activeMemberAvatars | array | 否 | 头像栈 | `[]` | 最多返回 3-5 个头像 |
| rdBudgetAmount | number | 是 | 研发预算分配 | `12400000` | 单位建议为元 |
| rdBudgetDisplay | string | 否 | 展示文案 | `¥ 12.4M` | 可前端格式化 |
| rdBudgetTrendRate | number | 否 | 较上周趋势 | `4.2` | 百分比 |
| rdBudgetUsageRate | number | 否 | 预算进度条 | `60` | 0-100 |
| monthlyNewExperimentCount | number | 是 | 本月新启动实验 | `24` | 数量 |
| patentApplicationTotal | number | 是 | 累计专利申请量 | `182` | 数量 |

### 5.3 新建项目字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | string | 是 | 项目名称 | `新型复合材料热稳定性验证` | 项目主标题 |
| code | string | 是 | 项目编号 | `RD-2026-318` | 需唯一 |
| teamId | string | 是 | 归属团队 | `team_material` | 团队 ID |
| ownerId | string | 是 | 项目负责人 | `u_10001` | 用户 ID |
| estimatedMemberCount | number | 否 | 预计成员数 | `8` | 数字 |
| templateId | string | 是 | 项目模板 | `requirement_iteration` | 模板 ID |
| startDate | string | 是 | 开始日期 | `2026-05-06` | 日期 |
| deadline | string | 是 | 截止日期 | `2026-06-20` | 日期 |
| status | string | 是 | 项目状态 | `in_progress` | 默认进行中 |
| health | string | 是 | 健康度 | `good` | 默认良好 |
| initialProgress | number | 是 | 初始完成度 | `0` | 0-100 |
| priority | string | 否 | 项目优先级 | `P1` | P0-P3 |
| riskSyncEnabled | boolean | 否 | 风险同步 | `true` | 是否开启 |
| reportSubscriptionCycle | string | 否 | 报告订阅 | `weekly_monday` | 订阅频率 |
| defaultView | string | 否 | 默认详情入口 | `overview` | 概览 / 看板 / 甘特 |
| summary | string | 否 | 项目摘要 | `围绕新型复合材料...` | 多行文本 |
| tags | string[] | 否 | 标签 | `["结构迭代", "性能验证"]` | 标签数组 |
| memberIds | string[] | 否 | 核心成员 | `["u_1","u_2"]` | 成员用户 ID |
| subscriberIds | string[] | 否 | 报告订阅人 | `["role_pm","role_qa"]` | 用户或角色 |
| riskReminderFrequency | string | 否 | 风险提醒频率 | `daily` | daily / weekly / exception_only |
| initMode | string | 否 | 模板初始化 | `auto_structure` | 自动结构 / 空白 / 复制 |
| enabledPages | string[] | 否 | 启用子页面 | `["overview","kanban","gantt","risk","reports"]` | 决定项目详情入口 |
| notifyAllMembers | boolean | 否 | 通知全员 | `false` | 创建后是否通知 |

### 5.4 Project 子页面入口字段

| 字段名 | 类型 | 必填 | 前端用途 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | string | 是 | 子页面 path 参数 | `project_001` | 项目 ID |
| defaultView | string | 否 | 默认进入子页 | `overview` | 默认 `/project/:id` |
| enabledPages | string[] | 是 | 控制详情页 tab | `["overview","members","kanban","gantt","risk","reports","docs"]` | 后端可返回可用子页 |
| permissions | string[] | 否 | 控制子页按钮 | `["project:member:read"]` | 子页详细权限 |

### 5.5 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| projectStatus | `in_progress` | 进行中 | success | 正在进行 |
| projectStatus | `pending` | 待启动 | neutral | 未开始 |
| projectStatus | `paused` | 已暂停 | warning | 暂停 |
| projectStatus | `archived` | 已归档 | neutral | 归档 |
| health | `completed` | 完成 | success | 已完成或已交付 |
| health | `good` | 良好 | success | 健康 |
| health | `risk` | 风险 | warning | 存在风险 |
| health | `critical` | 严重 | danger | 严重风险 |
| sortField | `owner` | 负责人 | - | 按负责人排序 |
| sortField | `health` | 健康度 | - | 按健康度排序 |
| sortField | `deadline` | 截止日期 | - | 按截止日期排序 |
| sortOrder | `asc` | 升序 | - | 升序 |
| sortOrder | `desc` | 降序 | - | 降序 |

### 5.6 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| activeMemberCount | number | 近 N 天参与活跃项目的成员数 | 头部活跃成员 | N 需确认 |
| rdBudgetAmount | number | 当前用户可见项目预算总额 | 研发预算卡 | 金额权限需确认 |
| monthlyNewExperimentCount | number | 本月新启动且可见的实验/项目数 | 本月新启动实验 | 是否只含实验需确认 |
| patentApplicationTotal | number | 当前范围累计专利申请量 | 专利申请量卡 | 数据源需确认 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取项目矩阵统计 | GET | `/api/projects/summary` | 页面头部和底部统计卡 | P0 |
| API-002 | 获取项目列表 | GET | `/api/projects` | 项目矩阵列表、搜索、筛选、排序 | P0 |
| API-003 | 获取项目创建选项 | GET | `/api/projects/create-options` | 新建项目弹窗字典、模板、推荐负责人 | P0 |
| API-004 | 保存项目草稿 | POST | `/api/projects/drafts` | 保存弹窗草稿 | P0 |
| API-005 | 创建项目 | POST | `/api/projects` | 正式创建项目 | P0 |
| API-006 | 获取项目详情入口配置 | GET | `/api/projects/{projectId}/entry` | 进入项目详情前获取可用子页 | P1 |
| API-007 | 获取 AI 项目矩阵建议 | GET | `/api/ai/project-matrix-suggestions` | AI 抽屉内容 | P1 |
| API-008 | 采纳 AI 项目建议 | POST | `/api/ai/project-suggestions/{suggestionId}/apply` | 一键采纳建议 | P1 |
| API-009 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部通知角标 | P0 |

## 7. 接口详情

### API-001 获取项目矩阵统计

**请求方式**

- Method: `GET`
- Path: `/api/projects/summary`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| scope | query | string | 否 | `mine` | `mine` / `team` / `org`，按权限生效 |
| date | query | string | 否 | `2026-05-11` | 统计日期 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "activeMemberCount": 12,
    "activeMemberAvatars": [
      { "userId": "u_1", "name": "成员1", "avatar": "https://example.com/a.png" },
      { "userId": "u_2", "name": "成员2", "avatar": "https://example.com/b.png" },
      { "userId": "u_3", "name": "成员3", "avatar": "https://example.com/c.png" }
    ],
    "rdBudgetAmount": 12400000,
    "rdBudgetTrendRate": 4.2,
    "rdBudgetUsageRate": 60,
    "monthlyNewExperimentCount": 24,
    "patentApplicationTotal": 182
  }
}
```

### API-002 获取项目列表

**请求方式**

- Method: `GET`
- Path: `/api/projects`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `纳米` | 按项目名称、编号、负责人搜索 |
| status | query | string | 否 | `in_progress` | 项目状态 |
| health | query | string | 否 | `risk` | 健康度 |
| ownerId | query | string | 否 | `u_10001` | 负责人 |
| tag | query | string | 否 | `AI 预测` | 标签 |
| sortField | query | string | 否 | `deadline` | owner / health / deadline / weight |
| sortOrder | query | string | 否 | `asc` | asc / desc |
| page | query | number | 否 | `1` | 页码 |
| pageSize | query | number | 否 | `20` | 页大小 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "1",
        "name": "纳米晶体结构优化",
        "department": "材料科学部",
        "code": "RD-2026-089",
        "tags": ["结构迭代", "AI 预测"],
        "progress": 72,
        "health": "good",
        "healthLabel": "良好",
        "status": "in_progress",
        "statusLabel": "进行中",
        "owner": {
          "id": "u_10001",
          "name": "王志强",
          "avatar": "https://example.com/avatar/u_10001.png"
        },
        "deadline": "2026-05-16",
        "memberCount": 12,
        "colorSemantic": "primary",
        "detailPath": "/project/1",
        "enabledPages": ["overview", "members", "kanban", "gantt", "risk", "reports", "docs"]
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 4
    }
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 未登录 | `401` | 跳转登录 |
| 无权限 | `403` | 展示无权限 |
| 参数错误 | `400 PROJECT_PARAM_INVALID` | 重置筛选或 Toast |
| 服务异常 | `500` | 展示错误占位 |

### API-003 获取项目创建选项

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
      { "id": "u_10002", "name": "陈思远", "avatar": "https://example.com/b.png" },
      { "id": "u_10003", "name": "周雅楠", "avatar": "https://example.com/c.png" }
    ],
    "templates": [
      {
        "id": "requirement_iteration",
        "name": "需求迭代模板",
        "description": "适合需要概览、项目看板、甘特、风险和报表全链路协同的研发项目。",
        "recommended": true
      },
      {
        "id": "platform_delivery",
        "name": "平台交付模板",
        "description": "强调联调窗口、里程碑节点和负责人资源约束。"
      },
      {
        "id": "experiment_validation",
        "name": "验证实验模板",
        "description": "适合实验验证、样本归档和阶段性结果汇总场景。"
      }
    ],
    "defaultValues": {
      "status": "in_progress",
      "health": "good",
      "priority": "P1",
      "riskSyncEnabled": true,
      "reportSubscriptionCycle": "weekly_monday",
      "defaultView": "overview",
      "riskReminderFrequency": "daily",
      "initMode": "auto_structure",
      "enabledPages": ["overview", "kanban", "gantt", "risk", "reports"]
    },
    "aiSuggestions": [
      {
        "title": "优先选择模板",
        "content": "如果是需求迭代类项目，建议优先使用需求评审到验收模板。"
      },
      {
        "title": "提前锁定负责人",
        "content": "材料组与平台组在下周二至周四存在资源交叉峰值。"
      }
    ]
  }
}
```

### API-004 保存项目草稿

**请求方式**

- Method: `POST`
- Path: `/api/projects/drafts`
- Auth: 是

**请求参数**

请求 body 使用“5.3 新建项目字段”。

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

### API-005 创建项目

**请求方式**

- Method: `POST`
- Path: `/api/projects`
- Auth: 是

**请求参数**

请求 body 使用“5.3 新建项目字段”。

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
| 无创建权限 | `403 PROJECT_CREATE_FORBIDDEN` | 隐藏按钮或 Toast |
| 成员不存在 | `400 PROJECT_MEMBER_INVALID` | 提示成员信息失效 |
| 模板不可用 | `400 PROJECT_TEMPLATE_INVALID` | 提示模板不可用 |

### API-006 获取项目详情入口配置

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/entry`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | path | string | 是 | `project_318` | 项目 ID |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "projectId": "project_318",
    "defaultView": "overview",
    "enabledPages": ["overview", "members", "kanban", "gantt", "risk", "reports", "docs"],
    "permissions": [
      "project:read",
      "project:member:read",
      "project:kanban:read",
      "project:gantt:read",
      "project:risk:read",
      "project:report:read",
      "project:doc:read"
    ]
  }
}
```

### API-007 获取 AI 项目矩阵建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/project-matrix-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| context | query | string | 否 | `projects` | 当前上下文 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "primarySuggestion": {
      "id": "sug_project_001",
      "title": "智能分组建议",
      "content": "建议将“量子纠缠通信协议 V2”提升至重点风险视图，并将“深度学习实验室自动化”的联调节点提前 3 天。",
      "actions": [
        { "key": "apply", "label": "一键采纳" },
        { "key": "view_project", "label": "查看项目" }
      ]
    },
    "items": [
      {
        "id": "sug_project_002",
        "title": "新建项目推荐模板",
        "description": "如果新项目属于需求迭代，建议优先使用需求评审到验收模板。"
      },
      {
        "id": "sug_project_003",
        "title": "负载提醒",
        "description": "材料组与平台组在下周二至周四存在资源交叉峰值，建议提前锁定负责人。",
        "confidence": 0.89
      }
    ]
  }
}
```

### API-008 采纳 AI 项目建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/project-suggestions/{suggestionId}/apply`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| suggestionId | path | string | 是 | `sug_project_001` | 建议 ID |
| actionKey | body | string | 是 | `apply` | 动作 |
| projectIds | body | string[] | 否 | `["project_003"]` | 关联项目 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "resultMessage": "已生成重点风险视图建议，并同步到项目风险提醒。"
  }
}
```

### API-009 获取通知未读数

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

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入项目矩阵 | 页面加载 | `GET /api/projects/summary`、`GET /api/projects` | 当前用户、默认筛选 | 渲染统计和列表 | 错误占位 / Toast |
| 搜索项目 | 搜索框 | `GET /api/projects` | `keyword` | 更新列表 | Toast |
| 点击全部状态 | 状态筛选 | `GET /api/projects` | `status` | 更新列表 | Toast |
| 按负责人排序 | 排序按钮 | `GET /api/projects` | `sortField=owner`、`sortOrder` | 更新列表 | Toast |
| 按健康度排序 | 排序按钮 | `GET /api/projects` | `sortField=health`、`sortOrder` | 更新列表 | Toast |
| 按截止日期排序 | 排序按钮 | `GET /api/projects` | `sortField=deadline`、`sortOrder` | 更新列表 | Toast |
| 权重排序 | 排序按钮 | `GET /api/projects` | `sortField=weight` | 更新列表 | Toast |
| 点击项目行 | 项目列表 | 可选 `GET /api/projects/{id}/entry` | `projectId` | 跳转 `/project/:id` | 无权限提示 |
| 打开新建项目弹窗 | 侧边栏 / 页面按钮 | `GET /api/projects/create-options` | 当前用户 | 渲染弹窗字典 | Toast |
| 保存草稿 | 弹窗按钮 | `POST /api/projects/drafts` | 表单 | Toast 提示已保存 | 表单错误 / Toast |
| 创建项目 | 弹窗按钮 | `POST /api/projects` | 表单 | Toast，刷新列表或跳转详情 | 表单错误 / Toast |
| 打开 AI 助手 | 顶部 / 悬浮按钮 | `GET /api/ai/project-matrix-suggestions` | 当前上下文 | 渲染建议 | Toast |
| 一键采纳 AI 建议 | AI 抽屉 | `POST /api/ai/project-suggestions/{id}/apply` | 建议 ID | Toast，刷新项目提示 | Toast |
| 查看项目 | AI 抽屉 | 可选 `GET /api/projects/{id}/entry` | 项目 ID | 跳转项目详情 | 无权限提示 |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| name | input | 是 | 2-80 字 | 名称非空、长度合法 | 请输入项目名称 |
| code | input | 是 | 字母、数字、短横线，最长 64 | 全局唯一 | 项目编号已存在 |
| teamId | select | 是 | 必须在团队列表中 | 团队存在且用户有权限 | 请选择归属团队 |
| ownerId | select | 是 | 必须在负责人列表中 | 用户存在且可成为负责人 | 请选择项目负责人 |
| estimatedMemberCount | input | 否 | 正整数，1-999 | 数值范围合法 | 请输入正确成员数 |
| templateId | card/select | 是 | 必须在模板列表中 | 模板存在且可用 | 请选择项目模板 |
| startDate | date/input | 是 | 日期格式 | 日期合法 | 请选择开始日期 |
| deadline | date/input | 是 | 晚于开始日期 | 日期范围合法 | 截止日期需晚于开始日期 |
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

- 是否允许重复提交：不允许。保存草稿、创建项目、AI 采纳请求期间按钮应禁用。
- 是否需要二次确认：创建项目默认不需要；如勾选通知全员，建议二次确认。
- 是否需要审计日志：需要。保存草稿、创建项目、AI 建议采纳、项目归档/删除等操作都应记录。
- 是否需要乐观锁或版本号：草稿更新和项目编辑建议使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 项目名称 | name | string | 否 | 支持搜索 |
| 项目编号 | code | string | 否 | 支持搜索 |
| 标签 | tags | array | 否 | 支持筛选 |
| 完成度 | progress | number | 是 | 可选排序 |
| 健康度 | health | string | 是 | 当前页面有健康度排序 |
| 状态 | status | string | 是 | 全部状态筛选 |
| 负责人 | owner.name / ownerId | string | 是 | 当前页面有负责人排序 |
| 截止日期 | deadline | string | 是 | 当前页面有截止日期排序 |
| 成员数 | memberCount | number | 是 | 可选排序 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 搜索项目名称、编号、负责人 |
| 状态 | status | string | all | 全部 / 进行中 / 待启动 / 已暂停 / 已归档 |
| 健康度 | health | string | all | 良好 / 风险 / 严重 / 完成 |
| 负责人 | ownerId | string | 空 | 负责人筛选 |
| 标签 | tag | string | 空 | 标签筛选 |
| 排序字段 | sortField | string | 空 | owner / health / deadline / weight |
| 排序方向 | sortOrder | string | asc | asc / desc |
| 页码 | page | number | 1 | 分页 |
| 页大小 | pageSize | number | 20 | 最大 100 |

### 10.3 分页规则

- 默认页大小：20。
- 最大页大小：100。
- 默认排序：后端建议按项目权重、风险等级、更新时间综合排序。
- 搜索时保留当前筛选状态。
- 当前前端为本地搜索和排序，接入后建议改为服务端查询。

## 11. 文件、导入、导出

项目矩阵当前无文件导入导出按钮。

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出项目矩阵 | `POST /api/projects/export` | xlsx / csv | 不适用 | 异步任务 | P2，当前页面未设计按钮 |
| 导入项目 | `POST /api/projects/import` | xlsx / csv | 待确认 | 上传并预览 | P2，当前页面未设计按钮 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 顶部未读数、创建项目通知 |
| AI 项目矩阵建议 | 是 | AI 建议服务 | AI 抽屉内容 |
| AI 创建建议 | 是 | AI 建议服务 | 新建项目弹窗模板、负责人建议 |
| 审计日志 | 是 | 审计日志服务 | 创建项目、保存草稿、AI 采纳 |
| WebSocket / SSE | 否 | 暂无 | 项目矩阵当前不需要实时连接 |

## 13. 缓存与实时性

- 数据是否允许缓存：项目列表可短缓存 30-60 秒，权限变更后必须刷新。
- 缓存时间：项目统计建议 60 秒；项目列表按筛选条件短缓存。
- 页面返回时是否刷新：建议刷新项目列表、统计和通知未读数。
- 是否需要轮询：当前不需要。
- 是否需要 WebSocket / SSE：当前不需要；后续如项目状态实时变更可接 WebSocket。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `PROJECT_PARAM_INVALID` | 查询参数错误 | Toast 或重置筛选 |
| 400 / `PROJECT_VALIDATE_FAILED` | 创建项目字段校验失败 | 展示字段错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录或 token 过期 | 跳转登录 |
| 403 / `PROJECT_FORBIDDEN` | 无项目访问权限 | 展示无权限 |
| 403 / `PROJECT_CREATE_FORBIDDEN` | 无创建项目权限 | 隐藏按钮或 Toast |
| 404 / `PROJECT_NOT_FOUND` | 项目不存在 | 从列表移除或展示不存在 |
| 409 / `PROJECT_CODE_EXISTS` | 项目编号重复 | 表单字段错误 |
| 429 / `AI_RATE_LIMITED` | AI 建议请求过于频繁 | 提示稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | 展示失败提示 |

## 15. 验收标准

- 进入 `/projects` 后，项目矩阵列表由 `GET /api/projects` 返回，不再使用前端 mock。
- 项目列表支持关键词搜索、状态筛选、负责人排序、健康度排序、截止日期排序。
- 项目行字段完整支持名称、部门、编号、标签、完成度、健康度、状态、负责人、截止日期、成员数。
- 点击项目行可进入 `/project/:id`，且只进入当前用户有权限访问的项目。
- 项目矩阵统计卡由 `GET /api/projects/summary` 返回，不再硬编码预算、实验数、专利数、活跃成员数。
- 新建项目弹窗的团队、负责人、模板、默认值和 AI 建议由后端返回。
- 保存草稿和创建项目可提交完整表单，后端返回草稿 ID 或项目 ID。
- 项目编号重复、日期范围错误、模板不可用、无权限等异常有明确错误码。
- AI 抽屉建议由接口返回，一键采纳后有明确结果。
- `Projects.vue` 仅负责项目主列表与入口，Project 子页面深层数据由对应子页面接口和文档承接。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 项目矩阵列表是否服务端分页，还是首期返回全部可见项目？ | 前后端 | 待确认 |
| Q2 | “全部状态”筛选首期是否需要展开为多个状态 chip？ | 产品/前端 | 待确认 |
| Q3 | “权重排序”的权重口径是什么：风险、进度、优先级、更新时间还是 AI 综合评分？ | 产品/后端/AI | 待确认 |
| Q4 | 研发预算、实验数量、专利申请量的数据源分别来自哪个系统？ | 后端/数据 | 待确认 |
| Q5 | 项目 ID 使用数字 ID、UUID，还是项目编号 code？路由 `/project/:id` 建议使用哪个？ | 前后端 | 待确认 |
| Q6 | 创建项目后是跳转项目详情，还是留在项目矩阵并刷新列表？ | 产品/前端 | 待确认 |
| Q7 | `ProjectMembers.vue` 等 Project 子页面文件是否后续独立挂路由，还是继续统一由 `ProjectDetail.vue` 承载 tab？ | 前端/产品 | 待确认 |
| Q8 | 新建项目中的“核心成员”“报告订阅人”是自由文本还是必须选择用户/角色？ | 产品/前后端 | 待确认 |
| Q9 | AI 项目建议采纳后具体执行什么动作：调整排序、生成风险提醒、更新项目标签还是创建待办？ | 产品/AI/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`src/views/Projects.vue` 的 `projects` 数组。
- 当前搜索和排序为前端本地 computed：`sortedProjects`。
- 当前顶部搜索框未绑定接口；项目矩阵内搜索框绑定 `searchKeyword`。
- 当前通知角标静态写死为 `5`。
- 当前用户信息 mock：`currentUser = { name: '张工', role: '研发总监', avatar: ... }`。
- 当前新建项目弹窗字段为静态 HTML value，尚未绑定响应式表单。
- 当前“保存草稿”“创建项目”仅调用 `showToast`，未提交接口。
- 当前 AI 助手抽屉为静态文案，“一键采纳”“查看项目”未绑定接口。
- 当前路由中 `/project/:id` 和 `/project/:id/:tab` 均由 `ProjectDetail.vue` 承载；`ProjectMembers.vue`、`ProjectReports.vue` 等文件存在，但当前未单独挂载。
