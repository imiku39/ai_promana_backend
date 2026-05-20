# 任务详情后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/TaskDetail.vue`  
> 页面定位：单个任务详情页，覆盖任务基础信息、状态流转、子任务、评论和 AI 建议。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 任务详情 |
| 前端路由 | `/task/:id` |
| 前端文件 | `src/views/TaskDetail.vue` |
| 所属模块 | 任务管理 / 任务详情 / 协作评论 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示单个任务的标题、状态、优先级、负责人、截止日期、所属项目和描述。
- 支持任务编辑、删除、状态流转。
- 展示和管理子任务，可勾选子任务完成状态、添加子任务。
- 展示任务评论列表，支持新增评论。
- 展示 AI 助手的任务拆解建议和排期建议。

### 2.2 对接范围

- 任务详情查询。
- 任务编辑、删除、状态流转。
- 子任务列表、创建子任务、更新子任务完成状态。
- 评论列表、新增评论、删除评论。
- AI 任务拆解建议、排期建议、采纳 AI 建议。
- 权限、审计日志、通知。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Workbench.vue` | 个人工作台任务看板可进入任务详情 |
| `ProjectKanban.vue` | 项目看板任务卡片可进入任务详情 |
| `ProjectDetail.vue` | 项目概览本周任务可进入任务详情 |
| `Notifications.vue` | 任务状态变更、评论、@提醒 |
| `Settings.vue` | 通知偏好影响任务通知 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 否 | 全量任务权限 |
| 管理员 | 是 | 是 | 是 | 视权限 | 否 | 组织范围 |
| 项目负责人 | 是 | 是 | 是 | 是 | 否 | 可管理项目任务 |
| 任务负责人 | 是 | 是 | 是 | 否 | 否 | 可更新本人任务 |
| 项目成员 | 是 | 是 | 视权限 | 否 | 否 | 可评论和更新授权任务 |
| 协作者 | 视权限 | 否 | 视权限 | 否 | 否 | 只读或有限协作 |

### 3.1 权限规则

- 页面入口权限：访问 `/task/:id` 需要登录态和 `task:read`，且当前用户对该任务有可见权限。
- 按钮级权限：
  - “编辑”需要 `task:update`。
  - “删除”需要 `task:delete`。
  - 状态流转需要 `task:transition`。
  - 添加/更新子任务需要 `task:subtask:update`。
  - 评论需要 `task:comment:create`。
  - AI 建议采纳需要 `ai:task-suggestion:apply` 和对应任务写权限。
- 数据范围权限：只返回当前用户参与项目、负责项目或被授权任务。
- 敏感字段脱敏规则：无权限不返回内部备注、成本、客户敏感信息、审计追踪原始数据。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 任务详情 | 页面主体 | 是 | `GET /api/tasks/{taskId}` | 当前为 `task` mock |
| 状态流转选项 | 状态按钮 | 是 | `GET /api/tasks/{taskId}/transition-options` | 当前静态 `statuses` |
| 子任务列表 | 子任务区块 | 是 | 可随详情返回或 `GET /api/tasks/{taskId}/subtasks` | 当前随 mock |
| 评论列表 | 评论区块 | 是 | `GET /api/tasks/{taskId}/comments` | 可分页 |
| AI 建议 | AI 助手卡片 | 否 | `GET /api/ai/task-suggestions` | 当前静态 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 任务加载中 | 请求处理中 | 当前未接 |
| empty | 任务不存在 | 数据不存在或无权限 | 返回上级 |
| error | Toast / 错误占位 | 接口异常 | 标准错误结构 |
| saving | 编辑/状态更新中 | 写请求处理中 | 禁用按钮 |
| deleted | 删除后跳转 | 任务已删除 | 返回列表 |
| aiLoading | AI 建议加载中 | AI 请求处理中 | P1 |

## 5. 字段模型

### 5.1 任务主对象字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 路由参数/任务 ID | `task_001` | 任务唯一 ID |
| title | string | 是 | 标题 | `完成登录页面开发` | 任务标题 |
| status | string | 是 | 状态标签/按钮 | `in_progress` | 任务状态 |
| statusLabel | string | 否 | 状态展示 | `进行中` | 可后端返回 |
| priority | string | 是 | 优先级标签 | `high` | 优先级 |
| priorityLabel | string | 否 | 优先级展示 | `高` | 可后端返回 |
| assignee.id | string | 是 | 负责人 | `u_10001` | 负责人 ID |
| assignee.name | string | 是 | 负责人 | `张三` | 展示 |
| assignee.avatar | string | 否 | 头像 | `https://...` | 头像 |
| assignee.avatarColor | string | 否 | 头像底色 | `#409eff` | 当前前端使用颜色 |
| deadline | string | 是 | 截止日期 | `2026-04-26` | 日期 |
| project.id | string | 是 | 项目 | `project_001` | 项目 ID |
| project.name | string | 是 | 项目 | `AI项目管理系统` | 项目名称 |
| description | string | 否 | 描述 | `开发系统登录页面...` | 任务描述 |
| progress | number | 否 | 可选 | `60` | 0-100 |
| createdBy.id | string | 否 | 审计 | `u_10002` | 创建人 |
| createdAt | string | 否 | 审计 | `2026-04-24T09:00:00+08:00` | 创建时间 |
| updatedAt | string | 否 | 审计 | `2026-04-24T10:30:00+08:00` | 更新时间 |
| permissions | string[] | 是 | 按钮控制 | `["task:update"]` | 当前用户权限 |
| version | number | 是 | 更新/流转 | `3` | 乐观锁 |

### 5.2 子任务字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 子任务 key | `subtask_001` | 子任务 ID |
| title | string | 是 | 子任务标题 | `实现账号密码登录表单` | 标题 |
| completed | boolean | 是 | checkbox | `true` | 是否完成 |
| assigneeId | string | 否 | 后续扩展 | `u_10001` | 子任务负责人 |
| sortOrder | number | 否 | 排序 | `1000` | 子任务顺序 |
| completedAt | string | 否 | 审计 | `2026-04-24T10:00:00+08:00` | 完成时间 |
| version | number | 是 | 更新 | `1` | 乐观锁 |

### 5.3 评论字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 评论 key | `comment_001` | 评论 ID |
| author.id | string | 是 | 评论作者 | `u_10002` | 用户 ID |
| author.name | string | 是 | 评论作者 | `李四` | 展示 |
| author.avatar | string | 否 | 头像 | `https://...` | 头像 |
| author.avatarColor | string | 否 | 头像底色 | `#67c23a` | 当前前端使用 |
| content | string | 是 | 评论内容 | `登录页面需要支持记住密码功能` | 文本 |
| createdAt | string | 是 | 评论时间 | `2026-04-24 10:00` | 时间 |
| mentionedUserIds | string[] | 否 | 通知 | `["u_10001"]` | @ 用户 |
| permissions | string[] | 否 | 行操作 | `["delete"]` | 当前用户权限 |

### 5.4 AI 建议字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| suggestionId | string | 是 | AI 卡片 | `sug_task_001` | 建议 ID |
| breakdown | string | 是 | 任务拆解建议 | `建议将任务拆分为...` | 拆解内容 |
| scheduling | string | 是 | 排期建议 | `设计 UI 1 天...` | 排期内容 |
| confidence | number | 否 | 可选 | `0.88` | 置信度 |
| actions | array | 否 | 后续按钮 | `[]` | 生成子任务、更新排期 |

### 5.5 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| taskStatus | `todo` | 待开始 | neutral | 未开始 |
| taskStatus | `in_progress` | 进行中 | success / primary | 当前 mock 状态 |
| taskStatus | `review` | 待评审 | warning | 待评审 |
| taskStatus | `done` | 已完成 | success | 完成 |
| taskStatus | `blocked` | 已阻塞 | danger | 阻塞 |
| priority | `low` | 低 | neutral | 低优先级 |
| priority | `medium` | 中 | primary | 中优先级 |
| priority | `high` | 高 | danger | 当前 mock 状态 |
| priority | `urgent` | 紧急 | danger | 最高优先级 |

### 5.6 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| subtaskTotal | number | 子任务总数 | 子任务区块 | 可后端返回 |
| completedSubtaskCount | number | completed=true 的子任务数 | 子任务区块 | 可用于进度 |
| commentCount | number | 评论总数 | 评论区块 | 可分页 |
| progress | number | 完成子任务数 / 总子任务数或手动进度 | 任务详情 | 口径需确认 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取任务详情 | GET | `/api/tasks/{taskId}` | 首屏详情 | P0 |
| API-002 | 更新任务 | PUT | `/api/tasks/{taskId}` | 编辑任务 | P0 |
| API-003 | 删除任务 | DELETE | `/api/tasks/{taskId}` | 删除任务 | P0 |
| API-004 | 获取状态流转选项 | GET | `/api/tasks/{taskId}/transition-options` | 状态按钮 | P0 |
| API-005 | 任务状态流转 | POST | `/api/tasks/{taskId}/transition` | 更新状态 | P0 |
| API-006 | 创建子任务 | POST | `/api/tasks/{taskId}/subtasks` | 添加子任务 | P0 |
| API-007 | 更新子任务 | PATCH | `/api/tasks/{taskId}/subtasks/{subtaskId}` | 勾选完成 | P0 |
| API-008 | 删除子任务 | DELETE | `/api/tasks/{taskId}/subtasks/{subtaskId}` | 删除子任务 | P1 |
| API-009 | 获取评论列表 | GET | `/api/tasks/{taskId}/comments` | 评论列表 | P0 |
| API-010 | 新增评论 | POST | `/api/tasks/{taskId}/comments` | 发送评论 | P0 |
| API-011 | 删除评论 | DELETE | `/api/tasks/{taskId}/comments/{commentId}` | 删除评论 | P1 |
| API-012 | 获取 AI 任务建议 | GET | `/api/ai/task-suggestions` | 拆解/排期建议 | P1 |
| API-013 | 采纳 AI 任务建议 | POST | `/api/ai/task-suggestions/{suggestionId}/apply` | 生成子任务/更新排期 | P1 |

## 7. 接口详情

### API-001 获取任务详情

**请求方式**

- Method: `GET`
- Path: `/api/tasks/{taskId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| taskId | path | string | 是 | `task_001` | 任务 ID |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "task_001",
    "title": "完成登录页面开发",
    "status": "in_progress",
    "statusLabel": "进行中",
    "priority": "high",
    "priorityLabel": "高",
    "assignee": {
      "id": "u_10001",
      "name": "张三",
      "avatar": "https://example.com/avatar.png",
      "avatarColor": "#409eff"
    },
    "deadline": "2026-04-26",
    "project": {
      "id": "project_001",
      "name": "AI项目管理系统"
    },
    "description": "开发系统登录页面，包括账号密码登录、第三方登录、注册入口和忘记密码功能。",
    "subtasks": [
      {
        "id": "subtask_001",
        "title": "实现账号密码登录表单",
        "completed": true,
        "sortOrder": 1000,
        "version": 1
      }
    ],
    "summary": {
      "subtaskTotal": 5,
      "completedSubtaskCount": 2,
      "commentCount": 2,
      "progress": 40
    },
    "permissions": ["task:update", "task:delete", "task:transition", "task:comment:create"],
    "version": 3
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 任务不存在 | `404 TASK_NOT_FOUND` | 展示不存在或返回上级 |
| 无权限 | `403 TASK_FORBIDDEN` | 展示无权限 |
| 未登录 | `401 AUTH_TOKEN_EXPIRED` | 跳转登录 |

### API-002 更新任务

**请求方式**

- Method: `PUT`
- Path: `/api/tasks/{taskId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| title | body | string | 是 | `完成登录页面开发` | 标题 |
| priority | body | string | 是 | `high` | 优先级 |
| assigneeId | body | string | 是 | `u_10001` | 负责人 |
| deadline | body | string | 是 | `2026-04-26` | 截止日期 |
| description | body | string | 否 | `开发系统登录页面...` | 描述 |
| version | body | number | 是 | `3` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "taskId": "task_001",
    "version": 4,
    "updatedAt": "2026-05-11T14:00:00+08:00"
  }
}
```

### API-005 任务状态流转

**请求方式**

- Method: `POST`
- Path: `/api/tasks/{taskId}/transition`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| fromStatus | body | string | 是 | `in_progress` | 原状态 |
| toStatus | body | string | 是 | `review` | 目标状态 |
| blockedReason | body | 条件必填 | `等待第三方登录配置` | 转为 blocked 时必填 |
| comment | body | string | 否 | `提交评审` | 流转备注 |
| version | body | number | 是 | `3` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "taskId": "task_001",
    "status": "review",
    "statusLabel": "待评审",
    "version": 4,
    "notifiedUsers": ["u_10001", "u_10002"]
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 流转不合法 | `400 TASK_TRANSITION_DENIED` | 状态回滚并 Toast |
| 阻塞原因缺失 | `400 TASK_BLOCK_REASON_REQUIRED` | 提示填写原因 |
| 版本冲突 | `409 TASK_VERSION_CONFLICT` | 提示刷新 |

### API-006 创建子任务

**请求方式**

- Method: `POST`
- Path: `/api/tasks/{taskId}/subtasks`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| title | body | string | 是 | `添加忘记密码功能` | 子任务标题 |
| assigneeId | body | string | 否 | `u_10001` | 负责人 |
| sortOrder | body | number | 否 | `6000` | 排序 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "subtask_006",
    "title": "添加忘记密码功能",
    "completed": false,
    "sortOrder": 6000,
    "version": 1
  }
}
```

### API-007 更新子任务

**请求方式**

- Method: `PATCH`
- Path: `/api/tasks/{taskId}/subtasks/{subtaskId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| title | body | string | 否 | `实现账号密码登录表单` | 修改标题 |
| completed | body | boolean | 否 | `true` | 完成状态 |
| version | body | number | 是 | `1` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "subtask_001",
    "completed": true,
    "completedAt": "2026-05-11T14:05:00+08:00",
    "taskProgress": 40,
    "version": 2
  }
}
```

### API-009 获取评论列表

**请求方式**

- Method: `GET`
- Path: `/api/tasks/{taskId}/comments`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
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
        "id": "comment_001",
        "author": {
          "id": "u_10002",
          "name": "李四",
          "avatarColor": "#67c23a"
        },
        "content": "登录页面需要支持记住密码功能",
        "createdAt": "2026-04-24 10:00",
        "permissions": []
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 2
    }
  }
}
```

### API-010 新增评论

**请求方式**

- Method: `POST`
- Path: `/api/tasks/{taskId}/comments`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| content | body | string | 是 | `好的，我会添加记住密码功能` | 评论内容 |
| mentionedUserIds | body | string[] | 否 | `["u_10001"]` | @ 用户 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "comment_003",
    "author": {
      "id": "u_10001",
      "name": "张三",
      "avatarColor": "#409eff"
    },
    "content": "好的，我会添加记住密码功能",
    "createdAt": "2026-05-11 14:10",
    "permissions": ["delete"]
  }
}
```

### API-012 获取 AI 任务建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/task-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| taskId | query | string | 是 | `task_001` | 任务 ID |
| context | query | string | 否 | `task_detail` | 上下文 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "suggestionId": "sug_task_001",
    "breakdown": "建议将任务拆分为：1. 设计登录页面 UI；2. 实现表单验证；3. 集成第三方登录；4. 测试登录功能。",
    "scheduling": "建议排期：设计 UI 1 天 + 实现表单 1 天 + 集成第三方登录 1 天 + 测试 0.5 天，总计 3.5 天。",
    "confidence": 0.88,
    "actions": [
      { "key": "create_subtasks", "label": "生成子任务" },
      { "key": "update_schedule", "label": "更新排期" }
    ]
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入任务详情 | 页面加载 | `GET /api/tasks/{taskId}`、`GET /api/tasks/{taskId}/comments` | route.params.id | 渲染任务和评论 | 错误占位 |
| 点击编辑 | 头部按钮 | `PUT /api/tasks/{taskId}` | 编辑表单 | Toast，刷新详情 | 表单错误 |
| 点击删除 | 头部按钮 | `DELETE /api/tasks/{taskId}` | taskId | Toast，返回上级 | Toast |
| 点击状态按钮 | 状态区 | `POST /api/tasks/{taskId}/transition` | toStatus、version | 更新状态 | 回滚 Toast |
| 勾选子任务 | 子任务 checkbox | `PATCH /subtasks/{subtaskId}` | completed、version | 更新子任务和进度 | 回滚 Toast |
| 添加子任务 | 添加按钮 | `POST /subtasks` | title | 新增子任务 | 表单错误 |
| 输入评论 | 评论输入框 | 无 | newComment | 本地输入 | 前端校验 |
| 点击发送 | 评论按钮 | `POST /comments` | content | 追加评论 | 表单错误 |
| 加载 AI 建议 | 页面加载/按钮 | `GET /api/ai/task-suggestions` | taskId | 渲染建议 | Toast |
| 采纳 AI 建议 | AI 卡片 | `POST /api/ai/task-suggestions/{id}/apply` | suggestionId/actionKey | 生成子任务/更新排期 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| title | input | 是 | 2-120 字 | 非空、长度合法 | 请输入任务标题 |
| status | button/select | 是 | 枚举 | 流转合法 | 状态流转不合法 |
| priority | select | 是 | 枚举 | 合法值 | 请选择优先级 |
| assigneeId | selector | 是 | 用户存在 | 项目成员或授权用户 | 负责人无效 |
| deadline | date | 是 | 日期格式 | 日期合法 | 截止日期无效 |
| description | textarea | 否 | 最长 2000 字 | 长度合法 | 描述过长 |
| subtask.title | input | 是 | 1-120 字 | 非空 | 请输入子任务标题 |
| subtask.completed | checkbox | 是 | boolean | 布尔值 | 无 |
| comment.content | input | 是 | 1-1000 字 | 非空、内容安全 | 请输入评论内容 |
| blockedReason | textarea | 条件必填 | 转 blocked 时必填 | 非空、长度合法 | 请填写阻塞原因 |

### 9.1 提交规则

- 是否允许重复提交：编辑、删除、状态流转、子任务更新、评论发送、AI 采纳请求期间不允许重复提交。
- 是否需要二次确认：删除任务、删除评论、采纳会批量生成子任务的 AI 建议需要二次确认。
- 是否需要审计日志：需要，任务编辑、删除、状态流转、子任务变更、评论、AI 采纳都记录。
- 是否需要乐观锁或版本号：需要，任务和子任务更新使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 子任务标题 | subtasks.title | string | 否 | 按 sortOrder |
| 子任务状态 | subtasks.completed | boolean | 是 | 已完成/未完成 |
| 评论作者 | comments.author.name | string | 否 | 评论列表 |
| 评论时间 | comments.createdAt | string | 是 | 默认倒序或正序待确认 |
| 评论内容 | comments.content | string | 否 | 支持内容安全过滤 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 评论页码 | page | number | 1 | 评论分页 |
| 评论页大小 | pageSize | number | 20 | 评论分页 |
| 评论排序 | sortOrder | string | asc | asc / desc |

### 10.3 分页规则

- 子任务列表不分页，按 `sortOrder` 返回全部。
- 评论默认页大小 20，最大页大小 100。
- 评论排序需确认：当前 UI 更适合按创建时间正序展示。

## 11. 文件、导入、导出

当前任务详情页无附件上传 UI，但任务详情业务后续可扩展附件能力。

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 上传任务附件 | `POST /api/tasks/{taskId}/attachments` | png/jpg/pdf/docx/xlsx/zip | 待确认 | 上传并安全扫描 | P2 |
| 下载任务附件 | `GET /api/tasks/{taskId}/attachments/{fileId}/download` | 原文件 | 不适用 | 鉴权临时链接 | P2 |
| 导出任务详情 | `POST /api/tasks/{taskId}/export` | pdf / markdown | 不适用 | 异步任务 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 状态变更、评论、@、负责人变更 |
| 邮件/企微通知 | 可选 | 通知服务 | 受用户通知偏好控制 |
| AI 任务拆解 | 是 | AI 任务服务 | 拆解建议、生成子任务 |
| AI 排期建议 | 是 | AI 任务服务 | 估算工期、更新排期 |
| 审计日志 | 是 | 审计日志服务 | 任务写操作 |
| WebSocket / SSE | 可选 | 任务事件流 | 多人协作实时评论/状态 |

## 13. 缓存与实时性

- 数据是否允许缓存：任务详情可短缓存 30 秒，写操作后立即刷新。
- 缓存时间：AI 建议可按任务版本缓存。
- 页面返回时是否刷新：建议刷新任务详情和评论。
- 是否需要轮询：当前不需要。
- 是否需要 WebSocket / SSE：首期可不接；后续多人协作评论可接 WebSocket/SSE。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `TASK_VALIDATE_FAILED` | 任务字段错误 | 表单错误 |
| 400 / `TASK_TRANSITION_DENIED` | 状态流转不合法 | 回滚并 Toast |
| 400 / `TASK_BLOCK_REASON_REQUIRED` | 阻塞原因缺失 | 提示填写原因 |
| 400 / `COMMENT_CONTENT_INVALID` | 评论内容无效 | 评论字段错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `TASK_FORBIDDEN` | 无任务查看权限 | 无权限提示 |
| 403 / `TASK_UPDATE_FORBIDDEN` | 无编辑权限 | Toast |
| 404 / `TASK_NOT_FOUND` | 任务不存在 | 返回上级 |
| 404 / `SUBTASK_NOT_FOUND` | 子任务不存在 | 刷新子任务 |
| 409 / `TASK_VERSION_CONFLICT` | 任务版本冲突 | 提示刷新 |
| 409 / `SUBTASK_VERSION_CONFLICT` | 子任务版本冲突 | 刷新子任务 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 进入 `/task/:id` 后，任务基础信息、子任务、评论和权限由接口返回，不再使用前端静态 mock。
- 状态按钮由后端返回可流转状态，点击状态后调用流转接口并处理非法流转。
- 勾选子任务会调用接口更新完成状态，并返回任务进度。
- 新增评论会调用接口并追加到评论列表。
- 编辑、删除任务有接口支撑、权限控制和二次确认。
- AI 助手建议由接口返回，支持拆解建议和排期建议。
- 无权限、任务不存在、版本冲突、评论内容违规等异常有明确错误码。
- 所有任务写操作写入审计日志，并按通知偏好通知相关人员。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 任务详情页是否需要统一改为当前主应用玻璃拟态布局？ | 产品/前端 | 待确认 |
| Q2 | 任务状态枚举是否与项目看板完全共用？ | 产品/后端 | 待确认 |
| Q3 | 任务进度由子任务完成率自动计算，还是允许手动维护？ | 产品/后端 | 待确认 |
| Q4 | 删除任务是硬删除、软删除还是归档？ | 产品/后端 | 待确认 |
| Q5 | 评论是否支持 @、附件、富文本和表情？ | 产品/前后端 | 待确认 |
| Q6 | AI 建议采纳后是生成子任务、更新排期，还是只写入建议记录？ | 产品/AI/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`src/views/TaskDetail.vue` 的 `task`、`statuses`、`aiSuggestions`。
- 当前状态按钮没有点击事件，不会调用接口或更新状态。
- 当前子任务 checkbox 只修改本地 `subtask.completed`。
- 当前“编辑”“删除”“添加子任务”“发送评论”按钮没有绑定真实处理函数。
- 当前评论输入 `newComment` 未提交接口。
- 当前 AI 助手为固定浮层，建议后续接 `GET /api/ai/task-suggestions`。
- 需要后端优先确认的字段：任务状态枚举、优先级枚举、任务进度口径、删除策略。
- 需要后端优先确认的接口：`GET /api/tasks/{taskId}`、`POST /api/tasks/{taskId}/transition`、子任务接口、评论接口。
