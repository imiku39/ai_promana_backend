# 个人工作台后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Workbench.vue`  
> 页面定位：个人工作台聚合页，覆盖结构化日志、个人看板、PBC 目标和新建任务弹窗。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 个人工作台 |
| 前端路由 | `/workbench` |
| 前端文件 | `src/views/Workbench.vue` |
| 所属模块 | 个人工作台 / 日志 / 个人看板 / PBC / 任务创建 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 将当前用户的结构化日志、个人任务看板和 PBC 目标集中在一个工作台中。
- 支持日志 tab：编辑今日日志、AI 一键生成、查看今日焦点和最近日志互动。
- 支持看板 tab：按项目/事项分组展示个人任务，并按优先级、本周截止、阻塞状态筛选。
- 支持 PBC tab：展示个人目标、达成率、绑定任务、周期评估对话和 AI 趋势提示。
- 支持新建任务弹窗：创建个人任务草稿、保存草稿、创建任务，并同步到日志、看板和 PBC。
- 支持工作台上下文 AI 助手：生成日志草稿、任务提醒、PBC 绑定建议。

### 2.2 对接范围

- 个人工作台首屏聚合数据。
- 今日日志详情保存、AI 生成日志草稿、日志互动列表。
- 个人看板任务列表、筛选、任务状态/阻塞状态。
- PBC 目标列表、周期评估对话、任务绑定、趋势预测。
- 新建任务弹窗选项、保存草稿、创建任务。
- AI 工作建议、AI 创建任务建议、AI 自动绑定任务。
- 顶部当前用户信息和通知未读数。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Dashboard.vue` | 可从全局工作台进入个人工作台，也有快速创建任务入口 |
| `TaskDetail.vue` | 个人看板任务卡片可进入任务详情 |
| `ProjectKanban.vue` | 项目看板任务与个人看板可共享任务模型 |
| `ProjectMembers.vue` | 任务负责人和协作成员来源 |
| `Notifications.vue` | 任务提醒、日志互动、PBC 反馈通知 |
| `Settings.vue` | 通知偏好、AI 偏好影响工作台提醒 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 视权限 | 是 | 可查看本人工作台，代看他人需额外权限 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 默认本人工作台 |
| 项目负责人 | 是 | 是 | 是 | 视权限 | 是 | 可创建和管理本人任务 |
| 成员 | 是 | 是 | 是 | 视权限 | 否 | 默认本人日志、任务、PBC |
| 协作者 | 视权限 | 视权限 | 视权限 | 否 | 否 | 取决于账号权限 |

### 3.1 权限规则

- 页面入口权限：访问 `/workbench` 需要登录态和 `workbench:read`。
- 按钮级权限：
  - “新建任务”“创建任务”需要 `task:create`。
  - “保存草稿”需要 `task:draft:create`。
  - “AI 一键生成”“立即生成”需要 `ai:workbench:generate`。
  - “自动绑定任务”需要 `pbc:task:bind`。
  - 保存日志需要 `worklog:update`。
- 数据范围权限：默认只返回当前登录用户的日志、个人任务、PBC 目标；管理员查看他人工作台需 `workbench:read:any`。
- 敏感字段脱敏规则：上级反馈、个人自评、日志内容默认只对本人、直属上级和授权管理员可见。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 当前静态为张工/研发总监 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 当前静态为 5 |
| 工作台总览 | 日志、看板、PBC 聚合 | 是 | `GET /api/workbench/overview` | 首屏建议聚合 |
| 今日日志 | 日志 tab 主体 | 是 | `GET /api/workbench/logs/today` | 可并入 overview |
| 个人看板 | 看板 tab 主体 | 是 | `GET /api/workbench/kanban` | 支持筛选 |
| PBC 目标 | PBC tab 主体 | 是 | `GET /api/workbench/pbc` | 目标和评估 |
| 新建任务选项 | 弹窗下拉和模板 | 否 | `GET /api/workbench/task-create-options` | 打开弹窗时加载 |
| AI 工作建议 | AI 抽屉和卡片 | 否 | `GET /api/ai/workbench-suggestions` | 打开抽屉时加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 数据加载中 | 请求处理中 | 当前未接 |
| empty | 无日志/无任务/无 PBC | 当前范围无数据 | 分 tab 空状态 |
| error | Toast / 错误占位 | 接口异常 | 标准错误 |
| saving | 保存草稿/创建任务/保存日志 | 写请求处理中 | 禁用按钮 |
| filtered | 看板筛选生效 | 后端按筛选返回 | 当前为前端本地 computed |
| modalOpen | 新建任务弹窗 | 加载创建选项 | 当前静态 |

## 5. 字段模型

### 5.1 工作台总览字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| userId | string | 是 | 隐含字段 | `u_10001` | 当前用户 |
| activeTab | string | 否 | query/tab | `logs` | logs/kanban/pbc |
| focus.todoCount | number | 是 | 今日焦点 | `7` | 待办任务数 |
| focus.logInteractionCount | number | 是 | 今日焦点 | `12` | 日志互动数 |
| focus.aiSummary | string | 否 | 今日焦点说明 | `AI 判断你今天...` | AI 文案 |
| notificationUnreadCount | number | 是 | 顶部角标 | `5` | 未读数 |

### 5.2 日志字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| logId | string | 是 | 今日日志 | `log_20260511` | 日志 ID |
| date | string | 是 | 今日日志 | `2026-05-11` | 日志日期 |
| completed | string | 是 | 今日完成 | `完成 Q3...` | 今日完成内容 |
| tomorrowPlan | string | 是 | 明日计划 | `跟进平台组...` | 明日计划 |
| blockers | string | 否 | 阻塞问题 | `联调环境参数回灌...` | 阻塞描述 |
| aiDraftAvailable | boolean | 否 | AI 日志建议 | `true` | 是否有 AI 草稿 |
| interactions | array | 是 | 最近日志互动 | `[]` | 评论、点赞、AI 摘要 |
| version | number | 是 | 保存日志 | `3` | 乐观锁 |

### 5.3 个人看板字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| columnId | string | 是 | 看板列 key | `project_001` | 当前 UI 按项目/事项分组 |
| columnName | string | 是 | 看板列标题 | `纳米晶体结构优化` | 项目或通用事项 |
| tasks | array | 是 | 任务卡片 | `[]` | 任务列表 |
| tasks[].id | string | 是 | 任务 key | `task_001` | 任务 ID |
| tasks[].title | string | 是 | 任务标题 | `更新联调验证脚本` | 标题 |
| tasks[].priority | string | 是 | 优先级标签 | `P1` | P0-P3 |
| tasks[].tag | string | 否 | 标签 | `里程碑` | 标签 |
| tasks[].deadline | string | 是 | 截止信息 | `今天 18:00` | 可为展示文案 |
| tasks[].deadlineAt | string | 否 | 截止时间 | `2026-05-11T18:00:00+08:00` | 机器时间 |
| tasks[].progress | number | 否 | 进度 | `65` | 0-100 |
| tasks[].isBlocked | boolean | 是 | 阻塞筛选 | `false` | 是否阻塞 |
| tasks[].blockedReason | string | 否 | 阻塞原因 | `协议接口未冻结` | 阻塞任务 |
| tasks[].pbcGoalId | string | 否 | PBC 绑定 | `pbc_001` | 绑定目标 |

### 5.4 PBC 目标字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| goalId | string | 是 | 目标 key | `pbc_001` | PBC 目标 ID |
| goalType | string | 是 | 标签 | `numeric` | 数值型/里程碑型 |
| title | string | 是 | 目标标题 | `提升团队协作效率` | 目标名称 |
| description | string | 否 | 目标说明 | `对齐部门 OKR...` | 说明 |
| progressRate | number | 是 | 达成率 | `64` | 0-100 |
| status | string | 是 | 目标状态 | `in_progress` | 进行中/待反馈 |
| boundTaskCount | number | 是 | 绑定任务 | `8` | 绑定任务数 |
| completedTaskCount | number | 是 | 已完成 | `5` | 完成任务数 |
| selfReview | string | 否 | 周期评估对话 | `本周期已完成...` | 自评 |
| managerFeedback | string | 否 | 周期评估对话 | `方向正确...` | 上级反馈 |
| forecastRate | number | 否 | AI 趋势提示 | `73` | 预测达成率 |
| forecastDays | number | 否 | AI 趋势提示 | `7` | 预测周期 |

### 5.5 新建任务字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| title | string | 是 | 任务名称 | `补齐联调验证说明与样本校验结论` | 任务标题 |
| projectId | string | 否 | 关联项目 | `project_001` | 通用事项可为空或 special |
| assigneeId | string | 是 | 负责人 | `u_10001` | 默认本人 |
| priority | string | 是 | 任务优先级 | `P1` | P0-P3 |
| status | string | 是 | 任务状态 | `todo` | 默认待开始 |
| templateType | string | 否 | 任务模板 | `log_followup` | 日志/看板/PBC |
| startDate | string | 否 | 开始日期 | `2026-04-28` | 日期 |
| deadlineAt | string | 是 | 截止日期 | `2026-04-29T18:00:00+08:00` | 截止时间 |
| estimateHours | number | 否 | 预计工时 | `12` | 建议统一小时 |
| progress | number | 否 | 当前进度 | `0` | 0-100 |
| riskType | string | 否 | 风险标记 | `none` | 无/阻塞/联调/资源 |
| description | string | 否 | 任务说明 | `补齐联调验证...` | 最长 2000 字 |
| logSection | string | 否 | 日志归属区块 | `completed` | 今日完成/明日计划/阻塞问题 |
| pbcGoalId | string | 否 | 绑定 PBC 目标 | `pbc_001` | 可为空 |
| reviewerId | string | 否 | 评审人 | `u_10002` | 评审人 |
| notifyTargetIds | string[] | 否 | 通知对象 | `["role_pm","u_10003"]` | 用户/角色 |
| tags | string[] | 否 | 任务标签 | `["联调","PBC"]` | 标签 |
| reminderChannels | string[] | 否 | 提醒方式 | `["in_app","wechat_work"]` | 通知渠道 |
| syncOptions | object | 否 | 同步开关 | `{}` | 日志、看板、PBC 联动 |

### 5.6 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| workbenchTab | `logs` | 日志 | active | 默认 tab |
| workbenchTab | `kanban` | 看板 | active | 个人看板 |
| workbenchTab | `pbc` | PBC | active | 目标 |
| priority | `P0` | P0 | danger | 最高优先级 |
| priority | `P1` | P1 | warning | 高优先级 |
| priority | `P2` | P2 | primary | 中优先级 |
| priority | `P3` | P3 | neutral | 低优先级 |
| taskStatus | `todo` | 待开始 | neutral | 默认 |
| taskStatus | `in_progress` | 进行中 | primary | 进行中 |
| taskStatus | `review` | 待评审 | warning | 待评审 |
| taskStatus | `done` | 已完成 | success | 已完成 |
| taskStatus | `blocked` | 已阻塞 | danger | 阻塞 |
| logSection | `completed` | 今日完成 | success | 日志区块 |
| logSection | `tomorrow_plan` | 明日计划 | primary | 日志区块 |
| logSection | `blockers` | 阻塞问题 | danger | 日志区块 |
| pbcGoalType | `numeric` | 数值型目标 | success | 数值型 |
| pbcGoalType | `milestone` | 里程碑型目标 | warning | 里程碑型 |

### 5.7 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| todoTaskCount | number | 当前用户未完成任务数 | 今日焦点 | 当前展示 7 |
| logInteractionCount | number | 当天日志评论/点赞/AI 摘要数 | 今日焦点 | 当前展示 12 |
| pbcProgressRate | number | 已完成绑定任务权重 / 目标权重 | PBC 目标 | 当前展示 64%、51% |
| pbcForecastRate | number | AI 预测目标达成率 | AI 趋势提示 | 当前展示 73% |
| blockedTaskCount | number | 当前用户阻塞任务数 | 看板筛选/AI | 可选 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取个人工作台总览 | GET | `/api/workbench/overview` | 首屏聚合 | P0 |
| API-002 | 获取今日日志 | GET | `/api/workbench/logs/today` | 日志 tab | P0 |
| API-003 | 保存今日日志 | PUT | `/api/workbench/logs/today` | 保存日志 | P0 |
| API-004 | 获取日志互动 | GET | `/api/workbench/logs/interactions` | 最近日志互动 | P1 |
| API-005 | AI 生成日志草稿 | POST | `/api/ai/workbench/log-draft` | AI 一键生成/草稿 | P1 |
| API-006 | 获取个人看板 | GET | `/api/workbench/kanban` | 看板 tab | P0 |
| API-007 | 获取 PBC 目标 | GET | `/api/workbench/pbc` | PBC tab | P0 |
| API-008 | 绑定任务到 PBC 目标 | POST | `/api/workbench/pbc/{goalId}/bind-tasks` | 自动绑定任务 | P1 |
| API-009 | 获取任务创建选项 | GET | `/api/workbench/task-create-options` | 新建任务弹窗 | P0 |
| API-010 | 保存任务草稿 | POST | `/api/tasks/drafts` | 保存草稿 | P0 |
| API-011 | 创建任务 | POST | `/api/tasks` | 创建任务 | P0 |
| API-012 | 获取 AI 工作台建议 | GET | `/api/ai/workbench-suggestions` | AI 抽屉 | P1 |
| API-013 | 采纳 AI 工作台建议 | POST | `/api/ai/workbench-suggestions/{suggestionId}/apply` | 生成日志/绑定 PBC | P1 |
| API-014 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部通知角标 | P0 |

## 7. 接口详情

### API-001 获取个人工作台总览

**请求方式**

- Method: `GET`
- Path: `/api/workbench/overview`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| tab | query | string | 否 | `logs` | 当前 tab |
| date | query | string | 否 | `2026-05-11` | 日志和统计日期 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "focus": {
      "todoTaskCount": 7,
      "logInteractionCount": 12,
      "aiSummary": "AI 判断你今天最值得优先处理的是“联调环境参数回灌”和“P0 代码评审”。"
    },
    "todayLog": {
      "logId": "log_20260511",
      "date": "2026-05-11",
      "completed": "1. 完成 Q3 实验室能效评估报告初稿。",
      "tomorrowPlan": "1. 跟进平台组联调环境准备。",
      "blockers": "当前联调环境参数回灌任务仍缺少资源窗口确认。",
      "version": 3
    },
    "kanban": {
      "columns": []
    },
    "pbc": {
      "goals": []
    },
    "aiCards": {
      "logSuggestion": {
        "title": "AI 日志建议",
        "content": "你今天完成的 3 个任务中，有 2 个可自动映射到日报。"
      },
      "pbcTrend": {
        "title": "AI 趋势提示",
        "content": "按照当前任务完成速度，本周期 PBC 达成率预计将在 7 天内提升至 73%。"
      }
    }
  }
}
```

### API-003 保存今日日志

**请求方式**

- Method: `PUT`
- Path: `/api/workbench/logs/today`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| date | body | string | 是 | `2026-05-11` | 日志日期 |
| completed | body | string | 是 | `完成 Q3...` | 今日完成 |
| tomorrowPlan | body | string | 否 | `跟进平台组...` | 明日计划 |
| blockers | body | string | 否 | `联调环境...` | 阻塞问题 |
| version | body | number | 是 | `3` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "logId": "log_20260511",
    "version": 4,
    "updatedAt": "2026-05-11T14:30:00+08:00"
  }
}
```

### API-006 获取个人看板

**请求方式**

- Method: `GET`
- Path: `/api/workbench/kanban`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| priority | query | string | 否 | `P0` | P0/P1/P2/P3 |
| dueRange | query | string | 否 | `this_week` | 本周截止 |
| blockedOnly | query | boolean | 否 | `true` | 仅阻塞 |
| keyword | query | string | 否 | `联调` | 任务搜索 |
| groupBy | query | string | 否 | `project` | project/status |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "columns": [
      {
        "columnId": "project_001",
        "columnName": "纳米晶体结构优化",
        "tasks": [
          {
            "id": "task_001",
            "title": "更新联调验证脚本",
            "priority": "P1",
            "tag": "里程碑",
            "deadline": "今天 18:00",
            "deadlineAt": "2026-05-11T18:00:00+08:00",
            "progress": 65,
            "isBlocked": false,
            "pbcGoalId": null
          }
        ]
      }
    ],
    "summary": {
      "taskTotal": 7,
      "blockedTaskCount": 1,
      "p0p1TaskCount": 4,
      "dueThisWeekCount": 4
    }
  }
}
```

### API-007 获取 PBC 目标

**请求方式**

- Method: `GET`
- Path: `/api/workbench/pbc`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| periodId | query | string | 否 | `2026Q2` | PBC 周期 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "periodId": "2026Q2",
    "goals": [
      {
        "goalId": "pbc_001",
        "goalType": "numeric",
        "title": "提升团队协作效率",
        "description": "对齐部门 OKR：缩短联调和日报协作耗时。",
        "progressRate": 64,
        "status": "in_progress",
        "boundTaskCount": 8,
        "completedTaskCount": 5,
        "forecastRate": 73,
        "forecastDays": 7
      },
      {
        "goalId": "pbc_002",
        "goalType": "milestone",
        "title": "完成协作管理系统首版上线",
        "description": "对齐季度 KPI：完成项目全生命周期协同平台首版交付。",
        "progressRate": 51,
        "status": "waiting_manager_feedback",
        "boundTaskCount": 6,
        "completedTaskCount": 3
      }
    ],
    "evaluationThread": [
      {
        "type": "self",
        "content": "本周期已完成 5 个关键任务，联调与日报效率改造推进正常。",
        "createdAt": "2026-05-11T10:00:00+08:00"
      },
      {
        "type": "manager",
        "content": "方向正确，建议下周期把负载热力图和智能分配作为核心推进项。",
        "createdAt": "2026-05-11T11:00:00+08:00"
      }
    ]
  }
}
```

### API-009 获取任务创建选项

**请求方式**

- Method: `GET`
- Path: `/api/workbench/task-create-options`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "projects": [
      { "id": "project_001", "name": "纳米晶体结构优化" },
      { "id": "project_002", "name": "深度学习实验室自动化" },
      { "id": "general", "name": "通用事项" }
    ],
    "assignees": [
      { "id": "u_10001", "name": "张工", "avatar": "https://example.com/a.png" },
      { "id": "u_10002", "name": "陈思远" },
      { "id": "u_10003", "name": "王雅婷" }
    ],
    "reviewers": [
      { "id": "u_10002", "name": "陈思远" },
      { "id": "u_10003", "name": "王雅婷" }
    ],
    "pbcGoals": [
      { "id": "pbc_001", "title": "提升团队协作效率" },
      { "id": "pbc_002", "title": "完成协作管理系统首版上线" }
    ],
    "templates": [
      { "id": "log_followup", "name": "日志跟进任务", "recommended": true },
      { "id": "kanban_progress", "name": "看板推进任务" },
      { "id": "pbc_bound", "name": "PBC 绑定任务" }
    ],
    "defaultValues": {
      "status": "todo",
      "priority": "P1",
      "reminderChannels": ["in_app", "wechat_work"],
      "syncOptions": {
        "syncTodayLog": true,
        "addTomorrowPlan": true,
        "syncPersonalKanban": true,
        "bindPbcTrend": true
      }
    },
    "aiSuggestions": [
      {
        "title": "优先补齐联调收尾任务",
        "content": "如果任务和联调验证相关，建议直接设置为 P1。"
      }
    ]
  }
}
```

### API-010 保存任务草稿

**请求方式**

- Method: `POST`
- Path: `/api/tasks/drafts`
- Auth: 是

**请求参数**

请求 body 使用“5.5 新建任务字段”。

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "draftId": "task_draft_001",
    "savedAt": "2026-05-11T14:40:00+08:00"
  }
}
```

### API-011 创建任务

**请求方式**

- Method: `POST`
- Path: `/api/tasks`
- Auth: 是

**请求参数**

请求 body 使用“5.5 新建任务字段”。

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "taskId": "task_10001",
    "title": "补齐联调验证说明与样本校验结论",
    "targetPath": "/task/task_10001",
    "synced": {
      "todayLog": true,
      "personalKanban": true,
      "pbcGoal": true
    }
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 字段校验失败 | `400 TASK_VALIDATE_FAILED` | 表单字段错误 |
| 项目无权限 | `403 TASK_PROJECT_FORBIDDEN` | 提示无项目权限 |
| PBC 目标无效 | `400 PBC_GOAL_INVALID` | 提示目标无效 |
| 截止日期错误 | `400 TASK_DEADLINE_INVALID` | 日期字段错误 |
| 重复提交 | `409 TASK_DUPLICATED_SUBMIT` | 提示已创建 |

### API-012 获取 AI 工作台建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/workbench-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| context | query | string | 否 | `workbench` | 当前上下文 |
| tab | query | string | 否 | `logs` | 当前 tab |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "card": {
      "suggestionId": "sug_workbench_001",
      "title": "工作建议",
      "content": "建议先生成今日日志草稿，再处理 2 个 P0 任务。",
      "actions": [
        { "key": "generate_log_draft", "label": "立即生成" },
        { "key": "remind_later", "label": "稍后提醒" }
      ]
    },
    "items": [
      {
        "title": "看板提醒",
        "content": "设计自动化巡检告警已接近截止时间，建议今天转为待评审前补齐验证说明。"
      },
      {
        "title": "PBC 建议",
        "content": "当前有 2 个任务尚未绑定目标，自动关联后周期趋势会更完整。"
      }
    ]
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入个人工作台 | 页面加载 | `GET /api/workbench/overview`、`GET /api/notifications/unread-count` | 当前用户、query.tab | 渲染工作台 | 错误占位 |
| 切换日志/看板/PBC | tab 切换 | 可选调用对应接口 | activeTab | 渲染 tab | Toast |
| 搜索个人任务或日志 | 顶部搜索 | `GET /api/workbench/overview` 或搜索接口 | keyword | 更新结果 | Toast |
| AI 一键生成日志 | 日志按钮 | `POST /api/ai/workbench/log-draft` | date、上下文 | 填充日志草稿 | Toast |
| 保存今日日志 | 日志编辑 | `PUT /api/workbench/logs/today` | 日志表单 | Toast | 表单错误 |
| 看板筛选全部状态 | 筛选按钮 | `GET /api/workbench/kanban` | 默认筛选 | 更新看板 | Toast |
| 看板筛选 P0/P1 | 筛选按钮 | `GET /api/workbench/kanban` | priority | 更新看板 | Toast |
| 看板筛选本周截止 | 筛选按钮 | `GET /api/workbench/kanban` | dueRange=this_week | 更新看板 | Toast |
| 看板筛选仅阻塞 | 筛选按钮 | `GET /api/workbench/kanban` | blockedOnly=true | 更新看板 | Toast |
| 打开新建任务弹窗 | 侧边栏/看板按钮 | `GET /api/workbench/task-create-options` | 当前用户 | 渲染选项 | Toast |
| 保存任务草稿 | 弹窗按钮 | `POST /api/tasks/drafts` | 表单 | Toast | 表单错误 |
| 创建任务 | 弹窗按钮 | `POST /api/tasks` | 表单 | Toast，刷新看板/日志/PBC | 表单错误 |
| 自动绑定任务 | PBC AI 卡片 | `POST /api/workbench/pbc/{goalId}/bind-tasks` | goalId、taskIds | Toast，刷新 PBC | Toast |
| 打开 AI 助手 | 顶部/悬浮按钮 | `GET /api/ai/workbench-suggestions` | activeTab | 渲染建议 | Toast |
| 采纳 AI 建议 | AI 抽屉 | `POST /api/ai/workbench-suggestions/{id}/apply` | suggestionId/actionKey | Toast，刷新相关区块 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| title | input | 是 | 2-120 字 | 非空、长度合法 | 请输入任务名称 |
| projectId | select | 否 | 项目存在 | 当前用户有项目权限 | 项目无权限 |
| assigneeId | select | 是 | 用户存在 | 可分配给该用户 | 负责人无效 |
| priority | select | 是 | P0-P3 | 枚举合法 | 请选择优先级 |
| status | select | 是 | 任务状态枚举 | 初始状态合法 | 请选择状态 |
| startDate | input/date | 否 | 日期格式 | 日期合法 | 开始日期无效 |
| deadlineAt | input/date | 是 | 晚于开始日期 | 日期合法 | 截止日期无效 |
| estimateHours | input | 否 | 正数 | 数值合法 | 预计工时无效 |
| progress | input | 否 | 0-100 | 数值合法 | 进度需为 0-100 |
| riskType | select | 否 | 枚举 | 风险类型合法 | 风险标记无效 |
| description | textarea | 否 | 最长 2000 字 | 长度合法 | 任务说明过长 |
| logSection | select | 否 | 枚举 | 日志区块合法 | 日志归属无效 |
| pbcGoalId | select | 否 | 目标存在 | 当前用户 PBC 目标 | PBC 目标无效 |
| reviewerId | select | 否 | 用户存在 | 可作为评审人 | 评审人无效 |
| notifyTargetIds | input/select | 否 | 用户/角色数组 | 对象合法 | 通知对象无效 |
| tags | input | 否 | 最多 20 个 | 标签合法 | 标签无效 |

### 9.1 提交规则

- 是否允许重复提交：保存草稿、创建任务、AI 生成、AI 采纳期间不允许重复提交。
- 是否需要二次确认：创建任务并通知多人、自动绑定多个 PBC 任务、AI 批量生成子任务时建议二次确认。
- 是否需要审计日志：需要，日志保存、任务草稿、任务创建、PBC 绑定、AI 采纳都记录。
- 是否需要乐观锁或版本号：日志保存需要 `version`；任务创建不需要；草稿更新建议使用 `draftVersion`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 分组名称 | columnName | string | 否 | 项目或通用事项 |
| 任务标题 | tasks.title | string | 否 | 支持搜索 |
| 优先级 | tasks.priority | string | 是 | P0-P3 |
| 标签 | tasks.tag | string | 否 | 里程碑/PBC/阻塞 |
| 截止时间 | tasks.deadlineAt | string | 是 | 本周截止 |
| 进度 | tasks.progress | number | 是 | 0-100 |
| 阻塞状态 | tasks.isBlocked | boolean | 是 | 仅阻塞筛选 |
| PBC 目标 | tasks.pbcGoalId | string | 否 | 绑定关系 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 搜索任务、日志 |
| 优先级 | priority | string | all | P0/P1/P2/P3 |
| 截止范围 | dueRange | string | all | this_week |
| 仅阻塞 | blockedOnly | boolean | false | 只看阻塞 |
| 分组方式 | groupBy | string | project | project/status |
| 当前 tab | tab | string | logs | logs/kanban/pbc |

### 10.3 分页规则

- 个人看板任务通常数量不大，可按分组返回全量；超过 100 条时支持分页或按分组懒加载。
- 日志互动默认返回最近 10 条，支持 `page`、`pageSize` 查看全部。
- PBC 目标默认返回当前周期全部目标。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出日志 Markdown | `POST /api/workbench/logs/{logId}/export` | md / pdf | 不适用 | 异步任务 | P2 |
| 导出 PBC 自评 | `POST /api/workbench/pbc/export` | pdf / xlsx | 不适用 | 异步任务 | P2 |
| 任务附件上传 | `POST /api/tasks/{taskId}/attachments` | png/pdf/docx/xlsx/zip | 待确认 | 上传并安全扫描 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 顶部未读数、任务提醒、日志互动、PBC 反馈 |
| 邮件/企微通知 | 可选 | 通知服务 | 新建任务提醒方式中涉及企微 |
| AI 日志草稿 | 是 | AI 工作台服务 | 一键生成、仅生成草稿 |
| AI 工作建议 | 是 | AI 工作台服务 | 任务优先级、日志、PBC 建议 |
| AI PBC 趋势 | 是 | AI/PBC 服务 | 预测目标达成率 |
| 审计日志 | 是 | 审计日志服务 | 任务、日志、PBC、AI 操作 |
| WebSocket / SSE | 可选 | 工作台事件流 | 后续实时任务和日志互动 |

## 13. 缓存与实时性

- 数据是否允许缓存：个人工作台可短缓存 30-60 秒；日志编辑和任务创建后必须刷新。
- 缓存时间：看板 30 秒，PBC 目标 60 秒，AI 建议按上下文短缓存。
- 页面返回时是否刷新：建议刷新总览、个人看板、通知未读数。
- 是否需要轮询：当前不需要；日志互动可页面返回刷新。
- 是否需要 WebSocket / SSE：首期不需要；后续可用于实时评论、任务提醒和 PBC 反馈。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `WORKBENCH_PARAM_INVALID` | 查询参数错误 | Toast 或重置筛选 |
| 400 / `WORKLOG_VALIDATE_FAILED` | 日志字段错误 | 表单错误 |
| 400 / `TASK_VALIDATE_FAILED` | 任务字段错误 | 表单错误 |
| 400 / `TASK_DEADLINE_INVALID` | 截止日期错误 | 日期字段错误 |
| 400 / `PBC_GOAL_INVALID` | PBC 目标无效 | 表单错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `WORKBENCH_FORBIDDEN` | 无工作台权限 | 无权限提示 |
| 403 / `TASK_CREATE_FORBIDDEN` | 无任务创建权限 | 隐藏按钮或 Toast |
| 403 / `TASK_PROJECT_FORBIDDEN` | 无项目任务权限 | 表单错误 |
| 404 / `WORKLOG_NOT_FOUND` | 日志不存在 | 创建空日志 |
| 409 / `WORKLOG_VERSION_CONFLICT` | 日志版本冲突 | 提示刷新 |
| 409 / `TASK_DUPLICATED_SUBMIT` | 重复创建任务 | 提示已创建 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 进入 `/workbench` 后，日志、看板、PBC、今日焦点和 AI 卡片由接口返回，不再使用静态数据。
- URL query `?tab=logs|kanban|pbc` 可正确定位 tab，并加载对应数据。
- 日志保存、AI 日志草稿生成、最近日志互动均有接口支撑。
- 个人看板支持优先级、本周截止、仅阻塞、关键词筛选。
- 新建任务弹窗的项目、负责人、评审人、PBC 目标、模板、默认值、AI 建议由后端返回。
- 保存草稿和创建任务可以提交完整字段，并同步到日志、个人看板和 PBC。
- PBC 目标、周期评估对话、AI 趋势提示由接口返回，自动绑定任务可调用接口。
- AI 助手可返回工作建议、看板提醒、PBC 建议，并支持采纳动作。
- 无权限、空数据、参数错误、日期错误、PBC 目标无效、AI 限流等状态有明确错误码。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 个人看板当前按项目/通用事项分组，是否后续改为按任务状态列分组？ | 产品/前端/后端 | 待确认 |
| Q2 | 今日日志是每天一条固定记录，还是可多条日志？ | 产品/后端 | 待确认 |
| Q3 | 新建任务时“同步到今日日志”“加入明日计划”“绑定 PBC 趋势”等开关具体执行哪些写操作？ | 产品/后端 | 待确认 |
| Q4 | PBC 达成率按任务数量、任务权重、工时还是人工评分计算？ | 产品/数据/后端 | 待确认 |
| Q5 | AI 一键生成日志草稿是否自动写入，还是只返回预览由用户确认？ | 产品/AI/前端 | 待确认 |
| Q6 | 新建任务的负责人是否允许选择非本人？普通成员是否可给他人创建任务？ | 产品/权限/后端 | 待确认 |
| Q7 | 任务草稿是否需要草稿列表和继续编辑入口？ | 产品/前端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`src/views/Workbench.vue` 的日志模板静态内容、`kanbanData`、PBC 卡片静态内容、AI 文案、新建任务弹窗静态 value。
- 当前顶部通知角标静态为 `5`。
- 当前顶部搜索框未绑定响应式状态和接口。
- 当前看板筛选为前端本地 computed：`filteredKanbanData`。
- 当前“AI 一键生成”“一键填充”“仅生成草稿”“自动绑定任务”“查看趋势图”“立即生成”“稍后提醒”均未接接口。
- 当前新建任务弹窗字段没有响应式表单对象，保存草稿和创建任务只调用 `showToast`。
- 当前任务卡片未绑定点击进入 `/task/:id`。
- 需要后端优先确认的字段：个人看板分组方式、PBC 目标口径、任务创建同步开关、日志结构。
- 需要后端优先确认的接口：`GET /api/workbench/overview`、`GET /api/workbench/kanban`、`GET /api/workbench/task-create-options`、`POST /api/tasks`。
