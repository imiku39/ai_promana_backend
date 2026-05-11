# 通知中心后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Notifications.vue`

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 通知中心 |
| 前端路由 | `/notifications` |
| 前端文件 | `src/views/Notifications.vue` |
| 所属模块 | 通知中心 / 消息提醒 / AI 处理建议 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 统一承接全站标题栏通知入口，替代临时通知弹窗。
- 支持用户查看待处理事项、系统变更、AI 提醒、协作反馈等通知。
- 支持按分类筛选、关键词搜索通知。
- 支持展示未读通知数、高优先级通知数、今日已处理通知数。
- 支持通过通知动作跳转到角色管理、审计日志、系统配置、全局工作台、个人工作台等关联页面。
- 支持查看通知处理建议、通知入口说明。
- 支持 AI 助手给出通知处理建议，并预留采纳建议能力。

### 2.2 对接范围

- 通知中心列表查询接口。
- 通知统计指标接口。
- 通知分类统计接口。
- 通知搜索与筛选接口。
- 通知已读、批量已读、处理状态更新接口。
- 通知动作跳转所需的业务目标信息。
- 通知偏好设置入口所需接口。
- 通知通道配置入口所需接口。
- AI 通知处理建议获取与采纳接口。
- 当前登录用户信息与通知未读数。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Dashboard.vue` | 顶部通知按钮跳转通知中心；AI 晨报通知可回到工作台 |
| `Workbench.vue` | 协作反馈、日志评论、个人待办类通知跳转个人工作台 |
| `Settings.vue` | 通知偏好设置入口 |
| `admin/AdminRoles.vue` | 角色模板变更申请类通知跳转目标 |
| `admin/AdminLogs.vue` | 审计风险通知跳转目标 |
| `admin/AdminSystem.vue` | 通知通道配置、系统配置更新跳转目标 |
| `UserProfileHoverCard.vue` | 当前用户信息展示 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 否 | 可处理 | 可删除/归档 | 视权限 | 可查看全量后台通知 |
| 管理员 | 是 | 否 | 可处理 | 视权限 | 视权限 | 可查看管理范围内通知 |
| 项目负责人 | 是 | 否 | 可处理本人相关 | 否 | 否 | 可处理项目角色、项目风险类通知 |
| 研发 / QA / 产品 | 是 | 否 | 可处理本人相关 | 否 | 否 | 查看本人待办和协作通知 |
| 协作者 | 是 | 否 | 可处理本人相关 | 否 | 否 | 仅查看授权项目通知 |

### 3.1 权限规则

- 页面入口权限：访问 `/notifications` 需要有效登录态。
- 按钮级权限：
  - “通知偏好”需要 `notification:preference:update` 或允许用户维护本人偏好。
  - “通道配置”需要 `admin:system:update` 或 `notification:channel:manage`。
  - 高风险权限审计通知跳转审计日志需要 `audit-log:read`。
  - 角色模板变更申请跳转角色管理需要 `role:read`，处理申请需要 `role:update`。
  - AI 建议采纳需要 `ai:notification-suggestion:apply`。
- 数据范围权限：
  - 普通用户仅能查看发送给自己的通知和本人可见项目范围内通知。
  - 管理员可查看管理范围内的系统通知、权限通知、通道配置通知。
  - 超级管理员可查看全租户或全系统通知。
- 敏感字段脱敏规则：通知正文不得暴露密码、密钥、token、完整手机号、完整邮箱等敏感信息；审计类通知仅返回前端可展示摘要，详情在审计日志页按权限查看。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 也可由全局状态提供 |
| 通知统计 | 顶部三张指标卡 | 是 | `GET /api/notifications/summary` | 未读、高优先级、今日已处理 |
| 通知分类统计 | 筛选按钮数量 | 是 | `GET /api/notifications/categories` 或列表接口聚合返回 | 全部、待处理、系统更新、AI 提醒 |
| 通知列表 | 最新通知流 | 是 | `GET /api/notifications` | 支持分类、关键词、分页 |
| 处理建议 | 右侧处理建议卡 | 否 | `GET /api/notifications/process-advice` | 可静态配置或后端返回 |
| 入口说明 | 右侧入口说明卡 | 否 | `GET /api/notifications/entry-guide` | 可静态配置或后端返回 |
| AI 助手建议 | AI 抽屉内容 | 否 | `GET /api/ai/notification-suggestions` | 打开抽屉时加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 列表加载中 / 局部骨架 | 请求处理中 | 当前页面暂未接 loading |
| empty | 暂无符合条件的通知 | 当前筛选无数据 | 前端已有空状态 |
| error | Toast 或错误占位 | 接口异常或无权限 | 后续接入时补充 |
| unread | 红点提示 | 通知未读 | `unread=true` |
| read | 无红点 | 通知已读 | `unread=false` |
| pending | 待处理 | 需要用户处理 | 筛选分类 |
| processed | 已处理 | 通知动作已完成 | 可用于统计 |

## 5. 字段模型

### 5.1 通知统计字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| unreadCount | number | 是 | 未读通知卡、顶部角标 | `5` | 当前未读数 |
| highPriorityCount | number | 是 | 高优先级卡 | `2` | 高优先级或 P0/P1 通知数 |
| processedTodayCount | number | 是 | 今日已处理卡 | `8` | 今日已处理通知数 |
| generatedAt | string | 否 | 不直接展示 | `2026-05-11T10:00:00+08:00` | 统计生成时间 |

### 5.2 通知列表字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 通知 key | `notice-role-change` | 唯一标识 |
| category | string | 是 | 分类筛选 | `pending` | `pending` / `system` / `ai` |
| type | string | 是 | 业务类型 | `role_change_request` | 用于图标、跳转和处理逻辑 |
| icon | string | 否 | 图标 | `warning` | Material Symbols 名称，可前端按 type 映射 |
| iconTheme | string | 否 | 图标背景语义 | `warning` | 避免后端直接下发 CSS |
| status | string | 是 | 状态 pill 文案 | `待处理` | 中文展示 |
| statusCode | string | 是 | 状态枚举 | `pending` | 机器可读状态 |
| priority | string | 是 | 优先级 | `P1` | P0-P3 |
| title | string | 是 | 通知标题 | `角色模板变更申请` | 标题 |
| description | string | 是 | 通知说明 | `用户张三申请将项目角色...` | 摘要 |
| unread | boolean | 是 | 未读红点 | `true` | 是否未读 |
| createdAt | string | 是 | 时间展示 | `2026-05-11T09:50:00+08:00` | 前端转相对时间 |
| sourceName | string | 否 | 搜索匹配 | `后台管理` | 来源模块 |
| tags | array | 否 | 标签列表 | `[]` | 通知标签 |
| actionLabel | string | 是 | 操作按钮 | `查看角色管理` | 按钮文案 |
| actionType | string | 是 | 动作类型 | `navigate` | navigate / mark_read / approve 等 |
| actionPath | string | 否 | 跳转路径 | `/admin/roles` | 前端路由 |
| targetId | string | 否 | 业务对象 ID | `role_req_001` | 后端处理动作需要 |
| handled | boolean | 否 | 处理状态 | `false` | 是否已处理 |
| handledAt | string | 否 | 处理时间 | `null` | 处理时间 |

### 5.3 通知标签字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| label | string | 是 | micro-tag 文案 | `后台管理` | 标签文案 |
| type | string | 否 | 标签样式 | `p1` | p0 / p1 / p2 / neutral / success / warning |
| colorSemantic | string | 否 | 颜色语义 | `warning` | 前端按语义映射样式 |

### 5.4 处理建议字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| title | string | 是 | 右侧处理建议标题 | `先处理权限和角色类通知` | 建议标题 |
| description | string | 是 | 右侧处理建议说明 | `这两类通知会直接影响...` | 建议说明 |
| priority | number | 否 | 排序 | `1` | 从小到大排序 |

### 5.5 AI 建议字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| primarySuggestion.id | string | 是 | AI 主建议 | `sug_notice_001` | 建议 ID |
| primarySuggestion.title | string | 是 | AI 卡片标题 | `通知处理建议` | 标题 |
| primarySuggestion.content | string | 是 | AI 卡片正文 | `建议先完成高优先级权限审计...` | 正文 |
| primarySuggestion.actions | array | 否 | AI 按钮 | `[{key:"accept"}]` | 采纳 / 稍后 |
| items | array | 否 | AI 列表项 | `[]` | 扩展说明 |

### 5.6 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| category | `all` | 全部 | neutral | 前端筛选项 |
| category | `pending` | 待处理 | warning | 待用户处理 |
| category | `system` | 系统更新 | success | 系统配置或通道变更 |
| category | `ai` | AI 提醒 | ai | AI 晨报、摘要、建议 |
| priority | `P0` | 最高优先级 | danger | 高风险立即处理 |
| priority | `P1` | 高优先级 | warning | 今日内处理 |
| priority | `P2` | 中优先级 | primary | 正常处理 |
| priority | `P3` | 低优先级 | neutral | 可延后 |
| statusCode | `pending` | 待处理 | warning | 待处理 |
| statusCode | `high_priority` | 高优先级 | danger | 高优先级 |
| statusCode | `completed` | 已完成 | success | 已完成 |
| statusCode | `ai_reminder` | AI 提醒 | ai | AI 类提醒 |
| statusCode | `collaboration_feedback` | 协作反馈 | neutral | 评论/反馈类 |

### 5.7 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| unreadCount | number | 当前用户未读通知总数 | 顶部角标、指标卡 | 当前静态为 5 |
| highPriorityCount | number | priority in P0/P1 且未处理 | 高优先级卡 | 当前静态为 2 |
| processedTodayCount | number | 当天已处理通知数 | 今日已处理卡 | 当前静态为 8 |
| categoryCount.pending | number | category=pending 的通知数 | 筛选按钮 | 受权限范围影响 |
| categoryCount.system | number | category=system 的通知数 | 筛选按钮 | 受权限范围影响 |
| categoryCount.ai | number | category=ai 的通知数 | 筛选按钮 | 受权限范围影响 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取通知统计 | GET | `/api/notifications/summary` | 指标卡和顶部角标 | P0 |
| API-002 | 获取通知列表 | GET | `/api/notifications` | 通知流、搜索、筛选 | P0 |
| API-003 | 获取通知详情 | GET | `/api/notifications/{notificationId}` | 查看详情或处理前确认 | P1 |
| API-004 | 标记通知已读 | POST | `/api/notifications/{notificationId}/read` | 单条已读 | P0 |
| API-005 | 批量标记已读 | POST | `/api/notifications/read-batch` | 批量已读 / 全部已读 | P1 |
| API-006 | 更新通知处理状态 | POST | `/api/notifications/{notificationId}/handle` | 处理通知 | P0 |
| API-007 | 获取通知处理建议 | GET | `/api/notifications/process-advice` | 右侧处理建议 | P1 |
| API-008 | 获取通知偏好 | GET | `/api/notification-preferences/me` | 设置页通知偏好 | P1 |
| API-009 | 更新通知偏好 | PUT | `/api/notification-preferences/me` | 设置页保存偏好 | P1 |
| API-010 | 获取通知通道配置 | GET | `/api/admin/notification-channels` | 后台通道配置 | P1 |
| API-011 | 获取 AI 通知建议 | GET | `/api/ai/notification-suggestions` | AI 抽屉内容 | P1 |
| API-012 | 采纳 AI 通知建议 | POST | `/api/ai/notification-suggestions/{suggestionId}/apply` | AI 建议采纳 | P1 |

## 7. 接口详情

### API-001 获取通知统计

**请求方式**

- Method: `GET`
- Path: `/api/notifications/summary`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| scope | query | string | 否 | `mine` | `mine` / `team` / `org`，按权限生效 |
| date | query | string | 否 | `2026-05-11` | 今日处理统计日期 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "unreadCount": 5,
    "highPriorityCount": 2,
    "processedTodayCount": 8,
    "categoryCounts": {
      "all": 5,
      "pending": 3,
      "system": 1,
      "ai": 1
    },
    "generatedAt": "2026-05-11T10:00:00+08:00"
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 未登录 | `401` | 跳转登录 |
| 无权限 | `403` | 展示无权限提示 |
| 服务异常 | `500` | 指标卡显示兜底值或 Toast |

### API-002 获取通知列表

**请求方式**

- Method: `GET`
- Path: `/api/notifications`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `角色` | 搜索通知标题、描述、来源、处理对象 |
| category | query | string | 否 | `pending` | all / pending / system / ai |
| readStatus | query | string | 否 | `unread` | all / unread / read |
| priority | query | string | 否 | `P1` | P0-P3 |
| page | query | number | 否 | `1` | 页码 |
| pageSize | query | number | 否 | `20` | 每页数量 |
| sort | query | string | 否 | `createdAt:desc` | 默认按创建时间倒序 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "notice-role-change",
        "category": "pending",
        "type": "role_change_request",
        "icon": "warning",
        "iconTheme": "warning",
        "status": "待处理",
        "statusCode": "pending",
        "priority": "P1",
        "title": "角色模板变更申请",
        "description": "用户「张三」申请将项目角色从“研发”调整为“PM”，需要在角色管理页确认权限边界与成员分配策略。",
        "unread": true,
        "createdAt": "2026-05-11T09:50:00+08:00",
        "sourceName": "后台管理",
        "tags": [
          { "label": "后台管理", "type": "p1" },
          { "label": "角色变更", "type": "neutral" }
        ],
        "actionLabel": "查看角色管理",
        "actionType": "navigate",
        "actionPath": "/admin/roles",
        "targetId": "role_req_001",
        "handled": false
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 5
    },
    "categoryCounts": {
      "all": 5,
      "pending": 3,
      "system": 1,
      "ai": 1
    }
  }
}
```

**响应字段说明**

| 字段名 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| list | array | 是 | `[]` | 通知列表 |
| pagination | object | 是 | `{}` | 分页信息 |
| categoryCounts | object | 否 | `{}` | 分类数量，可替代 API-001 中的分类统计 |

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 参数错误 | `400 NOTIFICATION_PARAM_INVALID` | Toast 或重置筛选条件 |
| 无权限 | `403 NOTIFICATION_FORBIDDEN` | 展示无权限 |
| 服务异常 | `500` | 展示错误占位 |

### API-003 获取通知详情

**请求方式**

- Method: `GET`
- Path: `/api/notifications/{notificationId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| notificationId | path | string | 是 | `notice-role-change` | 通知 ID |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "notice-role-change",
    "title": "角色模板变更申请",
    "description": "用户「张三」申请将项目角色从“研发”调整为“PM”。",
    "detail": {
      "requesterName": "张三",
      "fromRole": "研发",
      "toRole": "PM",
      "projectName": "纳米材料项目 A"
    },
    "actionPath": "/admin/roles",
    "createdAt": "2026-05-11T09:50:00+08:00"
  }
}
```

### API-004 标记通知已读

**请求方式**

- Method: `POST`
- Path: `/api/notifications/{notificationId}/read`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| notificationId | path | string | 是 | `notice-role-change` | 通知 ID |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "notice-role-change",
    "unread": false,
    "readAt": "2026-05-11T10:05:00+08:00"
  }
}
```

### API-005 批量标记已读

**请求方式**

- Method: `POST`
- Path: `/api/notifications/read-batch`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| notificationIds | body | string[] | 否 | `["notice-role-change"]` | 指定通知 ID；为空时配合 `scope` |
| scope | body | string | 否 | `current_filter` | `all` / `current_filter` |
| category | body | string | 否 | `pending` | 当前筛选分类 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "updatedCount": 3
  }
}
```

### API-006 更新通知处理状态

**请求方式**

- Method: `POST`
- Path: `/api/notifications/{notificationId}/handle`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| notificationId | path | string | 是 | `notice-role-change` | 通知 ID |
| actionKey | body | string | 是 | `navigate` | 处理动作 |
| remark | body | string | 否 | `已查看角色管理` | 处理备注 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "notice-role-change",
    "handled": true,
    "handledAt": "2026-05-11T10:08:00+08:00",
    "targetPath": "/admin/roles"
  }
}
```

### API-007 获取通知处理建议

**请求方式**

- Method: `GET`
- Path: `/api/notifications/process-advice`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "title": "先处理权限和角色类通知",
      "description": "这两类通知会直接影响后台配置与项目权限边界，优先级高于一般系统更新和信息提醒。",
      "priority": 1
    },
    {
      "title": "AI 摘要类通知适合批量收尾",
      "description": "晨报、日志草稿和任务补录等内容可回到工作台集中处理。",
      "priority": 2
    }
  ]
}
```

### API-008 获取通知偏好

**请求方式**

- Method: `GET`
- Path: `/api/notification-preferences/me`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "inAppEnabled": true,
    "emailEnabled": true,
    "enterpriseWechatEnabled": false,
    "categories": {
      "pending": true,
      "system": true,
      "ai": true,
      "collaboration": true
    },
    "quietHours": {
      "enabled": false,
      "start": "22:00",
      "end": "08:00"
    }
  }
}
```

### API-009 更新通知偏好

**请求方式**

- Method: `PUT`
- Path: `/api/notification-preferences/me`
- Auth: 是

**请求参数**

请求 body 使用 API-008 的 `data` 结构。

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": true
}
```

### API-010 获取通知通道配置

**请求方式**

- Method: `GET`
- Path: `/api/admin/notification-channels`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "channel": "in_app",
      "name": "站内通知",
      "enabled": true,
      "status": "healthy"
    },
    {
      "channel": "email",
      "name": "邮件通知",
      "enabled": true,
      "status": "healthy"
    },
    {
      "channel": "enterprise_wechat",
      "name": "企业微信",
      "enabled": false,
      "status": "not_configured"
    }
  ]
}
```

### API-011 获取 AI 通知建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/notification-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| context | query | string | 否 | `notifications` | 当前上下文 |
| category | query | string | 否 | `pending` | 当前筛选分类 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "primarySuggestion": {
      "id": "sug_notice_001",
      "title": "通知处理建议",
      "content": "建议先完成高优先级权限审计，再处理角色模板申请；AI 晨报和日志评论类通知可回到工作台集中收尾。",
      "actions": [
        { "key": "accept", "label": "采纳建议" },
        { "key": "later", "label": "稍后处理" }
      ]
    },
    "items": [
      {
        "id": "sug_notice_002",
        "title": "统一入口已生效",
        "description": "通知详情现在承载在独立页面中，标题栏按钮不再打开旧弹窗。"
      },
      {
        "id": "sug_notice_003",
        "title": "可继续扩展筛选",
        "description": "后续可扩展状态筛选、已读管理或批量操作。"
      }
    ]
  }
}
```

### API-012 采纳 AI 通知建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/notification-suggestions/{suggestionId}/apply`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| suggestionId | path | string | 是 | `sug_notice_001` | AI 建议 ID |
| actionKey | body | string | 是 | `accept` | 动作 key |
| notificationIds | body | string[] | 否 | `["notice-audit-risk"]` | 关联通知 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "resultMessage": "已将高优先级通知置顶，并生成处理顺序建议。"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入通知中心 | 页面加载 | `GET /api/notifications/summary`、`GET /api/notifications` | 当前用户 | 渲染指标和列表 | 错误占位 / Toast |
| 搜索通知 | 顶部搜索框 | `GET /api/notifications` | `keyword` | 更新列表 | Toast |
| 点击分类筛选 | 筛选 chip | `GET /api/notifications` | `category` | 更新列表和数量 | Toast |
| 点击通知动作 | 通知卡片按钮 | `POST /api/notifications/{id}/read` 可选，随后跳转 | `notificationId`、`actionPath` | 标记已读并跳转 | Toast |
| 点击通知偏好 | 页面按钮 | `GET /api/notification-preferences/me` 后跳转设置页 | 当前用户 | 进入设置页 | 无权限提示 |
| 点击通道配置 | 页面按钮 | `GET /api/admin/notification-channels` 后跳转后台系统页 | 当前用户 | 进入后台系统页 | 无权限提示 |
| 打开 AI 助手 | 顶部/悬浮按钮 | `GET /api/ai/notification-suggestions` | 当前上下文、筛选条件 | 渲染 AI 抽屉 | Toast |
| 采纳 AI 建议 | AI 抽屉按钮 | `POST /api/ai/notification-suggestions/{id}/apply` | 建议 ID、通知 ID | Toast 或刷新建议 | Toast |
| 按 Esc | 全局键盘 | 无 | 无 | 关闭 AI 抽屉 | 无 |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| keyword | input | 否 | 最长 100 字，去除首尾空格 | 过滤非法字符 | 搜索关键词过长 |
| category | chip | 否 | 枚举值 | 枚举合法 | 分类参数不合法 |
| readStatus | query | 否 | 枚举值 | 枚举合法 | 已读状态不合法 |
| priority | query | 否 | P0-P3 | 枚举合法 | 优先级不合法 |
| notificationIds | body | 否 | 字符串数组 | 通知存在且属于当前用户 | 通知不存在或无权限 |
| actionKey | body | 是 | 枚举值 | 动作合法且用户有权限 | 操作不允许 |

### 9.1 提交规则

- 是否允许重复提交：处理通知、标记已读、AI 建议采纳不允许重复提交。
- 是否需要二次确认：高风险通知处理、批量已读可视产品需求增加二次确认。
- 是否需要审计日志：需要。高优先级通知处理、AI 建议采纳、通道配置跳转后的修改均应记录。
- 是否需要乐观锁或版本号：通知处理状态更新建议使用 `version` 或后端幂等控制。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 状态 | statusCode | string | 是 | 待处理 / 已完成 / AI 提醒 |
| 标题 | title | string | 否 | 支持关键词搜索 |
| 说明 | description | string | 否 | 支持关键词搜索 |
| 分类 | category | string | 是 | pending / system / ai |
| 优先级 | priority | string | 是 | P0-P3 |
| 未读 | unread | boolean | 是 | 是否未读 |
| 时间 | createdAt | string | 是 | 默认倒序 |
| 来源 | sourceName | string | 否 | 搜索和筛选可选 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 搜索标题、正文、来源、动作 |
| 分类 | category | string | `all` | all / pending / system / ai |
| 已读状态 | readStatus | string | `all` | all / unread / read |
| 优先级 | priority | string | 空 | P0-P3 |
| 页码 | page | number | 1 | 分页 |
| 页大小 | pageSize | number | 20 | 最大 100 |

### 10.3 分页规则

- 默认页大小：20。
- 最大页大小：100。
- 默认排序：`createdAt:desc`。
- 搜索时保留当前分类筛选。
- 分类数量建议基于当前用户全部可见通知计算，不只计算当前页。

## 11. 文件、导入、导出

通知中心当前无文件上传、导入、导出能力。

后续如需要导出通知记录，可复用全局导出任务接口：

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出通知记录 | `POST /api/notifications/export` | xlsx / csv | 不适用 | 异步任务 | P2，当前页面未设计按钮 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 页面核心能力 |
| 未读数同步 | 是 | 通知中心服务 | 顶部角标、指标卡 |
| 通知偏好 | 是 | 偏好配置服务 | 设置页承接 |
| 通知通道 | 是 | 后台系统配置服务 | 后台系统页承接 |
| AI 建议 | 是 | AI 通知建议服务 | 抽屉建议与采纳 |
| 审计日志 | 是 | 审计日志服务 | 高风险通知处理、AI 采纳 |
| WebSocket / SSE | 可选 | 通知推送服务 | 后续支持实时通知时使用 |

## 13. 缓存与实时性

- 数据是否允许缓存：通知列表不建议长缓存；统计可短缓存 10-30 秒。
- 缓存时间：未读数应尽量实时，最多 30 秒。
- 页面返回时是否刷新：建议刷新统计和当前筛选列表。
- 是否需要轮询：当前可不轮询；如没有 WebSocket，可每 60 秒刷新未读数。
- 是否需要 WebSocket / SSE：P1/P2 能力。实时通知上线后，顶部角标和通知列表可通过 WebSocket 推送更新。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `NOTIFICATION_PARAM_INVALID` | 参数错误 | Toast 或重置筛选 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录或 token 过期 | 跳转登录 |
| 403 / `NOTIFICATION_FORBIDDEN` | 无通知访问权限 | 展示无权限 |
| 403 / `NOTIFICATION_ACTION_FORBIDDEN` | 无通知处理权限 | Toast 提示无权限 |
| 404 / `NOTIFICATION_NOT_FOUND` | 通知不存在 | 从列表移除或展示不存在 |
| 409 / `NOTIFICATION_ALREADY_HANDLED` | 通知已处理 | 刷新列表 |
| 429 / `AI_RATE_LIMITED` | AI 建议请求过于频繁 | 提示稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | 展示失败提示 |

## 15. 验收标准

- 进入 `/notifications` 后，未读通知、高优先级、今日已处理三张指标卡由后端返回。
- 顶部通知角标不再硬编码 `5`，改为后端未读数。
- 通知列表不再使用前端 mock，可按分类、关键词、已读状态、优先级查询。
- 筛选按钮数量由后端统计返回，数量与当前用户权限范围一致。
- 搜索关键词能匹配通知标题、描述、来源、动作对象。
- 通知卡片字段完整支持标题、状态、标签、未读红点、时间、动作按钮和跳转路径。
- 点击通知动作后，可标记已读并跳转到正确业务页面。
- 无数据时展示当前已有空状态。
- 通知偏好和通道配置有明确接口承接。
- AI 抽屉建议由接口返回，采纳建议后有明确成功/失败反馈。
- 高优先级通知处理、AI 建议采纳等关键动作写入审计日志。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 通知列表是否需要服务端分页，还是首期只返回最近 N 条？ | 前后端 | 待确认 |
| Q2 | 通知分类是否固定为 `pending/system/ai`，还是后续扩展协作反馈、审批、风险等更多分类？ | 产品/后端 | 待确认 |
| Q3 | 点击通知动作时是否自动标记已读？ | 产品/前端 | 待确认 |
| Q4 | 是否需要“全部已读”“删除通知”“归档通知”等批量操作？ | 产品 | 待确认 |
| Q5 | 通知详情是否在当前页展开，还是统一跳转业务页面查看？ | 产品/前端 | 待确认 |
| Q6 | 右侧处理建议和入口说明由后端配置返回，还是前端静态文案即可？ | 产品/后端 | 待确认 |
| Q7 | AI 建议采纳后具体执行什么动作：排序置顶、生成待办、批量标记、还是仅记录采纳？ | 产品/AI/后端 | 待确认 |
| Q8 | 实时通知使用 WebSocket、SSE，还是仅靠页面刷新和短轮询？ | 后端/架构 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`src/views/Notifications.vue` 的 `metricCards`、`notifications`、`processAdviceItems`、`entryGuideItems`、`aiListItems`。
- 当前通知列表使用本地 `computed` 做筛选：`filteredNotifications`。
- 当前搜索只在前端本地过滤，未调用接口。
- 当前通知分类数量通过 `getFilterCount` 本地计算。
- 当前顶部通知角标静态写死为 `5`。
- 当前用户信息 mock：`currentUser = { name: "张工", role: "研发总监", avatar: ... }`。
- 当前通知动作使用 `handleNavigate(item.actionPath)` 跳转，部分 mock 路径仍是旧 html 路径，实际通过 `pushAppPath` 转为应用路由。
- 当前“通知偏好”跳转 `/settings`，“通道配置”跳转 `/admin/system`。
- 当前 AI 建议采纳只 emit `accept-ai-suggestion`，未接真实接口。
- 建议后续前端接入时将通知列表、统计、AI 建议分别抽象为响应式数据源，替换当前静态数组。
