# 项目风险后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/ProjectRisk.vue`，当前主要由 `views/ProjectDetail.vue` 的 `risk` tab 承载  
> 页面定位：项目风险看板、资源冲突热力图、风险任务列表和 AI 根因分析。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 风险看板 |
| 前端路由 | `/project/:id/risk` |
| 前端文件 | `src/views/ProjectRisk.vue`、`src/views/ProjectDetail.vue` |
| 所属模块 | 项目管理 / 项目详情 / 风险 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示项目高危任务数、中度预警数和整体稳定度。
- 展示资源冲突预警热力图，辅助定位高冲突时间窗口。
- 展示 AI 深度洞察、风险根因和建议动作。
- 展示核心风险任务列表，包括风险等级、风险因子、进度阻碍和负责人。
- 支持导出风险清单、一键处理、风险状态流转和 AI 建议采纳。

### 2.2 对接范围

- 风险统计、资源冲突热力图、风险任务列表。
- 风险新增、编辑、状态流转、责任人分配。
- 风险清单导出和一键处理。
- AI 根因分析、完整风险报告生成、点赞/点踩反馈。
- 与看板阻塞任务、甘特延期节点、成员负载联动。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `ProjectDetail.vue` | 当前风险 tab 的主要承载页 |
| `ProjectKanban.vue` | 阻塞任务可转为风险 |
| `ProjectGantt.vue` | 延期节点进入风险评估 |
| `ProjectMembers.vue` | 成员负载用于资源冲突 |
| `ProjectReports.vue` | 风险趋势进入报表 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全量风险权限 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 组织范围 |
| 项目负责人 | 是 | 是 | 是 | 是 | 是 | 可处理本项目风险 |
| 项目成员 | 是 | 是 | 视责任范围 | 否 | 否 | 可反馈风险 |
| 协作者 | 是 | 否 | 否 | 否 | 否 | 只读 |

### 3.1 权限规则

- 页面入口权限：需要 `project:risk:read`。
- 按钮级权限：
  - 新增/编辑风险需要 `project:risk:update`。
  - 一键处理需要 `project:risk:resolve`。
  - 导出清单需要 `project:risk:export`。
  - AI 根因采纳需要 `ai:risk-suggestion:apply`。
- 数据范围权限：只返回当前项目授权范围内的风险任务。
- 敏感字段脱敏规则：无权限不返回客户影响、内部根因原始日志、责任追踪备注。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 项目详情头部 | 项目名称和状态 | 是 | `GET /api/projects/{projectId}` | 共用 |
| 风险统计 | 三个指标卡 | 是 | `GET /api/projects/{projectId}/risks/summary` | 高危、中度、稳定度 |
| 资源冲突热力图 | 热力图区块 | 是 | `GET /api/projects/{projectId}/risks/resource-heatmap` | 当前静态色块 |
| AI 深度洞察 | AI 洞察卡 | 否 | `GET /api/ai/project-risk-insights` | 根因分析 |
| 风险任务列表 | 表格 | 是 | `GET /api/projects/{projectId}/risks` | 支持筛选排序 |
| 风险规则/选项 | 筛选和表单选项 | 否 | `GET /api/projects/{projectId}/risks/options` | P1 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 风险加载 | 请求处理中 | 局部 loading |
| empty | 暂无风险 | 无风险任务 | 展示空状态 |
| error | Toast / 错误占位 | 接口异常 | 标准错误 |
| highRisk | 高危样式 | 高风险任务 | 红色标签 |
| resolving | 处理中 | 风险状态处理中 | 防重复操作 |

## 5. 字段模型

### 5.1 风险任务字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| riskId | string | 是 | 行 key | `risk_001` | 风险 ID |
| taskId | string | 否 | 关联任务 | `task_003` | 来源任务 |
| name | string | 是 | 任务名称 | `联调环境参数回灌` | 风险任务 |
| level | string | 是 | 风险等级 | `critical` | 等级枚举 |
| levelLabel | string | 是 | 展示 | `极高` | 中文 |
| factor | string | 是 | 风险因子 | `环境准备冲突` | 根因或因子 |
| blockRate | number | 是 | 进度阻碍 | `68` | 0-100 |
| owner.id | string | 是 | 负责人 | `u_10002` | 用户 ID |
| owner.name | string | 是 | 负责人 | `陈思远` | 展示 |
| status | string | 是 | 状态 | `open` | 风险状态 |
| dueDate | string | 否 | 处理期限 | `2026-05-13` | 日期 |
| mitigationPlan | string | 否 | 处理方案 | `协调测试窗口` | 方案 |
| source | string | 否 | 来源 | `kanban_blocked` | 看板/甘特/AI |
| version | number | 是 | 更新版本 | `2` | 乐观锁 |

### 5.2 风险统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| highRiskTaskCount | number | level 为 high/critical 的风险数 | 高危任务卡 | 当前展示 6 |
| highRiskDelta | number | 与上周差值 | 趋势 | 当前展示 +2 |
| mediumWarningCount | number | level 为 medium 的风险数 | 中度预警卡 | 当前展示 11 |
| stabilityRate | number | 综合稳定度评分 | 整体稳定度卡 | 当前展示 81% |

### 5.3 资源冲突热力图字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | string | 是 | 周日期 | `2026-05-11` | 日期 |
| dayLabel | string | 是 | 表头 | `周一` | 展示 |
| conflictRate | number | 是 | 色块深度 | `86` | 0-100 |
| level | number | 是 | 色块等级 | `5` | 0-5 |
| sourceCount | number | 否 | 冲突数 | `4` | 来源任务/成员数 |
| description | string | 否 | tooltip | `测试窗口冲突` | 说明 |

### 5.4 AI 洞察字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| insightId | string | 是 | key | `insight_001` | 洞察 ID |
| title | string | 是 | 标题 | `预测 · 概率 92%` | 展示 |
| content | string | 是 | 说明 | `周三将出现成员冲突` | 内容 |
| confidence | number | 否 | 置信度 | `0.92` | 0-1 |
| actions | array | 否 | 操作 | `[]` | 可采纳动作 |

### 5.5 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| riskLevel | `low` | 低 | success | 低风险 |
| riskLevel | `medium` | 中等 | warning | 中度预警 |
| riskLevel | `high` | 高危 | danger | 高风险 |
| riskLevel | `critical` | 极高 | danger | 最高风险 |
| riskStatus | `open` | 待处理 | danger | 未处理 |
| riskStatus | `processing` | 处理中 | warning | 处理中 |
| riskStatus | `mitigated` | 已缓解 | success | 已缓解 |
| riskStatus | `closed` | 已关闭 | neutral | 已关闭 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取风险统计 | GET | `/api/projects/{projectId}/risks/summary` | 指标卡 | P0 |
| API-002 | 获取资源冲突热力图 | GET | `/api/projects/{projectId}/risks/resource-heatmap` | 热力图 | P0 |
| API-003 | 获取风险列表 | GET | `/api/projects/{projectId}/risks` | 风险表格 | P0 |
| API-004 | 新增风险 | POST | `/api/projects/{projectId}/risks` | 新建风险 | P1 |
| API-005 | 更新风险 | PUT | `/api/projects/{projectId}/risks/{riskId}` | 编辑风险 | P1 |
| API-006 | 风险状态流转 | POST | `/api/projects/{projectId}/risks/{riskId}/transition` | 处理风险 | P0 |
| API-007 | 一键处理风险 | POST | `/api/projects/{projectId}/risks/batch-resolve` | 批量处理 | P1 |
| API-008 | 导出风险清单 | POST | `/api/projects/{projectId}/risks/export` | 导出 | P1 |
| API-009 | 获取 AI 风险洞察 | GET | `/api/ai/project-risk-insights` | AI 洞察 | P1 |
| API-010 | 采纳 AI 风险建议 | POST | `/api/ai/project-risk-insights/{insightId}/apply` | AI 处理 | P1 |

## 7. 接口详情

### API-003 获取风险列表

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/risks`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| level | query | string | 否 | `critical` | 风险等级 |
| status | query | string | 否 | `open` | 风险状态 |
| ownerId | query | string | 否 | `u_10002` | 负责人 |
| keyword | query | string | 否 | `联调` | 关键词 |
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
        "riskId": "risk_001",
        "taskId": "task_003",
        "name": "联调环境参数回灌",
        "level": "critical",
        "levelLabel": "极高",
        "factor": "环境准备冲突",
        "blockRate": 68,
        "owner": { "id": "u_10002", "name": "陈思远" },
        "status": "open",
        "statusLabel": "待处理",
        "dueDate": "2026-05-13",
        "mitigationPlan": "协调测试窗口并拆分回灌任务",
        "source": "kanban_blocked",
        "version": 2
      }
    ],
    "pagination": { "page": 1, "pageSize": 20, "total": 3 }
  }
}
```

### API-002 获取资源冲突热力图

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/risks/resource-heatmap`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| startDate | query | string | 否 | `2026-05-11` | 周起点 |
| days | query | number | 否 | `21` | 当前 UI 可展示 3 周色块 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    "cells": [
      {
        "date": "2026-05-11",
        "dayLabel": "周一",
        "conflictRate": 34,
        "level": 2,
        "sourceCount": 1,
        "description": "低负载"
      }
    ]
  }
}
```

### API-006 风险状态流转

**请求方式**

- Method: `POST`
- Path: `/api/projects/{projectId}/risks/{riskId}/transition`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| toStatus | body | string | 是 | `mitigated` | 目标状态 |
| mitigationPlan | body | string | 条件必填 | `已协调 QA 资源` | 处理方案 |
| ownerId | body | string | 否 | `u_10003` | 调整责任人 |
| version | body | number | 是 | `2` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "riskId": "risk_001",
    "status": "mitigated",
    "version": 3,
    "updatedAt": "2026-05-11T11:20:00+08:00"
  }
}
```

### API-009 获取 AI 风险洞察

**请求方式**

- Method: `GET`
- Path: `/api/ai/project-risk-insights`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | query | string | 是 | `project_001` | 项目 ID |
| context | query | string | 否 | `risk` | 上下文 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "insights": [
      {
        "insightId": "insight_001",
        "title": "预测 · 概率 92%",
        "content": "由于联调环境参数回灌与样本误差回归验证共用同一测试窗口，周三将出现成员冲突。",
        "confidence": 0.92,
        "actions": [
          { "key": "coordinate_resource", "label": "一键协调资源" },
          { "key": "generate_report", "label": "生成完整风险报告" }
        ]
      }
    ]
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入风险页 | tab 加载 | `GET /risks/summary`、`GET /resource-heatmap`、`GET /risks` | projectId | 渲染风险页 | 错误占位 |
| 筛选风险 | 筛选控件 | `GET /risks` | level/status/owner | 更新表格 | Toast |
| 导出清单 | 表格按钮 | `POST /risks/export` | 当前筛选 | 下载/任务提示 | Toast |
| 一键处理 | 页面按钮 | `POST /risks/batch-resolve` | 选中风险 | Toast，刷新列表 | Toast |
| 状态流转 | 行操作 | `POST /risks/{id}/transition` | 表单 | 刷新行 | 表单错误 |
| 生成完整风险报告 | AI 卡片 | `POST /ai/project-risk-insights/{id}/apply` | insightId | 生成报告/下载 | Toast |
| 点赞/点踩反馈 | AI 卡片 | `POST /api/ai/feedback` | insightId、feedback | Toast | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| name | input | 是 | 2-120 字 | 非空 | 请输入风险名称 |
| level | select | 是 | 枚举 | 合法等级 | 请选择风险等级 |
| factor | input | 是 | 2-100 字 | 非空 | 请输入风险因子 |
| blockRate | input | 是 | 0-100 | 数值合法 | 阻碍比例需为 0-100 |
| ownerId | selector | 是 | 用户存在 | 项目成员 | 请选择负责人 |
| mitigationPlan | textarea | 条件必填 | 处理中/缓解必填 | 非空 | 请填写处理方案 |
| dueDate | date | 否 | 日期格式 | 日期合法 | 期限无效 |

### 9.1 提交规则

- 是否允许重复提交：不允许。
- 是否需要二次确认：一键处理、关闭高危风险需要二次确认。
- 是否需要审计日志：需要，风险新增、编辑、流转、批量处理、AI 采纳记录。
- 是否需要乐观锁或版本号：需要，风险更新使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 任务名称 | name | string | 否 | 支持搜索 |
| 风险等级 | level | string | 是 | 极高/中等/高危 |
| 风险因子 | factor | string | 否 | 文本 |
| 进度阻碍 | blockRate | number | 是 | 0-100 |
| 负责人 | owner.name | string | 是 | 负责人 |
| 状态 | status | string | 是 | 待处理/处理中/已缓解 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 风险等级 | level | string | all | low/medium/high/critical |
| 状态 | status | string | all | open/processing/mitigated/closed |
| 负责人 | ownerId | string | 空 | 用户 ID |
| 关键词 | keyword | string | 空 | 风险名、因子 |

### 10.3 分页规则

- 默认页大小：20。
- 最大页大小：100。
- 默认排序：风险等级权重倒序、blockRate 倒序、更新时间倒序。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出风险清单 | `POST /api/projects/{projectId}/risks/export` | xlsx / csv / pdf | 不适用 | 异步任务 | 当前页面有按钮 |
| 生成风险报告 | `POST /api/ai/project-risk-insights/{id}/apply` | md / pdf | 不适用 | 异步任务 | AI 生成 |
| 导入风险 | `POST /api/projects/{projectId}/risks/import` | xlsx / csv | 待确认 | 上传并预览 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 高危风险、责任人变更、关闭通知 |
| AI 根因分析 | 是 | AI 风险服务 | 洞察、报告、协调建议 |
| 审计日志 | 是 | 审计日志服务 | 风险操作 |
| WebSocket / SSE | 可选 | 项目事件流 | 风险状态实时更新 |

## 13. 缓存与实时性

- 数据是否允许缓存：风险统计和热力图可短缓存 30-60 秒。
- 缓存时间：风险列表写操作后立即刷新。
- 页面返回时是否刷新：建议刷新统计、热力图、列表。
- 是否需要轮询：当前不需要。
- 是否需要 WebSocket / SSE：高协作项目后续可接。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `RISK_VALIDATE_FAILED` | 风险字段错误 | 表单错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `RISK_FORBIDDEN` | 无风险权限 | 无权限提示 |
| 404 / `RISK_NOT_FOUND` | 风险不存在 | 刷新列表 |
| 409 / `RISK_VERSION_CONFLICT` | 版本冲突 | 刷新 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 风险统计、热力图、AI 洞察和风险任务列表均由接口返回。
- 风险列表支持等级、状态、负责人、关键词筛选。
- 风险状态流转、一键处理、导出清单有接口支撑。
- AI 根因分析能返回洞察、置信度和可采纳动作。
- 风险写操作有权限控制、审计日志和版本冲突处理。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 风险等级算法由后端规则计算，还是允许项目负责人手动调整？ | 产品/后端 | 待确认 |
| Q2 | 看板阻塞任务是否自动同步为风险任务？ | 产品/后端 | 待确认 |
| Q3 | 资源冲突热力图展示 7 天还是 21 天？ | 产品/前端 | 待确认 |
| Q4 | AI 生成完整风险报告的输出格式是 Markdown、PDF 还是都支持？ | 产品/AI | 待确认 |

## 17. 前端备注

- 当前主承载数据在 `ProjectDetail.vue` 的 `heatmapBlocks`、`riskInsights`、`riskTasks`。
- `ProjectRisk.vue` 当前是固定 `currentTab = 'risk'` 的独立占位页，未在路由中单独挂载。
- 当前导出清单、一键处理、生成完整风险报告、点赞反馈均未接接口。
