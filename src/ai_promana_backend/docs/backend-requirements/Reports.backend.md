# 全局报表后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Reports.vue`  
> 页面定位：跨项目全局报表，偏管理视角、跨项目对比、资源趋势和 AI 管理洞察。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 全局报表 |
| 前端路由 | `/reports` |
| 前端文件 | `src/views/Reports.vue` |
| 所属模块 | 报表中心 / 全局报表 / 管理洞察 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示跨项目全局报表数据，服务研发总监、管理员和项目负责人进行管理决策。
- 汇总多项目健康度分布、成员负载分布和跨项目资源冲突风险。
- 提供管理视角 AI 洞察，生成管理周报、导出 CSV、定时订阅。
- 支持通过顶部搜索定位项目、成员或图表。
- 提供 AI 助手抽屉，在全局报表上下文下生成资源调度和管理建议。

### 2.2 对接范围

- 全局报表总览接口：AI 洞察、项目健康度分布、成员负载分布。
- 跨项目筛选条件：项目范围、部门、成员、日期范围、健康度。
- 全局报表导出：CSV / XLSX / PDF / Markdown。
- 定时订阅：订阅周期、收件人、报表范围、通知渠道。
- AI 管理周报生成、AI 建议获取与采纳、AI 反馈。
- 顶部当前用户信息、通知未读数。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Dashboard.vue` | 全局工作台可跳转全局报表，部分指标口径一致 |
| `Projects.vue` | 项目矩阵提供项目范围和健康度数据 |
| `ProjectReports.vue` | 项目级报表；全局报表聚合多个项目级数据 |
| `ProjectMembers.vue` | 成员负载数据来源 |
| `ProjectRisk.vue` | 跨项目风险和资源冲突来源 |
| `Notifications.vue` | 顶部通知入口和订阅下发提醒 |
| `UserProfileHoverCard.vue` | 顶部当前用户展示 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 可查看全量组织报表 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 按组织/部门范围 |
| 项目负责人 | 是 | 视权限 | 视权限 | 否 | 视权限 | 查看本人负责及授权项目 |
| 成员 | 视权限 | 否 | 否 | 否 | 否 | 通常只查看个人或参与项目聚合 |
| 协作者 | 否 | 否 | 否 | 否 | 否 | 默认无全局报表权限 |

### 3.1 权限规则

- 页面入口权限：访问 `/reports` 需要登录态和 `global:report:read` 或等价权限。
- 按钮级权限：
  - “导出全局报表”“导出 CSV”需要 `global:report:export`。
  - “跨项目筛选”需要 `global:report:filter` 或页面查看权限。
  - “定时订阅”需要 `global:report:subscribe`。
  - “生成周报”“生成管理周报”需要 `ai:global-report:generate`。
  - AI 建议采纳需要 `ai:global-report-suggestion:apply`，如会调整资源计划，还需对应业务权限。
- 数据范围权限：
  - 超级管理员可查看全量项目和成员。
  - 管理员按组织、部门、租户范围过滤。
  - 项目负责人默认只统计本人负责、参与或被授权的项目。
- 敏感字段脱敏规则：无权限不返回个人明细工时、绩效推断、成本预算、成员联系方式等敏感字段。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 当前静态为张工/研发总监 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 当前静态为 5 |
| 全局报表总览 | 首屏核心图表和 AI 洞察 | 是 | `GET /api/reports/global/overview` | P0 |
| 项目健康度分布 | 柱状图 | 是 | `GET /api/reports/global/project-health` | 可并入 overview |
| 成员负载分布 | 进度条列表 | 是 | `GET /api/reports/global/resource-load` | 可并入 overview |
| 报表筛选选项 | 跨项目筛选弹窗 | 否 | `GET /api/reports/global/options` | P1 |
| AI 助手建议 | AI 抽屉 | 否 | `GET /api/ai/global-report-suggestions` | P1 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 图表加载 / 局部骨架 | 请求处理中 | 当前未接 loading |
| empty | 无全局报表数据 | 当前范围无项目或无统计 | 展示空状态 |
| error | Toast / 错误占位 | 接口异常或无权限 | 标准错误结构 |
| filtered | 跨项目筛选生效 | 后端按筛选返回 | P1 |
| exporting | 导出中 | 异步任务处理中 | 禁用导出按钮 |
| drawerOpen | AI 抽屉打开 | 加载全局建议 | 当前为静态文案 |

## 5. 字段模型

### 5.1 全局 AI 洞察字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| insightId | string | 是 | AI 洞察卡片 | `insight_global_001` | 洞察 ID |
| title | string | 是 | 大标题 | `本周团队整体效率提升 9%...` | 管理洞察标题 |
| content | string | 是 | 说明文案 | `建议优先平衡 QA 资源窗口...` | 洞察详情 |
| efficiencyGrowthRate | number | 否 | 标题/统计 | `9` | 效率提升百分比 |
| conflictProjectCount | number | 否 | 标题/说明 | `3` | 存在资源冲突项目数 |
| conflictResource | string | 否 | 说明 | `QA` | 冲突资源类型 |
| generatedAt | string | 是 | 可选 | `2026-05-11T12:40:00+08:00` | 生成时间 |
| actions | array | 否 | 操作按钮 | `[]` | 生成周报、导出等 |

### 5.2 项目健康度分布字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | string | 是 | 柱状图 key | `project_lab` | 项目 ID |
| projectName | string | 是 | 柱状图标签 | `核心实验室` | 项目名称 |
| healthScore | number | 是 | 柱高 | `85` | 0-100 |
| healthStatus | string | 是 | 柱颜色 | `good` | 健康状态 |
| ownerId | string | 否 | 筛选 | `u_10001` | 负责人 |
| departmentId | string | 否 | 筛选 | `dept_material` | 部门 |
| riskCount | number | 否 | tooltip | `2` | 风险数量 |
| progress | number | 否 | tooltip | `72` | 项目进度 |

### 5.3 成员负载分布字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| resourceId | string | 是 | 行 key | `resource_qa` | 资源组/成员 ID |
| resourceName | string | 是 | 负载名称 | `QA 资源` | 资源组或成员名称 |
| resourceType | string | 是 | 类型 | `role_group` | role_group/team/member |
| loadRate | number | 是 | 进度条 | `89` | 0-100 |
| loadLevel | string | 是 | 颜色 | `danger` | 负载等级 |
| projectCount | number | 否 | tooltip | `3` | 涉及项目数 |
| taskCount | number | 否 | tooltip | `26` | 任务数 |
| conflictWindow | string | 否 | tooltip | `下周一至周三` | 冲突窗口 |

### 5.4 筛选字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| dateRange | object | 否 | 跨项目筛选 | `{ "start": "2026-05-04", "end": "2026-05-11" }` | 时间范围 |
| projectIds | string[] | 否 | 跨项目筛选 | `["project_001"]` | 项目范围 |
| departmentIds | string[] | 否 | 跨项目筛选 | `["dept_qa"]` | 部门范围 |
| memberIds | string[] | 否 | 搜索/筛选 | `["u_10001"]` | 成员范围 |
| healthStatuses | string[] | 否 | 筛选 | `["risk"]` | 健康度 |
| reportTypes | string[] | 否 | 筛选 | `["health","load"]` | 图表类型 |

### 5.5 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| healthStatus | `good` | 健康 | success | 正常项目 |
| healthStatus | `warning` | 需关注 | warning | 有轻度风险 |
| healthStatus | `danger` | 高风险 | danger | 高风险项目 |
| healthStatus | `completed` | 已完成 | success | 已完成项目 |
| loadLevel | `success` | 正常 | success | 0-70% |
| loadLevel | `warning` | 偏高 | warning | 70-85% |
| loadLevel | `danger` | 超载 | danger | 85% 以上 |
| exportFormat | `csv` | CSV | secondary | 当前页面按钮 |
| exportFormat | `xlsx` | Excel | secondary | 表格 |
| exportFormat | `pdf` | PDF | secondary | 管理报表 |
| exportFormat | `markdown` | Markdown | primary | 周报文本 |
| subscriptionCycle | `weekly_monday` | 每周一 | neutral | 周报 |
| subscriptionCycle | `daily` | 每日 | neutral | 日报 |
| subscriptionCycle | `monthly_first_day` | 每月 1 日 | neutral | 月报 |

### 5.6 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| efficiencyGrowthRate | number | 本周整体效率较上周增长率 | AI 洞察标题 | 当前展示 9% |
| conflictProjectCount | number | 存在同一资源窗口冲突的项目数 | AI 洞察标题 | 当前展示 3 |
| averageHealthScore | number | 可见项目健康度平均值 | 全局总览 | 可选 |
| overloadedResourceCount | number | loadRate 超过阈值的资源数 | 全局总览 | 可选 |
| reportGeneratedAt | string | 报表生成时间 | 导出/订阅 | 可选 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取全局报表总览 | GET | `/api/reports/global/overview` | 首屏 AI 洞察和图表 | P0 |
| API-002 | 获取项目健康度分布 | GET | `/api/reports/global/project-health` | 项目健康度柱状图 | P0 |
| API-003 | 获取成员/资源负载分布 | GET | `/api/reports/global/resource-load` | 跨项目资源负载 | P0 |
| API-004 | 获取全局报表筛选选项 | GET | `/api/reports/global/options` | 跨项目筛选 | P1 |
| API-005 | 导出全局报表 | POST | `/api/reports/global/export` | 导出 CSV/XLSX/PDF/Markdown | P0 |
| API-006 | 创建全局报表订阅 | POST | `/api/reports/global/subscriptions` | 定时订阅 | P1 |
| API-007 | 获取全局报表订阅列表 | GET | `/api/reports/global/subscriptions` | 查看订阅 | P2 |
| API-008 | 获取 AI 全局报表建议 | GET | `/api/ai/global-report-suggestions` | AI 抽屉建议 | P1 |
| API-009 | 生成管理周报 | POST | `/api/ai/global-report-weekly` | 生成周报 | P1 |
| API-010 | 采纳 AI 全局建议 | POST | `/api/ai/global-report-suggestions/{suggestionId}/apply` | 资源调度/提醒 | P1 |
| API-011 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部角标 | P0 |

## 7. 接口详情

### API-001 获取全局报表总览

**请求方式**

- Method: `GET`
- Path: `/api/reports/global/overview`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| startDate | query | string | 否 | `2026-05-04` | 统计开始日期 |
| endDate | query | string | 否 | `2026-05-11` | 统计结束日期 |
| projectIds | query | string | 否 | `project_001,project_002` | 项目 ID，逗号分隔 |
| departmentIds | query | string | 否 | `dept_qa` | 部门 ID，逗号分隔 |
| keyword | query | string | 否 | `QA` | 搜索项目、成员、图表 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "aiInsight": {
      "insightId": "insight_global_001",
      "title": "本周团队整体效率提升 9%，但 3 个项目共享同一 QA 资源，存在下周资源冲突风险。",
      "content": "建议从全局层面优先平衡 QA 资源窗口，并提前对联调验证、自动化巡检和协议升级三条线做时间切分。",
      "efficiencyGrowthRate": 9,
      "conflictProjectCount": 3,
      "conflictResource": "QA",
      "generatedAt": "2026-05-11T12:40:00+08:00"
    },
    "projectHealth": [
      {
        "projectId": "project_lab",
        "projectName": "核心实验室",
        "healthScore": 85,
        "healthStatus": "good",
        "riskCount": 1,
        "progress": 82
      },
      {
        "projectId": "project_material",
        "projectName": "材料迭代",
        "healthScore": 44,
        "healthStatus": "warning",
        "riskCount": 5,
        "progress": 61
      }
    ],
    "resourceLoad": [
      {
        "resourceId": "resource_qa",
        "resourceName": "QA 资源",
        "resourceType": "role_group",
        "loadRate": 89,
        "loadLevel": "danger",
        "projectCount": 3,
        "taskCount": 18,
        "conflictWindow": "下周一至周三"
      }
    ],
    "summary": {
      "averageHealthScore": 68,
      "overloadedResourceCount": 1,
      "reportGeneratedAt": "2026-05-11T12:40:00+08:00"
    }
  }
}
```

### API-002 获取项目健康度分布

**请求方式**

- Method: `GET`
- Path: `/api/reports/global/project-health`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| startDate | query | string | 否 | `2026-05-04` | 开始日期 |
| endDate | query | string | 否 | `2026-05-11` | 结束日期 |
| projectIds | query | string | 否 | `project_lab` | 项目筛选 |
| departmentIds | query | string | 否 | `dept_material` | 部门筛选 |
| healthStatus | query | string | 否 | `warning` | 健康度筛选 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "projectId": "project_lab",
      "projectName": "核心实验室",
      "healthScore": 85,
      "healthStatus": "good",
      "ownerId": "u_10001",
      "departmentId": "dept_lab",
      "riskCount": 1,
      "progress": 82
    }
  ]
}
```

### API-003 获取成员/资源负载分布

**请求方式**

- Method: `GET`
- Path: `/api/reports/global/resource-load`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| startDate | query | string | 否 | `2026-05-04` | 开始日期 |
| endDate | query | string | 否 | `2026-05-11` | 结束日期 |
| resourceType | query | string | 否 | `role_group` | role_group/team/member |
| departmentIds | query | string | 否 | `dept_qa` | 部门筛选 |
| projectIds | query | string | 否 | `project_001` | 项目筛选 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "resourceId": "resource_qa",
      "resourceName": "QA 资源",
      "resourceType": "role_group",
      "loadRate": 89,
      "loadLevel": "danger",
      "projectCount": 3,
      "taskCount": 18,
      "conflictWindow": "下周一至周三"
    },
    {
      "resourceId": "team_platform",
      "resourceName": "平台组",
      "resourceType": "team",
      "loadRate": 78,
      "loadLevel": "warning",
      "projectCount": 4,
      "taskCount": 31
    }
  ]
}
```

### API-005 导出全局报表

**请求方式**

- Method: `POST`
- Path: `/api/reports/global/export`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| format | body | string | 是 | `csv` | csv/xlsx/pdf/markdown |
| startDate | body | string | 否 | `2026-05-04` | 开始日期 |
| endDate | body | string | 否 | `2026-05-11` | 结束日期 |
| projectIds | body | string[] | 否 | `["project_001"]` | 项目范围 |
| departmentIds | body | string[] | 否 | `["dept_qa"]` | 部门范围 |
| includeAiInsight | body | boolean | 否 | `true` | 是否包含 AI 洞察 |
| includeCharts | body | boolean | 否 | `true` | 是否包含图表 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "exportTaskId": "export_global_001",
    "status": "processing",
    "downloadUrl": null,
    "expiresAt": null
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 无导出权限 | `403 GLOBAL_REPORT_EXPORT_FORBIDDEN` | Toast 或隐藏按钮 |
| 格式不支持 | `400 REPORT_EXPORT_FORMAT_INVALID` | 提示格式错误 |
| 数据为空 | `404 REPORT_DATA_EMPTY` | 提示当前范围无数据 |
| 任务创建失败 | `500 REPORT_EXPORT_FAILED` | Toast |

### API-006 创建全局报表订阅

**请求方式**

- Method: `POST`
- Path: `/api/reports/global/subscriptions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | body | string | 是 | `研发管理周报` | 订阅名称 |
| cycle | body | string | 是 | `weekly_monday` | 订阅周期 |
| format | body | string | 是 | `markdown` | 报表格式 |
| projectIds | body | string[] | 否 | `["project_001"]` | 项目范围 |
| departmentIds | body | string[] | 否 | `["dept_qa"]` | 部门范围 |
| subscriberIds | body | string[] | 是 | `["u_10001"]` | 订阅人 |
| channels | body | string[] | 否 | `["in_app", "email"]` | 通知渠道 |
| includeAiInsight | body | boolean | 否 | `true` | 是否包含 AI 洞察 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "subscriptionId": "global_report_sub_001",
    "enabled": true,
    "nextRunAt": "2026-05-18T09:00:00+08:00"
  }
}
```

### API-008 获取 AI 全局报表建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/global-report-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| context | query | string | 否 | `global_reports` | 上下文 |
| startDate | query | string | 否 | `2026-05-04` | 统计开始 |
| endDate | query | string | 否 | `2026-05-11` | 统计结束 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "card": {
      "suggestionId": "sug_global_report_001",
      "title": "全局建议",
      "content": "建议从下周一开始冻结 QA 的跨项目时段，避免 3 个高优先级项目在同一时间抢占验证资源。",
      "actions": [
        { "key": "generate_management_weekly", "label": "生成管理周报" },
        { "key": "create_resource_reminder", "label": "生成资源提醒" }
      ],
      "confidence": 0.91
    },
    "relatedProjects": [
      { "projectId": "project_001", "name": "联调验证" }
    ]
  }
}
```

### API-009 生成管理周报

**请求方式**

- Method: `POST`
- Path: `/api/ai/global-report-weekly`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| startDate | body | string | 否 | `2026-05-04` | 开始日期 |
| endDate | body | string | 否 | `2026-05-11` | 结束日期 |
| projectIds | body | string[] | 否 | `["project_001"]` | 项目范围 |
| format | body | string | 否 | `markdown` | markdown/pdf |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reportId": "weekly_global_001",
    "format": "markdown",
    "content": "# 研发管理周报\n\n本周团队整体效率提升 9%...",
    "downloadUrl": null,
    "generatedAt": "2026-05-11T12:50:00+08:00"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入全局报表 | 页面加载 | `GET /api/reports/global/overview`、`GET /api/notifications/unread-count` | 当前用户权限 | 渲染图表和角标 | 错误占位 / Toast |
| 搜索项目/成员/图表 | 顶部搜索框 | `GET /api/reports/global/overview` | keyword | 更新图表 | Toast |
| 点击跨项目筛选 | 页面按钮 | `GET /api/reports/global/options` | 当前用户 | 打开筛选项 | Toast |
| 应用跨项目筛选 | 筛选弹窗 | `GET /api/reports/global/overview` | 筛选表单 | 刷新图表 | Toast |
| 点击导出全局报表 | 侧边栏按钮 | `POST /api/reports/global/export` | 当前筛选、format | 下载/导出任务提示 | Toast |
| 点击导出 CSV | AI 洞察卡片 | `POST /api/reports/global/export` | `format=csv` | 下载/导出任务提示 | Toast |
| 点击定时订阅 | 页面按钮 | `POST /api/reports/global/subscriptions` | 订阅表单 | Toast | 表单错误 |
| 点击生成周报 | AI 洞察卡片 | `POST /api/ai/global-report-weekly` | 当前筛选 | 展示/下载周报 | Toast |
| 打开 AI 助手 | 顶部 / 悬浮按钮 | `GET /api/ai/global-report-suggestions` | 当前上下文 | 渲染建议 | Toast |
| 生成管理周报 | AI 抽屉 | `POST /api/ai/global-report-weekly` | 当前上下文 | 生成周报 | Toast |
| 采纳全局建议 | AI 抽屉 | `POST /api/ai/global-report-suggestions/{id}/apply` | suggestionId、actionKey | Toast，刷新洞察 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| startDate | date | 否 | 日期格式 | 不晚于 endDate | 开始日期无效 |
| endDate | date | 否 | 日期格式 | 不早于 startDate | 结束日期无效 |
| projectIds | selector | 否 | 项目数组 | 项目存在且有权限 | 项目范围无效 |
| departmentIds | selector | 否 | 部门数组 | 部门存在且有权限 | 部门范围无效 |
| memberIds | selector | 否 | 成员数组 | 成员存在且可见 | 成员范围无效 |
| format | select | 导出必填 | csv/xlsx/pdf/markdown | 格式合法 | 导出格式无效 |
| name | input | 订阅必填 | 1-80 字 | 名称合法 | 请输入订阅名称 |
| cycle | select | 订阅必填 | 枚举 | 周期合法 | 请选择订阅周期 |
| subscriberIds | selector | 订阅必填 | 用户或角色数组 | 对象存在且有权限 | 请选择订阅人 |
| channels | checkbox | 否 | in_app/email/dingtalk | 渠道可用 | 通知渠道无效 |

### 9.1 提交规则

- 是否允许重复提交：导出、订阅、AI 生成过程中不允许重复提交。
- 是否需要二次确认：导出含敏感个人工时/成本数据时建议二次确认；批量订阅外部渠道建议二次确认。
- 是否需要审计日志：需要，导出、订阅、AI 生成、AI 采纳、筛选范围包含敏感数据访问都应记录。
- 是否需要乐观锁或版本号：订阅更新/删除建议使用 `version`，当前新增订阅不需要。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 项目名称 | projectName | string | 否 | 项目健康度图 |
| 健康度分数 | healthScore | number | 是 | 0-100 |
| 健康状态 | healthStatus | string | 是 | good/warning/danger |
| 风险数量 | riskCount | number | 是 | tooltip / 明细 |
| 进度 | progress | number | 是 | tooltip / 明细 |
| 资源名称 | resourceName | string | 否 | 负载图 |
| 资源类型 | resourceType | string | 是 | 角色组/团队/成员 |
| 负载率 | loadRate | number | 是 | 0-100 |
| 涉及项目数 | projectCount | number | 是 | tooltip / 明细 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 搜索项目、成员、图表 |
| 开始日期 | startDate | string | 本周开始 | 统计范围 |
| 结束日期 | endDate | string | 今日 | 统计范围 |
| 项目范围 | projectIds | string[] | 当前可见全部 | 项目筛选 |
| 部门范围 | departmentIds | string[] | 当前可见全部 | 部门筛选 |
| 成员范围 | memberIds | string[] | 当前可见全部 | 成员筛选 |
| 健康状态 | healthStatus | string | all | 项目健康度 |
| 资源类型 | resourceType | string | role_group | 负载图维度 |

### 10.3 分页规则

- 当前页面图表数据无分页。
- 若跨项目明细弹窗后续扩展，默认页大小 20，最大页大小 100。
- 默认排序：项目健康度按风险权重和健康分排序；资源负载按 `loadRate` 倒序。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出全局报表 | `POST /api/reports/global/export` | csv / xlsx / pdf / markdown | 不适用 | 异步任务 | 当前侧边栏按钮 |
| 导出 CSV | `POST /api/reports/global/export` | csv | 不适用 | 同步或异步 | 当前 AI 卡片按钮 |
| 生成管理周报 | `POST /api/ai/global-report-weekly` | markdown / pdf | 不适用 | 同步文本或异步任务 | AI 能力 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 顶部未读数、订阅下发、资源冲突提醒 |
| AI 管理洞察 | 是 | AI 报表服务 | 首屏洞察、抽屉建议 |
| AI 管理周报 | 是 | AI 报表服务 | 生成 Markdown/PDF 周报 |
| 审计日志 | 是 | 审计日志服务 | 导出、订阅、AI 生成、敏感报表访问 |
| WebSocket / SSE | 否 | 暂无 | 当前不需要实时连接 |

## 13. 缓存与实时性

- 数据是否允许缓存：全局报表聚合可缓存 5-10 分钟；通知未读数不建议长缓存。
- 缓存时间：项目健康度和资源负载建议 5 分钟；AI 洞察按筛选条件缓存。
- 页面返回时是否刷新：建议刷新总览、通知未读数和导出任务状态。
- 是否需要轮询：导出任务需要轮询任务状态；普通图表不需要。
- 是否需要 WebSocket / SSE：当前不需要；后续资源冲突实时预警可考虑 SSE。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `GLOBAL_REPORT_PARAM_INVALID` | 筛选参数错误 | Toast 或表单错误 |
| 400 / `REPORT_EXPORT_FORMAT_INVALID` | 导出格式错误 | Toast |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录或 token 过期 | 跳转登录 |
| 403 / `GLOBAL_REPORT_FORBIDDEN` | 无全局报表权限 | 无权限提示 |
| 403 / `GLOBAL_REPORT_EXPORT_FORBIDDEN` | 无导出权限 | 隐藏按钮或 Toast |
| 404 / `REPORT_DATA_EMPTY` | 当前范围无数据 | 展示空状态 |
| 409 / `REPORT_SUBSCRIPTION_EXISTS` | 重复订阅 | 提示已订阅 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 进入 `/reports` 后，全局 AI 洞察、项目健康度分布、成员负载分布均由后端接口返回。
- 顶部通知未读数和当前用户信息使用真实接口，不再静态写死。
- 跨项目筛选能按日期、项目、部门、成员、健康状态刷新报表。
- 侧边栏“导出全局报表”和 AI 卡片“导出 CSV”均有导出接口支撑。
- “定时订阅”可提交订阅周期、格式、订阅人、通知渠道。
- AI 抽屉可获取全局建议，并支持生成管理周报。
- 无权限、无数据、参数错误、导出失败、AI 限流等状态有明确错误码。
- 后端按当前用户权限过滤报表范围，不向无权限用户返回敏感统计明细。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 全局报表默认统计周期是本周、最近 30 天，还是按自然周？ | 产品/后端 | 待确认 |
| Q2 | “团队整体效率提升 9%”的效率口径是什么：任务吞吐、工时效率、Story Point，还是 AI 综合评分？ | 产品/数据/后端 | 待确认 |
| Q3 | 项目健康度分数由哪些指标计算：进度、风险、缺陷、资源负载、预算？ | 产品/数据 | 待确认 |
| Q4 | 成员负载展示按角色组、团队还是个人？是否允许普通管理员查看个人明细？ | 产品/后端/安全 | 待确认 |
| Q5 | 全局报表导出是否包含个人工时、成本等敏感字段？是否需要二次确认和水印？ | 产品/安全/后端 | 待确认 |
| Q6 | AI 建议“冻结 QA 跨项目时段”是只生成建议，还是会创建资源锁定/排期调整任务？ | 产品/AI/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`src/views/Reports.vue` 的模板静态图表、AI 文案和 `currentUser`。
- 当前顶部通知角标静态为 `5`。
- 当前“导出全局报表”“跨项目筛选”“定时订阅”“生成周报”“导出 CSV”“生成管理周报”均未接接口。
- 当前搜索框没有绑定响应式状态和接口。
- 当前 AI 抽屉只使用 `isAiDrawerOpen` 控制显示，建议后续打开时加载 `GET /api/ai/global-report-suggestions`。
- 需要后端优先确认的字段：项目健康度分数、资源负载口径、全局报表权限范围、导出格式。
- 需要后端优先确认的接口：`GET /api/reports/global/overview`、`POST /api/reports/global/export`、`POST /api/ai/global-report-weekly`。
