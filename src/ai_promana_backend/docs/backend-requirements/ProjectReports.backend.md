# 项目报表后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/ProjectReports.vue`，当前主要由 `views/ProjectDetail.vue` 的 `reports` tab 承载  
> 页面定位：项目级进度、工时、质量、负载与 AI 周报洞察。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目报表 |
| 前端路由 | `/project/:id/reports` |
| 前端文件 | `src/views/ProjectReports.vue`、`src/views/ProjectDetail.vue` |
| 所属模块 | 项目管理 / 项目详情 / 报表 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示项目周期内的进度、工时、质量和阻塞/负载分布报表。
- 支持最近 30 天、本周、全部成员、进度报表、工时报表、质量报表筛选。
- 展示 AI 洞察卡片，生成周报结论和 Markdown 导出。
- 展示燃尽图、计划 vs 实际工时、Bug 趋势、阻塞时长与负载分布。
- 支持导出报表、订阅报表、AI 反馈。

### 2.2 对接范围

- 报表筛选选项、AI 洞察、燃尽图、工时柱状图、Bug 趋势、阻塞负载分布。
- 报表导出 Markdown/PDF/XLSX。
- 周报自动生成、复制 Markdown、点赞/点踩反馈。
- 报表订阅和定时下发。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `ProjectDetail.vue` | 当前报表 tab 的主要承载页 |
| `ProjectKanban.vue` | 任务状态、燃尽数据来源 |
| `ProjectMembers.vue` | 成员工时和负载来源 |
| `ProjectRisk.vue` | 风险和阻塞来源 |
| `Reports.vue` | 全局报表页面，可汇总项目报表 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全量报表 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 组织范围 |
| 项目负责人 | 是 | 是 | 是 | 否 | 是 | 可导出/订阅 |
| 项目成员 | 是 | 否 | 否 | 否 | 视权限 | 查看项目报表 |
| 协作者 | 是 | 否 | 否 | 否 | 否 | 只读 |

### 3.1 权限规则

- 页面入口权限：需要 `project:report:read`。
- 按钮级权限：
  - 导出 Markdown/PDF/XLSX 需要 `project:report:export`。
  - 报表订阅需要 `project:report:subscribe`。
  - 自动生成周报需要 `ai:report:generate`。
  - AI 反馈需要登录用户。
- 数据范围权限：报表只统计当前用户可见任务、成员、风险。
- 敏感字段脱敏规则：无权限不返回个人工时明细、成本、绩效推断字段。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 项目详情头部 | 项目名称和状态 | 是 | `GET /api/projects/{projectId}` | 共用 |
| 报表筛选选项 | 顶部 chip | 是 | `GET /api/projects/{projectId}/reports/options` | 时间范围、成员、类型 |
| AI 洞察卡片 | 周报摘要 | 是 | `GET /api/projects/{projectId}/reports/ai-insight` | 当前大卡片 |
| 燃尽图 | 剩余工作趋势 | 是 | `GET /api/projects/{projectId}/reports/burndown` | 双线图 |
| 工时图 | 计划 vs 实际 | 是 | `GET /api/projects/{projectId}/reports/work-hours` | 柱状图 |
| Bug 趋势 | 新增/关闭 | 是 | `GET /api/projects/{projectId}/reports/bugs` | 双线图 |
| 阻塞与负载 | mini bars | 是 | `GET /api/projects/{projectId}/reports/block-load` | 阻塞小时、负载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 图表加载 | 请求处理中 | 分图表 loading |
| empty | 无报表数据 | 当前筛选无数据 | 空图表 |
| error | Toast / 错误占位 | 接口异常 | 标准错误 |
| exporting | 导出中 | 异步任务处理中 | 按钮禁用 |
| subscribed | 已订阅 | 当前用户订阅 | 按钮状态 |

## 5. 字段模型

### 5.1 AI 洞察字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| insightId | string | 是 | AI 卡片 | `insight_report_001` | 洞察 ID |
| title | string | 是 | 卡片大标题 | `本周团队效率提升 12%...` | 标题 |
| content | string | 是 | 卡片说明 | `AI 综合燃尽图...` | 内容 |
| reportPeriod | object | 是 | 筛选范围 | `{}` | 报表周期 |
| actions | array | 否 | 操作按钮 | `[]` | 导出/反馈 |
| generatedAt | string | 是 | 可选 | `2026-05-11T...` | 生成时间 |

### 5.2 燃尽图字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | string | 是 | x 轴 | `2026-05-01` | 日期 |
| actualRemaining | number | 是 | 实际剩余 | `74` | 可为工时或点数 |
| targetRemaining | number | 是 | 目标燃尽 | `78` | 目标值 |
| unit | string | 是 | 单位 | `story_point` | 点数/小时 |

### 5.3 工时字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| userId | string | 是 | 柱状图 key | `u_10001` | 用户 ID |
| name | string | 是 | x 轴 | `王志强` | 成员名 |
| plannedHours | number | 是 | 计划工时 | `40` | 小时 |
| actualHours | number | 是 | 实际工时 | `45` | 小时 |
| usageRate | number | 是 | 柱高 | `82` | 前端可按比例计算 |
| level | string | 否 | 样式 | `warning` | 负载等级 |

### 5.4 Bug 趋势字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | string | 是 | x 轴 | `2026-05-01` | 日期 |
| createdCount | number | 是 | 新增 | `5` | 新增缺陷数 |
| closedCount | number | 是 | 关闭 | `3` | 关闭缺陷数 |
| criticalOpenCount | number | 否 | 关键缺陷 | `1` | 可选 |

### 5.5 阻塞与负载字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| label | string | 是 | mini bar 标签 | `联调环境` | 维度名称 |
| value | number | 是 | 进度条 | `78` | 百分比 |
| displayValue | string | 是 | 右侧值 | `31h` | 展示 |
| type | string | 是 | 类型 | `block_hours` | 阻塞/负载 |
| level | string | 否 | 样式 | `danger` | 样式语义 |

### 5.6 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| period | `last_30_days` | 最近 30 天 | active | 默认 |
| period | `this_week` | 本周 | active | 本周 |
| reportType | `progress` | 进度报表 | active | 进度 |
| reportType | `work_hours` | 工时报表 | active | 工时 |
| reportType | `quality` | 质量报表 | active | 质量 |
| exportFormat | `markdown` | Markdown | primary | 周报文本 |
| exportFormat | `pdf` | PDF | secondary | PDF |
| exportFormat | `xlsx` | Excel | secondary | 表格 |

### 5.7 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| efficiencyGrowthRate | number | 本周期效率较上周期增长率 | AI 洞察 | 当前展示 12% |
| remainingWork | number | 未完成任务工时/点数 | 燃尽图 | 口径需确认 |
| plannedVsActualDelta | number | 实际工时 - 计划工时 | 工时图 | 可后端计算 |
| bugCloseRate | number | 关闭数 / 新增数 | Bug 趋势 | 可选 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取报表选项 | GET | `/api/projects/{projectId}/reports/options` | 筛选项 | P0 |
| API-002 | 获取报表总览 | GET | `/api/projects/{projectId}/reports/overview` | 首屏聚合 | P0 |
| API-003 | 获取 AI 报表洞察 | GET | `/api/projects/{projectId}/reports/ai-insight` | AI 卡片 | P0 |
| API-004 | 获取燃尽图 | GET | `/api/projects/{projectId}/reports/burndown` | 燃尽图 | P0 |
| API-005 | 获取工时报表 | GET | `/api/projects/{projectId}/reports/work-hours` | 工时图 | P0 |
| API-006 | 获取 Bug 趋势 | GET | `/api/projects/{projectId}/reports/bugs` | Bug 图 | P0 |
| API-007 | 获取阻塞负载分布 | GET | `/api/projects/{projectId}/reports/block-load` | mini bars | P0 |
| API-008 | 导出项目报表 | POST | `/api/projects/{projectId}/reports/export` | 导出 | P0 |
| API-009 | 订阅项目报表 | POST | `/api/projects/{projectId}/reports/subscriptions` | 订阅 | P1 |
| API-010 | AI 反馈 | POST | `/api/ai/feedback` | 点赞/点踩 | P1 |

## 7. 接口详情

### API-002 获取报表总览

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/reports/overview`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| period | query | string | 否 | `last_30_days` | 时间范围 |
| memberId | query | string | 否 | `all` | 成员筛选 |
| reportTypes | query | string | 否 | `progress,quality` | 报表类型 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "aiInsight": {
      "insightId": "insight_report_001",
      "title": "本周团队效率提升 12%，但联调节点仍是唯一主风险源。",
      "content": "AI 综合燃尽图、成员负载与 Bug 趋势后判断：当前项目整体可控。",
      "generatedAt": "2026-05-11T11:40:00+08:00"
    },
    "burndown": [
      { "date": "2026-05-01", "actualRemaining": 74, "targetRemaining": 78, "unit": "story_point" }
    ],
    "workHours": [
      { "userId": "u_10001", "name": "王志强", "plannedHours": 40, "actualHours": 45, "usageRate": 82, "level": "primary" }
    ],
    "bugs": [
      { "date": "2026-05-01", "createdCount": 4, "closedCount": 2 }
    ],
    "blockLoad": [
      { "label": "联调环境", "value": 78, "displayValue": "31h", "type": "block_hours", "level": "danger" }
    ]
  }
}
```

### API-008 导出项目报表

**请求方式**

- Method: `POST`
- Path: `/api/projects/{projectId}/reports/export`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| format | body | string | 是 | `markdown` | markdown/pdf/xlsx |
| period | body | string | 是 | `last_30_days` | 时间范围 |
| memberId | body | string | 否 | `all` | 成员 |
| reportTypes | body | string[] | 否 | `["progress"]` | 报表类型 |
| includeAiInsight | body | boolean | 否 | `true` | 是否包含 AI 洞察 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "exportTaskId": "export_001",
    "status": "processing",
    "downloadUrl": null
  }
}
```

### API-009 订阅项目报表

**请求方式**

- Method: `POST`
- Path: `/api/projects/{projectId}/reports/subscriptions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| cycle | body | string | 是 | `weekly_monday` | 周期 |
| format | body | string | 是 | `markdown` | 格式 |
| subscriberIds | body | string[] | 是 | `["u_10001"]` | 订阅人 |
| channels | body | string[] | 否 | `["in_app","email"]` | 通知渠道 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "subscriptionId": "sub_001",
    "enabled": true,
    "nextRunAt": "2026-05-18T09:00:00+08:00"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入报表页 | tab 加载 | `GET /reports/overview` | projectId、默认筛选 | 渲染图表 | 错误占位 |
| 切换时间范围 | 筛选 chip | `GET /reports/overview` | period | 更新图表 | Toast |
| 切换成员/类型 | 筛选 chip | `GET /reports/overview` | memberId/reportTypes | 更新图表 | Toast |
| 一键导出 Markdown | AI 卡片 | `POST /reports/export` | 当前筛选 | 下载/任务提示 | Toast |
| 点赞/点踩 | AI 卡片 | `POST /api/ai/feedback` | insightId | Toast | Toast |
| 订阅报表 | 弹窗/按钮 | `POST /reports/subscriptions` | 表单 | Toast | 表单错误 |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| period | segmented | 是 | 枚举 | 合法范围 | 请选择时间范围 |
| memberId | select | 否 | 成员存在 | 项目成员 | 成员无效 |
| reportTypes | checkbox | 否 | 枚举数组 | 类型合法 | 报表类型无效 |
| format | select | 是 | markdown/pdf/xlsx | 格式合法 | 导出格式无效 |
| subscriberIds | selector | 订阅必填 | 用户或角色 | 对象存在 | 请选择订阅人 |
| cycle | select | 订阅必填 | 枚举 | 周期合法 | 请选择订阅周期 |

### 9.1 提交规则

- 是否允许重复提交：导出和订阅请求期间不允许重复提交。
- 是否需要二次确认：批量订阅外部渠道可二次确认。
- 是否需要审计日志：导出、订阅、AI 生成和反馈需记录。
- 是否需要乐观锁或版本号：订阅更新可使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 日期 | date | string | 是 | 趋势图 |
| 实际剩余 | actualRemaining | number | 否 | 燃尽图 |
| 目标燃尽 | targetRemaining | number | 否 | 燃尽图 |
| 成员 | name | string | 是 | 工时图 |
| 计划工时 | plannedHours | number | 是 | 工时 |
| 实际工时 | actualHours | number | 是 | 工时 |
| 新增 Bug | createdCount | number | 是 | Bug 趋势 |
| 关闭 Bug | closedCount | number | 是 | Bug 趋势 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 时间范围 | period | string | last_30_days | 最近 30 天 / 本周 |
| 成员 | memberId | string | all | 全部成员 |
| 报表类型 | reportTypes | string | all | 进度/工时/质量 |

### 10.3 分页规则

- 当前为图表聚合数据，无分页。
- 报表明细表后续如扩展，默认页大小 20，最大 100。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出 Markdown | `POST /api/projects/{projectId}/reports/export` | md | 不适用 | 异步任务或同步文本 | 当前页面按钮 |
| 导出 PDF | `POST /api/projects/{projectId}/reports/export` | pdf | 不适用 | 异步任务 | P1 |
| 导出 Excel | `POST /api/projects/{projectId}/reports/export` | xlsx | 不适用 | 异步任务 | P1 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 报表订阅下发 |
| AI 周报洞察 | 是 | AI 报表服务 | 摘要、Markdown、反馈 |
| 审计日志 | 是 | 审计日志服务 | 导出和订阅 |
| WebSocket / SSE | 否 | 暂无 | 导出任务可轮询 |

## 13. 缓存与实时性

- 数据是否允许缓存：报表聚合可缓存 5-10 分钟。
- 缓存时间：AI 洞察按筛选条件缓存，任务/风险变更后失效。
- 页面返回时是否刷新：建议刷新总览。
- 是否需要轮询：导出异步任务需要轮询任务状态。
- 是否需要 WebSocket / SSE：当前不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `REPORT_PARAM_INVALID` | 参数错误 | Toast |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `REPORT_FORBIDDEN` | 无报表权限 | 无权限提示 |
| 404 / `PROJECT_NOT_FOUND` | 项目不存在 | 返回列表 |
| 409 / `REPORT_SUBSCRIPTION_EXISTS` | 重复订阅 | 提示已订阅 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 报表页 AI 洞察、燃尽图、工时图、Bug 趋势、阻塞负载分布均由接口返回。
- 时间范围、成员、报表类型筛选能刷新所有图表。
- Markdown 导出有接口支撑，返回下载地址或导出任务 ID。
- AI 点赞/点踩反馈可提交。
- 报表订阅支持周期、格式、订阅人和通知渠道。
- 无权限、无数据、导出失败等状态有明确返回结构。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 燃尽图单位使用故事点、任务数还是工时？ | 产品/后端 | 待确认 |
| Q2 | 工时数据来自手动填报、任务预估还是外部工时系统？ | 后端/数据 | 待确认 |
| Q3 | Bug 趋势是否接入缺陷系统？缺陷等级是否需要展示？ | 产品/后端 | 待确认 |
| Q4 | 导出 Markdown 是同步返回文本还是异步生成文件？ | 前后端 | 待确认 |

## 17. 前端备注

- 当前主承载数据在 `ProjectDetail.vue` 的 `burnPoints`、`barChartData`、`bugPoints`、`miniBars` 和 AI 报表文案。
- `ProjectReports.vue` 当前是固定 `currentTab = 'reports'` 的独立占位页，未在路由中单独挂载。
- 当前筛选 chip、一键导出 Markdown、点赞/点踩均未接接口。
