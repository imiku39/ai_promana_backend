# 项目看板后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/ProjectKanban.vue`，当前主要由 `views/ProjectDetail.vue` 的 `kanban` tab 承载  
> 页面定位：项目任务看板、状态流转规则、筛选和 AI 分配建议。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目看板 |
| 前端路由 | `/project/:id/kanban` |
| 前端文件 | `src/views/ProjectKanban.vue`、`src/views/ProjectDetail.vue` |
| 所属模块 | 项目管理 / 项目详情 / 看板 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 按任务状态列展示项目任务卡片：待开始、进行中、待评审、已完成、已阻塞。
- 支持按状态、优先级、本周截止、仅阻塞、关联里程碑筛选任务。
- 展示任务总数、阻塞任务数和状态流转规则。
- 支持任务状态流转、拖拽排序、标记阻塞、创建任务、查看任务详情。
- 提供 AI 分配建议，辅助任务转派和阻塞处理。

### 2.2 对接范围

- 看板列和任务卡片查询。
- 看板筛选、列内排序、状态流转规则。
- 任务新增、编辑、状态变更、拖拽排序、阻塞原因提交。
- AI 分配建议和采纳动作。
- 与成员负载、甘特排期、风险看板的数据联动。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `ProjectDetail.vue` | 当前看板 tab 的主要承载页 |
| `ProjectMembers.vue` | 任务负责人和负载数据来源 |
| `ProjectGantt.vue` | 任务时间计划和依赖关系 |
| `ProjectRisk.vue` | 阻塞任务进入风险列表 |
| `TaskDetail.vue` | 后续可点击任务卡进入任务详情 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全量任务权限 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 组织范围 |
| 项目负责人 | 是 | 是 | 是 | 是 | 是 | 可管理本项目任务 |
| 项目成员 | 是 | 是 | 视任务权限 | 否 | 否 | 可更新本人任务 |
| 协作者 | 是 | 否 | 视权限 | 否 | 否 | 只读或有限协作 |

### 3.1 权限规则

- 页面入口权限：需要 `project:kanban:read`。
- 按钮级权限：
  - 新建任务需要 `project:task:create`。
  - 编辑任务需要 `project:task:update`。
  - 拖拽状态需要 `project:task:transition`。
  - 删除任务需要 `project:task:delete`。
  - 采纳 AI 分配建议需要 `ai:task-suggestion:apply` 和任务编辑权限。
- 数据范围权限：成员只能查看授权项目任务；敏感任务可按任务可见范围过滤。
- 敏感字段脱敏规则：无权限不返回任务内部备注、成本、外部客户信息。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 项目详情头部 | 项目名称和状态 | 是 | `GET /api/projects/{projectId}` | 共用 |
| 看板统计 | 任务总数、阻塞数 | 是 | `GET /api/projects/{projectId}/kanban/summary` | 顶部 chip |
| 看板列和卡片 | 主看板 | 是 | `GET /api/projects/{projectId}/kanban` | 按列返回 |
| 状态流转规则 | 规则表格 | 是 | `GET /api/projects/{projectId}/kanban/flow-rules` | 当前静态 |
| 筛选选项 | 筛选 chip | 否 | `GET /api/projects/{projectId}/kanban/options` | P1 |
| AI 分配建议 | AI 卡片 | 否 | `GET /api/ai/project-kanban-suggestions` | P1 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 看板加载 | 请求处理中 | 列级 loading |
| empty | 列为空 | 当前状态无任务 | 列空状态 |
| dragging | 拖拽中 | 前端操作中 | 结束后提交 |
| blocked | 阻塞列高亮 | 任务状态为 blocked | 需要阻塞原因 |
| error | Toast | 接口异常或流转失败 | 回滚拖拽 |

## 5. 字段模型

### 5.1 看板列字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| columnId | string | 是 | 列 key | `todo` | 列 ID |
| name | string | 是 | 列标题 | `待开始` | 展示名称 |
| status | string | 是 | 状态 | `todo` | 任务状态枚举 |
| count | number | 是 | 数量标签 | `5` | 当前列任务总数 |
| order | number | 是 | 列顺序 | `1` | 从左到右 |
| styleLevel | string | 否 | 列样式 | `danger` | 阻塞列样式 |
| cards | array | 是 | 任务卡片 | `[]` | 当前页任务 |

### 5.2 任务卡片字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| taskId | string | 是 | 卡片 key | `task_001` | 任务 ID |
| title | string | 是 | 卡片标题 | `联调环境参数回灌` | 任务标题 |
| status | string | 是 | 所在列 | `doing` | 任务状态 |
| priority | string | 是 | 标签 | `P0` | 优先级 |
| tags | array | 否 | 标签组 | `["依赖平台组"]` | 标签 |
| note | string | 否 | 卡片说明 | `负责人：陈思远 · 进度 62%` | 摘要文案 |
| owner.id | string | 否 | 负责人 | `u_10002` | 用户 ID |
| owner.name | string | 否 | 负责人 | `陈思远` | 展示 |
| progress | number | 否 | 卡片说明 | `62` | 0-100 |
| deadline | string | 否 | 截止日期 | `2026-05-13` | 日期 |
| milestoneId | string | 否 | 关联里程碑 | `m_003` | 里程碑 |
| blockedReason | string | 否 | 阻塞原因 | `环境配置窗口未确认` | 阻塞必填 |
| dependencyTaskIds | string[] | 否 | 依赖任务 | `["task_002"]` | 依赖 |
| sortOrder | number | 是 | 列内排序 | `1000` | 拖拽排序 |
| version | number | 是 | 更新版本 | `3` | 乐观锁 |

### 5.3 流转规则字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| ruleId | string | 是 | 规则 key | `rule_001` | 规则 ID |
| rule | string | 是 | 规则列 | `待开始不可直接完成` | 规则标题 |
| description | string | 是 | 说明列 | `必须先进入进行中` | 说明 |
| notifyRule | string | 否 | 通知列 | `通知创建者与 PM` | 通知说明 |
| fromStatus | string | 否 | 流转源 | `todo` | 源状态 |
| toStatus | string | 否 | 流转目标 | `done` | 目标状态 |
| requiredFields | string[] | 否 | 必填字段 | `["blockedReason"]` | 流转校验 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| taskStatus | `todo` | 待开始 | neutral | 未开始 |
| taskStatus | `doing` | 进行中 | primary | 处理中 |
| taskStatus | `review` | 待评审 | warning | 待确认 |
| taskStatus | `done` | 已完成 | success | 完成 |
| taskStatus | `blocked` | 已阻塞 | danger | 阻塞 |
| priority | `P0` | P0 | danger | 最高优先级 |
| priority | `P1` | P1 | warning | 高优先级 |
| priority | `P2` | P2 | primary | 中优先级 |
| priority | `P3` | P3 | neutral | 低优先级 |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| taskTotal | number | 当前筛选下任务总数 | 顶部 chip | 当前展示 26 |
| blockedCount | number | 状态为 blocked 的任务数 | 顶部 chip | 当前展示 3 |
| p0p1Count | number | P0/P1 任务数 | 筛选 chip | 可选 |
| dueThisWeekCount | number | 本周截止任务数 | 筛选 chip | 可选 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取看板统计 | GET | `/api/projects/{projectId}/kanban/summary` | 任务总数和阻塞数 | P0 |
| API-002 | 获取看板列和任务 | GET | `/api/projects/{projectId}/kanban` | 看板主体 | P0 |
| API-003 | 获取状态流转规则 | GET | `/api/projects/{projectId}/kanban/flow-rules` | 规则表格 | P0 |
| API-004 | 创建任务 | POST | `/api/projects/{projectId}/tasks` | 新建任务 | P1 |
| API-005 | 更新任务 | PUT | `/api/projects/{projectId}/tasks/{taskId}` | 编辑任务 | P1 |
| API-006 | 任务状态流转 | POST | `/api/projects/{projectId}/tasks/{taskId}/transition` | 拖拽/变更状态 | P0 |
| API-007 | 更新任务排序 | PATCH | `/api/projects/{projectId}/kanban/order` | 列内/跨列排序 | P0 |
| API-008 | 获取 AI 看板建议 | GET | `/api/ai/project-kanban-suggestions` | AI 分配建议 | P1 |
| API-009 | 采纳 AI 看板建议 | POST | `/api/ai/project-kanban-suggestions/{suggestionId}/apply` | AI 调整任务 | P1 |

## 7. 接口详情

### API-002 获取看板列和任务

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/kanban`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| status | query | string | 否 | `blocked` | 状态筛选 |
| priorities | query | string | 否 | `P0,P1` | 优先级 |
| dueRange | query | string | 否 | `this_week` | 截止时间 |
| blockedOnly | query | boolean | 否 | `true` | 仅阻塞 |
| milestoneId | query | string | 否 | `m_003` | 关联里程碑 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "summary": {
      "taskTotal": 26,
      "blockedCount": 3
    },
    "columns": [
      {
        "columnId": "todo",
        "name": "待开始",
        "status": "todo",
        "count": 5,
        "order": 1,
        "cards": [
          {
            "taskId": "task_001",
            "title": "整理联调验证清单",
            "status": "todo",
            "priority": "P2",
            "tags": ["里程碑"],
            "owner": { "id": "u_10004", "name": "赵扬" },
            "estimateHours": 12,
            "deadline": "2026-05-14",
            "note": "负责人：赵扬 · 预估工时 1.5d",
            "sortOrder": 1000,
            "version": 1
          }
        ]
      }
    ]
  }
}
```

### API-003 获取状态流转规则

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/kanban/flow-rules`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "rules": [
      {
        "ruleId": "rule_001",
        "rule": "待开始不可直接完成",
        "description": "必须先进入进行中或待评审",
        "notifyRule": "无",
        "fromStatus": "todo",
        "toStatus": "done",
        "allowed": false
      },
      {
        "ruleId": "rule_002",
        "rule": "标记阻塞需填写原因",
        "description": "必须补充阻塞文本，并可关联阻塞依赖任务",
        "notifyRule": "通知创建者与 PM",
        "toStatus": "blocked",
        "requiredFields": ["blockedReason"]
      }
    ]
  }
}
```

### API-006 任务状态流转

**请求方式**

- Method: `POST`
- Path: `/api/projects/{projectId}/tasks/{taskId}/transition`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| projectId | path | string | 是 | `project_001` | 项目 ID |
| taskId | path | string | 是 | `task_001` | 任务 ID |
| fromStatus | body | string | 是 | `doing` | 原状态 |
| toStatus | body | string | 是 | `blocked` | 目标状态 |
| blockedReason | body | string | 否 | `环境配置窗口未确认` | 阻塞必填 |
| dependencyTaskIds | body | string[] | 否 | `["task_002"]` | 依赖任务 |
| version | body | number | 是 | `3` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "taskId": "task_001",
    "status": "blocked",
    "version": 4,
    "notifiedUsers": ["u_10001", "u_10002"]
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 流转不合法 | `400 TASK_TRANSITION_DENIED` | 回滚卡片并 Toast |
| 缺少阻塞原因 | `400 TASK_BLOCK_REASON_REQUIRED` | 打开阻塞原因表单 |
| 无权限 | `403 TASK_UPDATE_FORBIDDEN` | 回滚并提示 |
| 版本冲突 | `409 TASK_VERSION_CONFLICT` | 刷新看板 |

### API-009 采纳 AI 看板建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/project-kanban-suggestions/{suggestionId}/apply`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "changedTasks": ["task_009"],
    "message": "已将联调回灌日志补录转派给 QA 协作者。"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入看板 | tab 加载 | `GET /kanban`、`GET /flow-rules` | projectId | 渲染看板 | 错误占位 |
| 点击筛选 chip | 顶部筛选 | `GET /kanban` | 筛选条件 | 更新列 | Toast |
| 拖拽卡片跨列 | 卡片拖拽 | `POST /tasks/{id}/transition` | taskId、状态 | 更新卡片 | 回滚 Toast |
| 拖拽列内排序 | 卡片拖拽 | `PATCH /kanban/order` | 排序数组 | 更新排序 | 回滚 Toast |
| 标记阻塞 | 状态变更 | `POST /transition` | 阻塞原因 | 卡片进入阻塞列 | 表单错误 |
| 点击任务卡 | 任务卡片 | `GET /tasks/{id}` | taskId | 打开详情 | Toast |
| 采纳 AI 建议 | AI 卡片 | `POST /ai/project-kanban-suggestions/{id}/apply` | suggestionId | Toast，刷新看板 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| title | input | 是 | 2-120 字 | 标题合法 | 请输入任务标题 |
| priority | select | 是 | P0-P3 | 枚举合法 | 请选择优先级 |
| ownerId | selector | 否 | 用户存在 | 项目成员 | 负责人无效 |
| deadline | date | 否 | 日期格式 | 日期合法 | 截止日期无效 |
| status | select/drag | 是 | 枚举 | 流转合法 | 状态流转不合法 |
| blockedReason | textarea | 条件必填 | 标记阻塞时必填 | 非空、长度 | 请填写阻塞原因 |
| dependencyTaskIds | selector | 否 | 任务数组 | 任务存在且不可循环依赖 | 依赖任务无效 |

### 9.1 提交规则

- 是否允许重复提交：不允许。
- 是否需要二次确认：删除任务、批量 AI 调整需要二次确认。
- 是否需要审计日志：需要，任务创建、编辑、流转、删除、AI 采纳记录。
- 是否需要乐观锁或版本号：需要，任务更新和流转使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 任务标题 | title | string | 否 | 支持搜索可选 |
| 状态 | status | string | 是 | 看板列 |
| 优先级 | priority | string | 是 | P0-P3 |
| 负责人 | owner.name | string | 是 | 可筛选 |
| 截止日期 | deadline | string | 是 | 本周截止 |
| 进度 | progress | number | 是 | 0-100 |
| 阻塞原因 | blockedReason | string | 否 | 阻塞列 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 状态 | status | string | all | 全部状态 |
| 优先级 | priorities | string | all | P0/P1 |
| 截止时间 | dueRange | string | all | this_week |
| 仅阻塞 | blockedOnly | boolean | false | 只看阻塞 |
| 里程碑 | milestoneId | string | 空 | 关联里程碑 |

### 10.3 分页规则

- 看板建议按列返回，单列默认最多 50 张卡片。
- 大项目可支持 `columnPageSize` 和 `cursor` 分列加载。
- 列内排序使用 `sortOrder`，拖拽后增量提交。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出任务看板 | `POST /api/projects/{projectId}/kanban/export` | xlsx / csv | 不适用 | 异步任务 | P2 |
| 批量导入任务 | `POST /api/projects/{projectId}/tasks/import` | xlsx / csv | 待确认 | 上传并预览 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 状态变更、阻塞、完成通知 |
| AI 分配建议 | 是 | AI 建议服务 | 转派、优先级、阻塞处理 |
| 审计日志 | 是 | 审计日志服务 | 任务写操作 |
| WebSocket / SSE | 可选 | 项目事件流 | 多人协作看板实时更新 |

## 13. 缓存与实时性

- 数据是否允许缓存：看板数据可短缓存 10-30 秒，写操作后立即刷新。
- 缓存时间：流转规则可缓存 5 分钟。
- 页面返回时是否刷新：建议刷新看板和统计。
- 是否需要轮询：首期可不轮询，操作后刷新。
- 是否需要 WebSocket / SSE：后续多人协作建议接入。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `TASK_VALIDATE_FAILED` | 任务字段错误 | 表单错误 |
| 400 / `TASK_TRANSITION_DENIED` | 流转不合法 | 回滚卡片 |
| 400 / `TASK_BLOCK_REASON_REQUIRED` | 阻塞原因缺失 | 表单提示 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `TASK_UPDATE_FORBIDDEN` | 无任务编辑权限 | Toast |
| 404 / `TASK_NOT_FOUND` | 任务不存在 | 刷新看板 |
| 409 / `TASK_VERSION_CONFLICT` | 版本冲突 | 刷新看板 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 看板列、任务卡片、统计和流转规则均由后端返回。
- 筛选 chip 能按状态、优先级、本周截止、阻塞、里程碑刷新看板。
- 任务状态流转按后端规则校验，非法流转会回滚。
- 标记阻塞必须填写阻塞原因并通知相关人员。
- AI 分配建议可采纳，采纳后刷新任务负责人和成员负载。
- 任务写操作有权限控制、版本冲突处理和审计日志。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 看板列是否固定 5 列，还是项目模板可配置？ | 产品/后端 | 待确认 |
| Q2 | 拖拽排序首期是否需要实现，还是仅支持状态按钮流转？ | 前端/产品 | 待确认 |
| Q3 | 任务与甘特计划是否共用同一个任务模型？ | 后端/产品 | 待确认 |
| Q4 | 阻塞任务是否自动创建风险记录？ | 产品/后端 | 待确认 |

## 17. 前端备注

- 当前主承载数据在 `ProjectDetail.vue` 的 `kanbanCols` 和 `flowRules`。
- `ProjectKanban.vue` 当前是固定 `currentTab = 'kanban'` 的独立占位页，未在路由中单独挂载。
- 当前筛选按钮、卡片拖拽、任务详情、AI 一键采纳均未接接口。
