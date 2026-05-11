# 项目甘特图后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/ProjectGantt.vue`，当前主要由 `views/ProjectDetail.vue` 的 `gantt` tab 承载  
> 页面定位：项目排期、基线对比、关键路径、依赖关系和 AI 排期建议。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目甘特图 |
| 前端路由 | `/project/:id/gantt` |
| 前端文件 | `src/views/ProjectGantt.vue`、`src/views/ProjectDetail.vue` |
| 所属模块 | 项目管理 / 项目详情 / 甘特图 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示项目排期甘特图，包含里程碑/任务、负责人、日期刻度、当前计划条和基线计划条。
- 支持按周、按日、按月切换视图，显示/隐藏基线、查看依赖关系和缩放。
- 展示关键路径、基线版本、超期节点、排期摘要和偏差说明。
- 提供 AI 排期建议，辅助追回偏差、生成补救任务和导出风险摘要。

### 2.2 对接范围

- 甘特图任务/里程碑排期查询。
- 基线版本、基线对比、偏差节点、关键路径。
- 视图粒度、依赖关系、缩放参数。
- 设置基线、更新排期、调整依赖关系。
- AI 排期建议和采纳动作。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `ProjectDetail.vue` | 当前甘特 tab 的主要承载页 |
| `ProjectKanban.vue` | 任务状态和负责人来源 |
| `ProjectRisk.vue` | 超期节点和关键路径风险进入风险看板 |
| `ProjectReports.vue` | 排期偏差进入报表趋势 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全量权限 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 组织范围 |
| 项目负责人 | 是 | 是 | 是 | 是 | 是 | 可管理排期和基线 |
| 项目成员 | 是 | 否 | 视任务权限 | 否 | 否 | 可查看排期 |
| 协作者 | 是 | 否 | 否 | 否 | 否 | 只读 |

### 3.1 权限规则

- 页面入口权限：需要 `project:gantt:read`。
- 按钮级权限：
  - 设置基线需要 `project:baseline:update`。
  - 更新任务排期需要 `project:schedule:update`。
  - 编辑依赖关系需要 `project:dependency:update`。
  - 导出排期需要 `project:gantt:export`。
  - 采纳 AI 排期建议需要 `ai:schedule-suggestion:apply` 和排期写权限。
- 数据范围权限：只返回当前用户有权限查看的任务和里程碑。
- 敏感字段脱敏规则：无权限不返回成本、内部备注、资源冲突详细说明。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 项目详情头部 | 项目名称、进度、时间范围 | 是 | `GET /api/projects/{projectId}` | 共用 |
| 甘特摘要 | 关键路径、基线版本、超期节点 | 是 | `GET /api/projects/{projectId}/gantt/summary` | 顶部 KPI |
| 甘特任务 | 甘特主体 | 是 | `GET /api/projects/{projectId}/gantt` | 刻度和任务条 |
| 基线版本 | 显示基线和设置基线 | 是 | `GET /api/projects/{projectId}/baselines` | P0 |
| 依赖关系 | 依赖线/列表 | 否 | `GET /api/projects/{projectId}/dependencies` | P1 |
| AI 排期建议 | 侧边建议 | 否 | `GET /api/ai/project-schedule-suggestions` | P1 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 甘特加载 | 请求处理中 | 局部 loading |
| empty | 无排期 | 项目无任务或无计划 | 引导创建 |
| error | Toast / 错误占位 | 接口异常 | 标准错误 |
| baselineVisible | 显示基线 | 返回 baseline 条 | 前端可切换 |
| delayed | 偏差节点 | 实际结束晚于基线 | 高亮 |

## 5. 字段模型

### 5.1 甘特任务字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| itemId | string | 是 | 行 key | `task_001` | 任务或里程碑 ID |
| itemType | string | 是 | 行类型 | `task` | task/milestone |
| name | string | 是 | 任务名称 | `联调验证` | 展示名称 |
| owner.id | string | 否 | 负责人 | `u_10002` | 用户 ID |
| owner.name | string | 否 | 负责人 | `陈思远` | 展示 |
| plannedStart | string | 是 | 当前计划条 | `2026-05-08` | 当前开始 |
| plannedEnd | string | 是 | 当前计划条 | `2026-05-16` | 当前结束 |
| baselineStart | string | 否 | 基线条 | `2026-05-06` | 基线开始 |
| baselineEnd | string | 否 | 基线条 | `2026-05-14` | 基线结束 |
| progress | number | 否 | 可选 | `66` | 0-100 |
| status | string | 是 | 样式 | `delayed` | 状态 |
| barClass | string | 否 | 颜色样式 | `red` | 前端样式语义 |
| dependencyIds | string[] | 否 | 依赖关系 | `["task_002"]` | 前置任务 |
| isCriticalPath | boolean | 是 | 关键路径 | `true` | 是否关键路径 |
| delayDays | number | 否 | 偏差 | `2` | 正数为延期 |
| version | number | 是 | 更新排期 | `3` | 乐观锁 |

### 5.2 甘特刻度字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| viewMode | string | 是 | 工具栏 | `week` | day/week/month |
| timelineStart | string | 是 | 刻度起点 | `2026-04-14` | 日期 |
| timelineEnd | string | 是 | 刻度终点 | `2026-06-30` | 日期 |
| ticks | array | 是 | 表头日期 | `["04/14"]` | 刻度展示 |

### 5.3 摘要字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| criticalPathCount | number | 是 | 关键路径 KPI | `3` | 关键路径段数 |
| baselineVersion | string | 是 | 基线版本 KPI | `V2` | 当前基线版本 |
| delayedNodeCount | number | 是 | 超期节点 KPI | `1` | 超期节点数 |
| criticalPathText | string | 否 | 排期摘要 | `开发 → 联调 → 验收` | 展示文案 |
| delaySummary | string | 否 | 排期摘要 | `+2 天` | 偏差文案 |
| description | string | 否 | 摘要说明 | `偏差集中在联调验证` | 文案 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| viewMode | `day` | 按日 | active | 日视图 |
| viewMode | `week` | 按周 | active | 默认 |
| viewMode | `month` | 按月 | active | 月视图 |
| itemType | `task` | 任务 | normal | 普通任务 |
| itemType | `milestone` | 里程碑 | primary | 里程碑 |
| scheduleStatus | `normal` | 正常 | success | 正常 |
| scheduleStatus | `delayed` | 延期 | danger | 晚于基线 |
| scheduleStatus | `at_risk` | 有风险 | warning | 可能延期 |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| criticalPathCount | number | 标记为关键路径的连续段数 | 顶部 KPI | 当前展示 3 |
| delayedNodeCount | number | delayDays > 0 的节点数 | 顶部 KPI | 当前展示 1 |
| maxDelayDays | number | 最大延期天数 | 摘要 | 当前展示 +2 天 |
| recoverableDays | number | AI 估算可追回天数 | AI 建议 | 当前展示 0.8 天 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取甘特摘要 | GET | `/api/projects/{projectId}/gantt/summary` | KPI 和摘要 | P0 |
| API-002 | 获取甘特数据 | GET | `/api/projects/{projectId}/gantt` | 甘特主体 | P0 |
| API-003 | 获取基线版本 | GET | `/api/projects/{projectId}/baselines` | 基线列表 | P0 |
| API-004 | 设置项目基线 | POST | `/api/projects/{projectId}/baseline` | 设置基线 | P0 |
| API-005 | 更新任务排期 | PATCH | `/api/projects/{projectId}/schedule/items/{itemId}` | 调整计划 | P1 |
| API-006 | 获取依赖关系 | GET | `/api/projects/{projectId}/dependencies` | 依赖关系 | P1 |
| API-007 | 更新依赖关系 | PUT | `/api/projects/{projectId}/dependencies` | 保存依赖 | P1 |
| API-008 | 获取 AI 排期建议 | GET | `/api/ai/project-schedule-suggestions` | AI 建议 | P1 |
| API-009 | 采纳 AI 排期建议 | POST | `/api/ai/project-schedule-suggestions/{suggestionId}/apply` | 生成补救计划 | P1 |

## 7. 接口详情

### API-002 获取甘特数据

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/gantt`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| viewMode | query | string | 否 | `week` | day/week/month |
| startDate | query | string | 否 | `2026-04-14` | 时间轴起点 |
| endDate | query | string | 否 | `2026-06-30` | 时间轴终点 |
| baselineVersion | query | string | 否 | `V2` | 基线版本 |
| showBaseline | query | boolean | 否 | `true` | 是否返回基线 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "timeline": {
      "viewMode": "week",
      "timelineStart": "2026-04-14",
      "timelineEnd": "2026-06-30",
      "ticks": ["04/14", "04/21", "04/28", "05/05", "05/12"]
    },
    "summary": {
      "criticalPathCount": 3,
      "baselineVersion": "V2",
      "delayedNodeCount": 1,
      "criticalPathText": "开发 → 联调 → 验收",
      "delaySummary": "+2 天",
      "description": "当前实际计划主要偏差集中在联调验证。"
    },
    "items": [
      {
        "itemId": "task_003",
        "itemType": "task",
        "name": "联调验证",
        "owner": { "id": "u_10002", "name": "陈思远" },
        "plannedStart": "2026-05-08",
        "plannedEnd": "2026-05-20",
        "baselineStart": "2026-05-06",
        "baselineEnd": "2026-05-16",
        "progress": 66,
        "status": "delayed",
        "barClass": "red",
        "dependencyIds": ["task_002"],
        "isCriticalPath": true,
        "delayDays": 2,
        "version": 4
      }
    ]
  }
}
```

### API-004 设置项目基线

**请求方式**

- Method: `POST`
- Path: `/api/projects/{projectId}/baseline`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | body | string | 是 | `V3` | 基线名称 |
| description | body | string | 否 | `联调调整后基线` | 说明 |
| source | body | string | 是 | `current_schedule` | 基线来源 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "baselineId": "baseline_v3",
    "version": "V3",
    "createdAt": "2026-05-11T11:00:00+08:00"
  }
}
```

### API-005 更新任务排期

**请求方式**

- Method: `PATCH`
- Path: `/api/projects/{projectId}/schedule/items/{itemId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| plannedStart | body | string | 是 | `2026-05-08` | 新开始日期 |
| plannedEnd | body | string | 是 | `2026-05-20` | 新结束日期 |
| ownerId | body | string | 否 | `u_10002` | 负责人 |
| version | body | number | 是 | `4` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "itemId": "task_003",
    "delayDays": 2,
    "version": 5,
    "affectedDependencies": ["task_004"]
  }
}
```

### API-009 采纳 AI 排期建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/project-schedule-suggestions/{suggestionId}/apply`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "createdTasks": ["task_020"],
    "updatedScheduleItems": ["task_003"],
    "recoverableDays": 0.8
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入甘特页 | tab 加载 | `GET /gantt` | projectId、viewMode | 渲染甘特 | 错误占位 |
| 切换按周/日/月 | 工具栏 | `GET /gantt` | viewMode | 切换刻度 | Toast |
| 显示/隐藏基线 | 工具栏 | `GET /gantt` 或前端切换 | showBaseline | 显示基线条 | Toast |
| 查看依赖关系 | 工具栏 | `GET /dependencies` | projectId | 显示依赖 | Toast |
| 设置基线 | 页面按钮 | `POST /baseline` | 当前排期 | Toast，刷新版本 | Toast |
| 调整任务日期 | 甘特条拖拽/表单 | `PATCH /schedule/items/{id}` | 日期和版本 | 刷新甘特 | 回滚 Toast |
| 采纳 AI 排期建议 | AI 卡片 | `POST /ai/project-schedule-suggestions/{id}/apply` | suggestionId | 生成补救计划 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| plannedStart | date | 是 | 日期格式 | 不晚于结束日期 | 请选择开始日期 |
| plannedEnd | date | 是 | 晚于开始日期 | 日期范围合法 | 结束日期需晚于开始日期 |
| ownerId | selector | 否 | 用户存在 | 项目成员 | 负责人无效 |
| dependencyIds | selector | 否 | 任务数组 | 不允许循环依赖 | 依赖关系无效 |
| baselineName | input | 是 | 1-40 字 | 版本唯一 | 基线名称已存在 |
| description | textarea | 否 | 最长 500 字 | 长度合法 | 说明过长 |

### 9.1 提交规则

- 是否允许重复提交：不允许。
- 是否需要二次确认：设置新基线、批量 AI 调整排期需要二次确认。
- 是否需要审计日志：需要，基线、排期、依赖调整都记录。
- 是否需要乐观锁或版本号：需要，排期项更新使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 任务/里程碑 | name | string | 否 | 左侧列表 |
| 负责人 | owner.name | string | 是 | 左侧列表 |
| 计划开始 | plannedStart | string | 是 | 甘特条 |
| 计划结束 | plannedEnd | string | 是 | 甘特条 |
| 基线开始 | baselineStart | string | 否 | 基线条 |
| 基线结束 | baselineEnd | string | 否 | 基线条 |
| 延期天数 | delayDays | number | 是 | 偏差 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 视图模式 | viewMode | string | week | day/week/month |
| 时间起点 | startDate | string | 项目开始 | 时间轴起点 |
| 时间终点 | endDate | string | 项目结束 | 时间轴终点 |
| 基线版本 | baselineVersion | string | 当前版本 | 基线对比 |
| 显示基线 | showBaseline | boolean | true | 是否返回基线 |

### 10.3 分页规则

- 甘特图首期建议返回项目排期全量任务；任务超过 200 条时支持按层级懒加载。
- 默认排序：里程碑顺序、计划开始时间、sortOrder。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出甘特图 | `POST /api/projects/{projectId}/gantt/export` | pdf / png / xlsx | 不适用 | 异步任务 | P1 |
| 导入排期 | `POST /api/projects/{projectId}/schedule/import` | xlsx / mpp | 待确认 | 上传并预览 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 基线变更、排期调整通知 |
| AI 排期建议 | 是 | AI 建议服务 | 追回偏差、补救任务 |
| 审计日志 | 是 | 审计日志服务 | 排期和基线操作 |
| WebSocket / SSE | 可选 | 项目事件流 | 多人编辑甘特实时同步 |

## 13. 缓存与实时性

- 数据是否允许缓存：甘特数据可短缓存 30 秒，基线列表可缓存 5 分钟。
- 缓存时间：写操作后立即失效。
- 页面返回时是否刷新：建议刷新甘特和摘要。
- 是否需要轮询：当前不需要。
- 是否需要 WebSocket / SSE：后续多人协作可接入。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `SCHEDULE_DATE_INVALID` | 日期范围错误 | 表单错误 |
| 400 / `DEPENDENCY_CYCLE_DETECTED` | 依赖循环 | 提示依赖无效 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `SCHEDULE_UPDATE_FORBIDDEN` | 无排期权限 | Toast |
| 404 / `SCHEDULE_ITEM_NOT_FOUND` | 排期项不存在 | 刷新 |
| 409 / `BASELINE_VERSION_EXISTS` | 基线名称重复 | 表单错误 |
| 409 / `SCHEDULE_VERSION_CONFLICT` | 版本冲突 | 刷新甘特 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 甘特摘要、刻度、任务条和基线条均由接口返回。
- 按日/周/月切换能正确返回不同刻度。
- 设置基线、更新排期、更新依赖有接口和权限控制。
- 延期节点、关键路径、超期节点数计算口径明确。
- AI 排期建议可采纳并返回创建任务、调整排期、预计追回天数。
- 排期写操作支持审计日志和版本冲突处理。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 甘特条位置由后端返回日期即可，还是需要返回前端百分比布局字段？ | 前后端 | 待确认 |
| Q2 | 基线版本是否允许多版本对比？ | 产品/后端 | 待确认 |
| Q3 | 是否需要支持里程碑和任务层级展开？ | 产品/前端 | 待确认 |
| Q4 | 依赖关系是否首期可视化展示，还是只返回列表？ | 产品/前端 | 待确认 |

## 17. 前端备注

- 当前主承载数据在 `ProjectDetail.vue` 的 `ganttDates`、`ganttData` 和 AI 排期文案。
- `ProjectGantt.vue` 当前是固定 `currentTab = 'gantt'` 的独立占位页，未在路由中单独挂载。
- 当前按周/按日/按月、显示基线、依赖关系、缩放、采纳建议均未接接口。
