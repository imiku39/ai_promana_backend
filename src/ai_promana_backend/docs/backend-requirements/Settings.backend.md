# 系统设置后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Settings.vue`  
> 页面定位：个人设置页，覆盖个人资料、通知偏好、账户安全和 AI 偏好。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 系统设置 / 个人设置 |
| 前端路由 | `/settings` |
| 前端文件 | `src/views/Settings.vue` |
| 所属模块 | 个人中心 / 系统设置 / 偏好配置 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 为当前登录用户提供个人资料、通知偏好、账户安全和 AI 偏好配置入口。
- 支持修改姓名、部门、邮箱、手机号。
- 支持配置任务状态变更、日志互动、报表订阅通知。
- 支持查看/发起修改密码和设备会话管理流程。
- 支持配置 AI 助手自动总结、智能排期建议、风险预警。
- 支持 AI 助手给出偏好建议并采纳。

### 2.2 对接范围

- 获取当前用户设置详情。
- 保存个人资料、通知偏好、AI 偏好。
- 恢复默认设置。
- 修改密码流程和设备会话列表/下线。
- 通知未读数、顶部当前用户信息。
- 设置项搜索。
- AI 偏好建议获取与采纳。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Login.vue` | 修改密码、会话失效后需要重新登录 |
| `Notifications.vue` | 通知偏好影响通知中心推送和展示 |
| `Dashboard.vue` | 全局顶部用户卡片和通知入口 |
| `Reports.vue` | 报表订阅偏好会影响定时报表通知 |
| `UserProfileHoverCard.vue` | 当前用户资料展示 |
| `AdminSystem.vue` | 后台系统配置页，和本页个人设置不同 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 否 | 是 | 否 | 否 | 编辑本人设置 |
| 管理员 | 是 | 否 | 是 | 否 | 否 | 编辑本人设置 |
| 项目负责人 | 是 | 否 | 是 | 否 | 否 | 编辑本人设置 |
| 成员 | 是 | 否 | 是 | 否 | 否 | 编辑本人设置 |
| 协作者 | 是 | 否 | 视权限 | 否 | 否 | 可按账号策略限制 |

### 3.1 权限规则

- 页面入口权限：访问 `/settings` 需要有效登录态。
- 按钮级权限：
  - “保存设置”“保存修改”需要当前用户有效登录态。
  - “恢复默认”需要当前用户有效登录态。
  - “修改密码”需要 `account:password:update` 或当前用户本人权限。
  - “设备会话查看/下线”需要 `account:session:read` / `account:session:revoke`。
  - “采纳 AI 建议”需要 `ai:preference-suggestion:apply`。
- 数据范围权限：用户只能查看和修改自己的个人设置；管理员代管他人设置应走后台用户管理接口。
- 敏感字段脱敏规则：手机号、邮箱可在展示时按安全策略部分脱敏；设备会话不返回完整 token、IP 可按权限脱敏。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 当前静态为张工/研发总监 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 当前静态为 5 |
| 用户设置详情 | 表单初始值 | 是 | `GET /api/user/settings` | 替代 localStorage |
| 设置默认值 | 恢复默认 | 否 | `GET /api/user/settings/defaults` | 可并入详情 |
| 设备会话摘要 | 账户安全展示 | 否 | `GET /api/auth/sessions/summary` | 当前静态 3 个设备 |
| AI 偏好建议 | AI 抽屉 | 否 | `GET /api/ai/settings-suggestions` | 打开抽屉时加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 设置加载中 | 请求处理中 | 当前未接 loading |
| saving | 保存中 | 写请求处理中 | 禁用按钮 |
| saved | Toast 设置已保存 | 保存成功 | 当前本地 toast |
| reset | Toast 设置已恢复 | 恢复默认成功 | 当前本地逻辑 |
| error | Toast / 字段错误 | 接口异常或校验失败 | 需标准错误 |
| drawerOpen | AI 抽屉打开 | 加载建议 | 当前静态文案 |

## 5. 字段模型

### 5.1 用户设置主对象字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| userId | string | 是 | 隐含字段 | `u_10001` | 当前用户 ID |
| profile.name | string | 是 | 个人资料/姓名 | `张工` | 用户姓名 |
| profile.department | string | 是 | 个人资料/部门 | `研发中心` | 部门名称 |
| profile.departmentId | string | 否 | 隐含字段 | `dept_rd` | 部门 ID |
| profile.email | string | 是 | 个人资料/邮箱 | `zhang@example.com` | 邮箱 |
| profile.phone | string | 否 | 个人资料/手机号 | `138****7788` | 展示可脱敏 |
| notifications.taskStatus | boolean | 是 | 通知偏好 | `true` | 任务状态变更提醒 |
| notifications.logFeedback | boolean | 是 | 通知偏好 | `true` | 日志互动提醒 |
| notifications.reportSubscription | boolean | 是 | 通知偏好 | `false` | 报表订阅通知 |
| aiPrefs.autoSummary | boolean | 是 | AI 偏好 | `true` | AI 自动总结 |
| aiPrefs.scheduling | boolean | 是 | AI 偏好 | `true` | 智能排期建议 |
| aiPrefs.riskAlert | boolean | 是 | AI 偏好 | `false` | 风险预警 |
| updatedAt | string | 否 | 设置版本 | `2026-05-11T13:20:00+08:00` | 更新时间 |
| version | number | 是 | 保存设置 | `3` | 乐观锁版本 |

### 5.2 设备会话字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| sessionId | string | 是 | 会话列表 | `sess_001` | 会话 ID |
| deviceName | string | 是 | 设备名称 | `Chrome / Windows` | 设备信息 |
| ip | string | 否 | IP | `192.168.*.*` | 可脱敏 |
| location | string | 否 | 登录地点 | `上海` | 由 IP 解析 |
| lastActiveAt | string | 是 | 最近活跃 | `2026-05-11T13:00:00+08:00` | 时间 |
| current | boolean | 是 | 当前设备 | `true` | 是否当前会话 |

### 5.3 设置搜索字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | string | 否 | 顶部搜索框 | `通知` | 搜索设置项、通知或安全策略 |
| results[].tab | string | 是 | 搜索结果 | `notification` | 定位 tab |
| results[].label | string | 是 | 搜索结果 | `任务状态变更` | 设置项名称 |
| results[].description | string | 否 | 搜索结果 | `任务完成...` | 说明 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| settingsTab | `profile` | 个人资料 | active | 默认 tab |
| settingsTab | `notification` | 通知偏好 | active | 通知设置 |
| settingsTab | `security` | 账户安全 | active | 密码与会话 |
| settingsTab | `ai` | AI 偏好 | active | 智能助手设置 |
| notificationChannel | `in_app` | 站内 | neutral | 站内消息 |
| notificationChannel | `email` | 邮件 | neutral | 邮件 |
| notificationChannel | `wechat_work` | 企微 | neutral | 企业微信 |
| securityAction | `password` | 修改密码 | primary | 修改密码流程 |
| securityAction | `session` | 设备会话 | primary | 会话管理 |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| activeSessionCount | number | 当前有效登录会话数 | 账户安全/设备会话 | 当前静态为 3 |
| lastPasswordChangedAt | string | 最近一次密码修改时间 | 账户安全/修改密码 | 当前静态 2026-03-12 |
| enabledNotificationCount | number | 开启的通知偏好数量 | 可选 | P2 |
| enabledAiPrefCount | number | 开启的 AI 偏好数量 | 可选 | P2 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取用户设置 | GET | `/api/user/settings` | 首屏设置详情 | P0 |
| API-002 | 保存用户设置 | PUT | `/api/user/settings` | 保存个人资料、通知、AI 偏好 | P0 |
| API-003 | 恢复默认设置 | POST | `/api/user/settings/reset` | 恢复默认 | P0 |
| API-004 | 获取设置默认值 | GET | `/api/user/settings/defaults` | 默认值 | P1 |
| API-005 | 搜索设置项 | GET | `/api/user/settings/search` | 设置搜索 | P1 |
| API-006 | 修改密码 | POST | `/api/auth/password/change` | 账户安全 | P0 |
| API-007 | 获取设备会话列表 | GET | `/api/auth/sessions` | 会话管理 | P1 |
| API-008 | 下线设备会话 | DELETE | `/api/auth/sessions/{sessionId}` | 删除会话 | P1 |
| API-009 | 获取设备会话摘要 | GET | `/api/auth/sessions/summary` | 当前 3 个设备 | P1 |
| API-010 | 获取 AI 设置建议 | GET | `/api/ai/settings-suggestions` | AI 抽屉建议 | P1 |
| API-011 | 采纳 AI 设置建议 | POST | `/api/ai/settings-suggestions/{suggestionId}/apply` | 修改偏好 | P1 |
| API-012 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部角标 | P0 |

## 7. 接口详情

### API-001 获取用户设置

**请求方式**

- Method: `GET`
- Path: `/api/user/settings`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "userId": "u_10001",
    "profile": {
      "name": "张工",
      "department": "研发中心",
      "departmentId": "dept_rd",
      "email": "zhang@example.com",
      "phone": "138****7788"
    },
    "notifications": {
      "taskStatus": true,
      "logFeedback": true,
      "reportSubscription": false
    },
    "aiPrefs": {
      "autoSummary": true,
      "scheduling": true,
      "riskAlert": false
    },
    "security": {
      "lastPasswordChangedAt": "2026-03-12T09:00:00+08:00",
      "activeSessionCount": 3
    },
    "updatedAt": "2026-05-11T13:20:00+08:00",
    "version": 3
  }
}
```

### API-002 保存用户设置

**请求方式**

- Method: `PUT`
- Path: `/api/user/settings`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| profile | body | object | 是 | `{}` | 个人资料 |
| notifications | body | object | 是 | `{}` | 通知偏好 |
| aiPrefs | body | object | 是 | `{}` | AI 偏好 |
| version | body | number | 是 | `3` | 乐观锁版本 |

**请求示例**

```json
{
  "profile": {
    "name": "张工",
    "department": "研发中心",
    "departmentId": "dept_rd",
    "email": "zhang@example.com",
    "phone": "13800137788"
  },
  "notifications": {
    "taskStatus": true,
    "logFeedback": true,
    "reportSubscription": false
  },
  "aiPrefs": {
    "autoSummary": true,
    "scheduling": true,
    "riskAlert": false
  },
  "version": 3
}
```

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "updatedAt": "2026-05-11T13:30:00+08:00",
    "version": 4
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 邮箱格式错误 | `400 USER_EMAIL_INVALID` | 邮箱字段错误 |
| 手机号格式错误 | `400 USER_PHONE_INVALID` | 手机号字段错误 |
| 邮箱已被占用 | `409 USER_EMAIL_EXISTS` | 邮箱字段错误 |
| 版本冲突 | `409 SETTINGS_VERSION_CONFLICT` | 提示刷新后重试 |
| 无权限 | `403 SETTINGS_UPDATE_FORBIDDEN` | Toast |

### API-003 恢复默认设置

**请求方式**

- Method: `POST`
- Path: `/api/user/settings/reset`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| sections | body | string[] | 否 | `["notifications","aiPrefs"]` | 不传则恢复全部可恢复设置 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "profile": {
      "name": "张工",
      "department": "研发中心",
      "email": "zhang@example.com",
      "phone": "138****7788"
    },
    "notifications": {
      "taskStatus": false,
      "logFeedback": false,
      "reportSubscription": false
    },
    "aiPrefs": {
      "autoSummary": false,
      "scheduling": false,
      "riskAlert": false
    },
    "version": 5
  }
}
```

### API-006 修改密码

**请求方式**

- Method: `POST`
- Path: `/api/auth/password/change`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| oldPassword | body | string | 是 | `OldPassword@123` | 原密码 |
| newPassword | body | string | 是 | `NewPassword@123` | 新密码 |
| confirmPassword | body | string | 是 | `NewPassword@123` | 确认新密码 |
| revokeOtherSessions | body | boolean | 否 | `true` | 是否下线其他设备 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "changedAt": "2026-05-11T13:35:00+08:00",
    "revokedSessionCount": 2
  }
}
```

### API-007 获取设备会话列表

**请求方式**

- Method: `GET`
- Path: `/api/auth/sessions`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "sessionId": "sess_001",
      "deviceName": "Chrome / Windows",
      "ip": "192.168.*.*",
      "location": "上海",
      "lastActiveAt": "2026-05-11T13:00:00+08:00",
      "current": true
    }
  ]
}
```

### API-010 获取 AI 设置建议

**请求方式**

- Method: `GET`
- Path: `/api/ai/settings-suggestions`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| context | query | string | 否 | `settings` | 当前上下文 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "suggestionId": "sug_settings_001",
    "title": "偏好建议",
    "content": "你当前同时开启了任务和日志通知，建议保留站内提醒并关闭邮件提醒，减少高频干扰。",
    "actions": [
      {
        "key": "reduce_email_notifications",
        "label": "采纳建议"
      }
    ],
    "previewSettings": {
      "notifications": {
        "taskStatus": true,
        "logFeedback": true,
        "reportSubscription": false
      }
    }
  }
}
```

### API-011 采纳 AI 设置建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/settings-suggestions/{suggestionId}/apply`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| suggestionId | path | string | 是 | `sug_settings_001` | 建议 ID |
| actionKey | body | string | 是 | `reduce_email_notifications` | 动作 |
| version | body | number | 是 | `4` | 设置版本 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "settings": {
      "notifications": {
        "taskStatus": true,
        "logFeedback": true,
        "reportSubscription": false
      }
    },
    "version": 5
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入系统设置 | 页面加载 | `GET /api/user/settings`、`GET /api/notifications/unread-count` | 当前用户 | 渲染表单 | 错误占位 |
| 切换设置 tab | 左侧设置导航 | 无 | activeTab | 展示对应卡片 | 无 |
| 搜索设置项 | 顶部搜索框 | `GET /api/user/settings/search` | keyword | 定位设置项 | 无结果提示 |
| 修改个人资料 | 表单输入 | 无 | 本地表单 | 本地更新 | 前端校验 |
| 切换通知偏好 | toggle | 无或 `PUT /api/user/settings` | notifications | 本地更新或自动保存 | Toast |
| 切换 AI 偏好 | toggle | 无或 `PUT /api/user/settings` | aiPrefs | 本地更新或自动保存 | Toast |
| 保存设置 | 侧边栏/页面按钮 | `PUT /api/user/settings` | 表单 | Toast，更新版本 | 字段错误 |
| 恢复默认 | 页面按钮 | `POST /api/user/settings/reset` | sections | Toast，刷新表单 | Toast |
| 修改密码 | 账户安全按钮 | `POST /api/auth/password/change` | 密码表单 | Toast，可下线设备 | 表单错误 |
| 查看设备会话 | 账户安全按钮 | `GET /api/auth/sessions` | 当前用户 | 打开会话管理 | Toast |
| 打开通知中心 | 通知图标 | 无 | - | 跳转/打开通知 | - |
| 打开 AI 助手 | 顶部/悬浮按钮 | `GET /api/ai/settings-suggestions` | context | 渲染建议 | Toast |
| 采纳 AI 建议 | AI 抽屉 | `POST /api/ai/settings-suggestions/{id}/apply` | suggestionId/actionKey | Toast，更新设置 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| profile.name | input | 是 | 2-40 字 | 非空、长度合法 | 请输入姓名 |
| profile.department | input/select | 是 | 2-60 字 | 部门合法 | 请输入部门 |
| profile.email | input | 是 | 邮箱格式 | 邮箱唯一或允许本人原邮箱 | 请输入有效邮箱 |
| profile.phone | input | 否 | 手机号格式 | 手机号合法 | 请输入有效手机号 |
| notifications.taskStatus | toggle | 是 | boolean | 布尔值 | 无 |
| notifications.logFeedback | toggle | 是 | boolean | 布尔值 | 无 |
| notifications.reportSubscription | toggle | 是 | boolean | 布尔值 | 无 |
| aiPrefs.autoSummary | toggle | 是 | boolean | 布尔值 | 无 |
| aiPrefs.scheduling | toggle | 是 | boolean | 布尔值 | 无 |
| aiPrefs.riskAlert | toggle | 是 | boolean | 布尔值 | 无 |
| oldPassword | password | 修改密码必填 | 非空 | 原密码正确 | 原密码错误 |
| newPassword | password | 修改密码必填 | 密码策略 | 不可与旧密码相同 | 新密码不符合规则 |
| confirmPassword | password | 修改密码必填 | 与新密码一致 | 一致性校验 | 两次密码不一致 |

### 9.1 提交规则

- 是否允许重复提交：保存、恢复默认、修改密码、采纳 AI 建议请求中不允许重复提交。
- 是否需要二次确认：恢复默认、下线其他设备、下线全部设备需要二次确认。
- 是否需要审计日志：需要，个人资料变更、通知偏好变更、AI 偏好变更、修改密码、设备下线、AI 采纳都记录。
- 是否需要乐观锁或版本号：需要，保存设置和 AI 采纳使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 设备名称 | deviceName | string | 否 | 设备会话列表 |
| IP | ip | string | 否 | 可脱敏 |
| 地点 | location | string | 否 | IP 解析 |
| 最近活跃 | lastActiveAt | string | 是 | 设备会话列表 |
| 当前设备 | current | boolean | 否 | 当前会话不可下线或需特殊提示 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 搜索设置项、通知或安全策略 |
| 设置分组 | tab | string | all | profile/notification/security/ai |

### 10.3 分页规则

- 设置页主表单无分页。
- 设备会话数量通常较少，可不分页；如超过 50 条，支持 `page`、`pageSize`。
- 设置搜索结果可返回前 20 条匹配项。

## 11. 文件、导入、导出

系统设置页当前无文件上传、导入、导出能力。

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出个人设置 | `POST /api/user/settings/export` | json | 不适用 | 同步 | P2，可选 |
| 导入个人设置 | `POST /api/user/settings/import` | json | 待确认 | 上传并预览 | P2，可选 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 顶部未读数、通知偏好控制 |
| 邮件/企微通知 | 是 | 通知服务 | 通知偏好可影响渠道 |
| AI 偏好建议 | 是 | AI 设置建议服务 | 抽屉偏好建议和采纳 |
| 审计日志 | 是 | 审计日志服务 | 设置变更、密码、会话操作 |
| WebSocket / SSE | 否 | 无 | 设置页不需要实时连接 |

## 13. 缓存与实时性

- 数据是否允许缓存：用户设置可本地缓存，但以后端为准；修改后应更新缓存。
- 缓存时间：前端可短缓存当前会话；跨设备需要重新拉取。
- 页面返回时是否刷新：建议刷新用户设置和通知未读数。
- 是否需要轮询：不需要。
- 是否需要 WebSocket / SSE：不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 / Toast |
| 400 / `SETTINGS_VALIDATE_FAILED` | 设置字段校验失败 | 表单错误 |
| 400 / `USER_EMAIL_INVALID` | 邮箱格式错误 | 邮箱字段错误 |
| 400 / `USER_PHONE_INVALID` | 手机号格式错误 | 手机号字段错误 |
| 400 / `PASSWORD_POLICY_INVALID` | 新密码不符合规则 | 密码字段错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录或 token 过期 | 跳转登录 |
| 403 / `SETTINGS_UPDATE_FORBIDDEN` | 无设置修改权限 | Toast |
| 404 / `SESSION_NOT_FOUND` | 会话不存在 | 刷新会话列表 |
| 409 / `USER_EMAIL_EXISTS` | 邮箱已被占用 | 邮箱字段错误 |
| 409 / `SETTINGS_VERSION_CONFLICT` | 设置版本冲突 | 提示刷新 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 进入 `/settings` 后，个人资料、通知偏好、AI 偏好和安全摘要由 `GET /api/user/settings` 返回。
- 保存设置调用 `PUT /api/user/settings`，不再只写入 `localStorage`。
- 恢复默认调用 `POST /api/user/settings/reset`，返回默认后的设置并更新页面。
- 个人资料字段支持姓名、部门、邮箱、手机号校验，邮箱重复和格式错误有明确错误码。
- 通知偏好和 AI 偏好保存后能影响通知/AI 服务实际行为。
- 修改密码和设备会话管理有独立接口支撑，并记录审计日志。
- AI 抽屉建议由接口返回，采纳后能更新设置并返回新版本。
- 当前用户只能修改自己的设置，不能越权修改他人设置。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 本页标题为“系统设置”，但内容是个人设置；是否需要改名为“个人设置”？ | 产品/前端 | 待确认 |
| Q2 | 部门字段是否允许用户自行修改，还是只能由管理员在后台修改？ | 产品/后端 | 待确认 |
| Q3 | 邮箱/手机号修改是否需要验证码确认？ | 产品/安全/后端 | 待确认 |
| Q4 | 通知偏好是否只控制通知类型，还是还要细分站内/邮件/企微渠道？ | 产品/后端 | 待确认 |
| Q5 | 恢复默认是否恢复个人资料，还是只恢复通知偏好和 AI 偏好？ | 产品/前端 | 待确认 |
| Q6 | AI 偏好建议采纳是直接修改设置，还是先展示预览让用户确认？ | 产品/AI/前端 | 待确认 |

## 17. 前端备注

- 当前页面中的本地数据位置：`src/views/Settings.vue` 的 `defaultProfileForm`、`defaultNotificationPrefs`、`defaultAiPrefs`。
- 当前保存行为：`handleSaveSettings` 将设置写入 `localStorage.setItem('app-settings', ...)`，未接后端接口。
- 当前恢复默认行为：`handleResetSettings` 会把通知偏好和 AI 偏好全部置为关闭，然后调用本地保存。
- 当前通知角标静态为 `5`。
- 当前“修改密码”“设备会话”“应用切换器”“AI 偏好建议采纳”均只 emit 或本地控制，未接真实接口。
- 当前 `handleOpenNotifications` 只 emit，没有跳转 `/notifications`。
- 需要后端优先确认的字段：部门是否可改、邮箱/手机号验证规则、通知渠道细分、AI 偏好实际影响范围。
- 需要后端优先确认的接口：`GET /api/user/settings`、`PUT /api/user/settings`、`POST /api/user/settings/reset`、`POST /api/auth/password/change`。
