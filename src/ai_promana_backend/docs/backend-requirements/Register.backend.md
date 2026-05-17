# 注册页后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Register.vue`

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 注册页 / 创建协作账户 |
| 前端路由 | `/register` |
| 前端文件 | `src/views/Register.vue` |
| 所属模块 | 认证与账号体系 / 用户注册 / 管理员审核 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 支持未登录用户提交研发协作平台账号注册申请。
- 注册表单收集账号、姓名、邮箱、部门、密码、确认密码。
- 提交后由系统管理员审核并分配平台角色，审核通过后用户可登录系统。
- 注册成功不直接进入系统，当前前端提交后跳转 `/login`。

### 2.2 对接范围

- 注册申请提交接口。
- 账号、邮箱、密码、部门等字段校验。
- 账号/邮箱唯一性校验。
- 注册后账号状态：待审核、已通过、已拒绝、已禁用。
- 管理员审核注册申请和角色分配的后续接口关联。
- 注册成功通知、管理员待办通知、注册审计日志。
- 验证码、邮箱验证、部门下拉等能力当前 UI 未展示，可作为 P1/P2。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Login.vue` | 注册页“返回登录”跳转登录页；注册成功后建议跳转登录页 |
| `AdminUsers.vue` | 管理员审核注册申请、分配角色、启用账号 |
| `AdminRoles.vue` | 注册审核通过后可分配系统角色 |
| `Notifications.vue` | 管理员收到注册待审核通知，用户收到审核结果通知 |
| `router/index.js` | `/register` 路由公开访问，无需登录态 |

## 3. 角色与权限

| 角色 | 可查看注册页 | 可新增注册申请 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 未登录用户 | 是 | 是 | 否 | 否 | 否 | 注册页公开访问 |
| 待审核用户 | 是 | 否 | 否 | 否 | 否 | 已提交申请，等待审核 |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 可审核注册申请 |
| 管理员 | 是 | 视权限 | 是 | 视权限 | 是 | 需要用户管理权限 |
| 项目负责人 / 成员 | 是 | 是 | 否 | 否 | 否 | 未登录状态下提交申请 |

### 3.1 权限规则

- 页面入口权限：`/register` 不需要 token；如果已登录访问 `/register`，前端可跳转 `/dashboard`。
- 注册提交接口：不需要登录态，但需要频率限制、IP 限制和安全校验。
- 按钮级权限：注册页本身无按钮级权限控制。
- 数据范围权限：注册申请进入待审核池，只有具备 `user:registration:review` 的管理员可查看和处理。
- 敏感字段脱敏规则：后端不得返回密码、密码盐；注册申请列表中邮箱可按管理员权限决定是否脱敏。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 注册表单 | 用户输入注册信息 | 是 | 前端本地状态 | 当前字段来自 `registerForm` |
| 注册配置 | 密码规则、是否开放注册、是否需要验证码 | 否 | `GET /api/auth/register/config` | P1，当前页面未接 |
| 部门选项 | 部门下拉或自动补全 | 否 | `GET /api/org/departments` | 当前前端为自由输入 |
| 已登录状态 | 已登录用户访问注册页时跳转 | 否 | `GET /api/auth/me` | 可选 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| idle | 表单可输入 | 未发起请求 | 默认 |
| validating | 字段校验中 | 账号/邮箱校验 | P1 |
| loading | 提交按钮 loading / 禁用 | 注册请求处理中 | 后续前端补充 |
| success | 跳转 `/login` | 注册申请提交成功 | 提示等待审核 |
| pending | 等待审核 | 账号已创建但未启用 | 登录时返回待审核 |
| error | Toast 或字段错误 | 参数错误、重复、服务异常 | 需标准错误码 |

## 5. 字段模型

### 5.1 注册请求字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| account | string | 是 | 账号输入框 | `RD0001` | 研发工号 / 平台账号，需唯一 |
| name | string | 是 | 姓名输入框 | `王志强` | 用户真实姓名 |
| email | string | 是 | 邮箱输入框 | `wang@example.com` | 工作邮箱，需唯一 |
| department | string | 是 | 部门输入框 | `材料科学部` | 当前前端自由输入，后续可改为部门 ID |
| departmentId | string | 否 | 隐含字段 | `dept_material` | 如接组织架构，建议提交 ID |
| password | string | 是 | 密码输入框 | `Password@123` | 密码明文经 HTTPS 传输，后端哈希存储 |
| confirmPassword | string | 是 | 确认密码输入框 | `Password@123` | 前端校验一致，后端也需校验 |
| inviteCode | string | 否 | 暂无控件 | `INVITE-001` | 如启用邀请码注册 |
| captchaToken | string | 否 | 暂无控件 | `captcha_xxx` | 连续失败或安全策略触发 |
| clientType | string | 否 | 隐含字段 | `web` | 客户端类型 |

### 5.2 注册响应字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| registrationId | string | 是 | 注册结果 | `reg_10001` | 注册申请 ID |
| userId | string | 否 | 审核对象 | `u_10001` | 如提交后立即创建用户 |
| account | string | 是 | 注册结果 | `RD0001` | 注册账号 |
| email | string | 是 | 注册结果 | `wang@example.com` | 注册邮箱 |
| accountStatus | string | 是 | 登录/审核状态 | `pending` | 默认待审核 |
| reviewStatus | string | 是 | 审核状态 | `pending` | 待审核 |
| submittedAt | string | 是 | 注册结果 | `2026-05-11T12:20:00+08:00` | 提交时间 |
| message | string | 否 | Toast 文案 | `注册申请已提交` | 可展示文案 |
| redirectPath | string | 否 | 跳转 | `/login` | 注册成功后跳转 |

### 5.3 注册审核字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| reviewStatus | string | 是 | 管理员审核列表 | `pending` | 待审核/通过/拒绝 |
| roleIds | string[] | 审核通过时必填 | 管理员分配角色 | `["role_dev"]` | 平台角色 |
| reviewerId | string | 否 | 审计 | `u_admin` | 审核人 |
| reviewedAt | string | 否 | 审计 | `2026-05-11T13:00:00+08:00` | 审核时间 |
| rejectReason | string | 拒绝时必填 | 审核结果 | `资料不完整` | 拒绝原因 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| accountStatus | `pending` | 待审核 | warning | 注册后默认状态 |
| accountStatus | `active` | 正常 | success | 审核通过，可登录 |
| accountStatus | `rejected` | 已拒绝 | danger | 审核拒绝 |
| accountStatus | `disabled` | 已禁用 | danger | 管理员禁用 |
| reviewStatus | `pending` | 待审核 | warning | 待管理员处理 |
| reviewStatus | `approved` | 已通过 | success | 审核通过 |
| reviewStatus | `rejected` | 已拒绝 | danger | 审核拒绝 |
| registerSource | `self_register` | 自主注册 | neutral | 用户自主提交 |
| registerSource | `invite` | 邀请注册 | primary | 通过邀请码 |

### 5.5 统计字段

注册页本身无统计展示。管理员审核页面可统计待审核数、今日新增申请数、通过率等，由 `AdminUsers.vue` 或后台管理文档承接。

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取注册配置 | GET | `/api/auth/register/config` | 注册规则、是否开放注册 | P1 |
| API-002 | 提交注册申请 | POST | `/api/auth/register` | 注册页核心提交 | P0 |
| API-003 | 校验账号可用性 | GET | `/api/auth/register/check-account` | 账号唯一性校验 | P1 |
| API-004 | 校验邮箱可用性 | GET | `/api/auth/register/check-email` | 邮箱唯一性校验 | P1 |
| API-005 | 获取部门列表 | GET | `/api/org/departments` | 部门选择/自动补全 | P1 |
| API-006 | 查询注册申请状态 | GET | `/api/auth/register/{registrationId}` | 提交后状态查询 | P2 |
| API-007 | 管理员审核注册申请 | POST | `/api/admin/registrations/{registrationId}/review` | 审核通过/拒绝 | P1 |
| API-008 | 发送邮箱验证码 | POST | `/api/auth/register/email-code` | 邮箱验证 | P2 |

## 7. 接口详情

### API-001 获取注册配置

**请求方式**

- Method: `GET`
- Path: `/api/auth/register/config`
- Auth: 否

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "registrationEnabled": true,
    "reviewRequired": true,
    "emailVerificationRequired": false,
    "captchaRequired": false,
    "inviteCodeRequired": false,
    "passwordPolicy": {
      "minLength": 8,
      "maxLength": 128,
      "requireUppercase": true,
      "requireLowercase": true,
      "requireNumber": true,
      "requireSpecialChar": false
    },
    "departmentMode": "free_text"
  }
}
```

### API-002 提交注册申请

**请求方式**

- Method: `POST`
- Path: `/api/auth/register`
- Auth: 否

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| account | body | string | 是 | `RD0001` | 研发工号 / 平台账号 |
| name | body | string | 是 | `王志强` | 姓名 |
| email | body | string | 是 | `wang@example.com` | 邮箱 |
| department | body | string | 是 | `材料科学部` | 部门名称 |
| departmentId | body | string | 否 | `dept_material` | 部门 ID |
| password | body | string | 是 | `Password@123` | 密码 |
| confirmPassword | body | string | 是 | `Password@123` | 确认密码 |
| inviteCode | body | string | 否 | `INVITE-001` | 邀请码 |
| captchaToken | body | string | 否 | `captcha_xxx` | 验证码 token |
| clientType | body | string | 否 | `web` | 客户端类型 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "registrationId": "reg_10001",
    "userId": "u_10001",
    "account": "RD0001",
    "email": "wang@example.com",
    "accountStatus": "pending",
    "reviewStatus": "pending",
    "submittedAt": "2026-05-11T12:20:00+08:00",
    "message": "注册申请已提交，请等待系统管理员审核。",
    "redirectPath": "/login"
  }
}
```

**响应字段说明**

| 字段名 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| registrationId | string | 是 | `reg_10001` | 注册申请 ID |
| userId | string | 否 | `u_10001` | 用户 ID，如后端提交时创建用户 |
| accountStatus | string | 是 | `pending` | 账号状态 |
| reviewStatus | string | 是 | `pending` | 审核状态 |
| submittedAt | string | 是 | `2026-05-11T12:20:00+08:00` | 提交时间 |
| redirectPath | string | 否 | `/login` | 成功后建议跳转 |

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 注册已关闭 | `403 AUTH_REGISTER_DISABLED` | 提示注册暂未开放 |
| 参数缺失/格式错误 | `400 AUTH_REGISTER_PARAM_INVALID` | 展示字段错误 |
| 账号已存在 | `409 AUTH_ACCOUNT_EXISTS` | 账号字段错误 |
| 邮箱已存在 | `409 AUTH_EMAIL_EXISTS` | 邮箱字段错误 |
| 密码不符合规则 | `400 AUTH_PASSWORD_POLICY_INVALID` | 展示密码规则 |
| 两次密码不一致 | `400 AUTH_PASSWORD_CONFIRM_NOT_MATCH` | 确认密码字段错误 |
| 邀请码无效 | `400 AUTH_INVITE_CODE_INVALID` | 邀请码错误 |
| 验证码无效 | `400 AUTH_CAPTCHA_INVALID` | 重新验证 |
| 请求过于频繁 | `429 AUTH_REGISTER_RATE_LIMITED` | 提示稍后再试 |
| 服务异常 | `500 COMMON_SERVER_ERROR` | Toast 提示提交失败 |

### API-003 校验账号可用性

**请求方式**

- Method: `GET`
- Path: `/api/auth/register/check-account`
- Auth: 否

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| account | query | string | 是 | `RD0001` | 待校验账号 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "available": true,
    "normalizedAccount": "RD0001"
  }
}
```

### API-004 校验邮箱可用性

**请求方式**

- Method: `GET`
- Path: `/api/auth/register/check-email`
- Auth: 否

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| email | query | string | 是 | `wang@example.com` | 待校验邮箱 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "available": true,
    "normalizedEmail": "wang@example.com"
  }
}
```

### API-005 获取部门列表

**请求方式**

- Method: `GET`
- Path: `/api/org/departments`
- Auth: 否 / 是，待确认

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `材料` | 部门搜索 |
| enabledOnly | query | boolean | 否 | `true` | 只返回可用部门 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": "dept_material",
      "name": "材料科学部",
      "parentId": null,
      "enabled": true
    }
  ]
}
```

### API-007 管理员审核注册申请

**请求方式**

- Method: `POST`
- Path: `/api/admin/registrations/{registrationId}/review`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| registrationId | path | string | 是 | `reg_10001` | 注册申请 ID |
| action | body | string | 是 | `approve` | approve / reject |
| roleIds | body | string[] | 通过时必填 | `["role_dev"]` | 分配角色 |
| departmentId | body | string | 否 | `dept_material` | 确认部门 |
| rejectReason | body | 拒绝时必填 | `资料不完整` | 拒绝原因 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "registrationId": "reg_10001",
    "userId": "u_10001",
    "reviewStatus": "approved",
    "accountStatus": "active",
    "reviewedAt": "2026-05-11T13:00:00+08:00"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入注册页 | 页面加载 | 可选 `GET /api/auth/register/config` | 无 | 渲染规则 | Toast / 禁用注册 |
| 输入账号 | 账号输入框 | 可选 `GET /api/auth/register/check-account` | `registerForm.account` | 可用提示 | 字段错误 |
| 输入邮箱 | 邮箱输入框 | 可选 `GET /api/auth/register/check-email` | `registerForm.email` | 可用提示 | 字段错误 |
| 输入部门 | 部门输入框 | 可选 `GET /api/org/departments` | keyword | 自动补全 | 无 |
| 点击返回登录 | 返回登录链接 | 无 | 无 | 跳转 `/login` | 无 |
| 点击提交注册 | 提交注册按钮 | `POST /api/auth/register` | 注册表单 | Toast，跳转 `/login` | 字段错误 / Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| account | input text | 是 | 2-64 字，建议字母数字下划线/短横线 | 唯一、格式合法 | 请输入研发工号 |
| name | input text | 是 | 2-40 字 | 非空、长度合法 | 请输入姓名 |
| email | input email | 是 | 邮箱格式 | 唯一、格式合法 | 请输入有效邮箱 |
| department | input text | 是 | 2-60 字 | 部门存在或自由文本合法 | 请输入部门 |
| departmentId | select/hidden | 否 | 必须来自部门列表 | 部门存在且可用 | 请选择有效部门 |
| password | input password | 是 | 8-128 字，符合密码策略 | 强度、黑名单、历史密码 | 请设置安全密码 |
| confirmPassword | input password | 是 | 与 password 一致 | 一致性校验 | 两次输入密码不一致 |
| inviteCode | input | 条件必填 | 按注册配置 | 邀请码有效 | 邀请码无效 |
| captchaToken | captcha | 条件必填 | 按安全策略 | 验证码有效 | 验证码无效 |

### 9.1 提交规则

- 是否允许重复提交：不允许，注册请求处理中禁用提交按钮。
- 是否需要二次确认：不需要。
- 是否需要审计日志：需要，注册申请提交、审核通过、审核拒绝都记录。
- 是否需要邮箱验证：当前 UI 未展示，后端可通过配置决定是否 P2 接入。
- 是否需要验证码：当前 UI 未展示，后端可在安全策略触发后返回 `captchaRequired=true`。
- 是否需要乐观锁或版本号：注册提交不需要；管理员审核申请时建议使用申请 `version` 防止重复审核。

## 10. 列表、筛选、分页与排序

注册页无列表、筛选、分页、排序能力。注册申请审核列表由后台用户管理页面承接。

## 11. 文件、导入、导出

注册页无文件上传、导入、导出能力。

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 注册申请提交后通知管理员；审核结果通知用户 |
| 邮件通知 | 可选 | 邮件服务 | 审核结果、邮箱验证 |
| AI 建议 | 否 | 无 | 注册页不需要 AI 能力 |
| 审计日志 | 是 | 审计日志服务 | 注册提交、审核、拒绝、异常请求 |
| WebSocket / SSE | 否 | 无 | 注册页不需要实时连接 |

## 13. 缓存与实时性

- 数据是否允许缓存：注册配置可短缓存 5-10 分钟；部门列表可缓存 5 分钟。
- 缓存时间：注册配置变更后前端刷新即可生效。
- 页面返回时是否刷新：建议重新读取注册配置，避免注册开关变化。
- 是否需要轮询：不需要。
- 是否需要 WebSocket / SSE：不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 提示提交成功并跳转登录 |
| 400 / `AUTH_REGISTER_PARAM_INVALID` | 注册参数错误 | 展示字段错误 |
| 400 / `AUTH_PASSWORD_POLICY_INVALID` | 密码不符合规则 | 展示密码规则 |
| 400 / `AUTH_PASSWORD_CONFIRM_NOT_MATCH` | 确认密码不一致 | 字段错误 |
| 400 / `AUTH_CAPTCHA_INVALID` | 验证码错误 | 重新验证 |
| 403 / `AUTH_REGISTER_DISABLED` | 注册关闭 | 提示注册暂未开放 |
| 409 / `AUTH_ACCOUNT_EXISTS` | 账号已存在 | 账号字段错误 |
| 409 / `AUTH_EMAIL_EXISTS` | 邮箱已存在 | 邮箱字段错误 |
| 429 / `AUTH_REGISTER_RATE_LIMITED` | 注册请求过于频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast 提交失败 |

## 15. 验收标准

- 注册页表单可提交到 `POST /api/auth/register`，不再直接无条件跳转登录。
- 账号、姓名、邮箱、部门、密码、确认密码均有前后端校验。
- 账号重复、邮箱重复、密码不符合规则、两次密码不一致等异常返回明确错误码。
- 注册成功后返回 `registrationId`、`accountStatus=pending`、`reviewStatus=pending`，前端提示等待管理员审核并跳转 `/login`。
- 管理员可在后台用户管理中审核注册申请并分配角色。
- 注册申请提交后通知管理员，审核结果可通过站内通知或邮件通知用户。
- 后端不返回密码、密码盐等敏感字段，密码必须哈希存储。
- 注册提交和审核行为均写入审计日志。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 是否开放自主注册，还是必须邀请码/管理员创建？ | 产品/后端 | 待确认 |
| Q2 | `account` 是否必须为研发工号？是否允许邮箱作为账号？ | 产品/后端 | 待确认 |
| Q3 | 部门是自由输入，还是必须从组织架构选择 `departmentId`？ | 前后端 | 待确认 |
| Q4 | 注册后是否必须管理员审核？是否存在自动通过规则？ | 产品/后端 | 待确认 |
| Q5 | 是否需要邮箱验证码、图形验证码或短信验证？ | 产品/安全/后端 | 待确认 |
| Q6 | 审核通过后默认角色如何确定：管理员手动分配，还是根据部门/邀请码自动分配？ | 产品/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的表单状态位置：`src/views/Register.vue` 的 `registerForm`。
- 当前页面中的 mock 行为：`handleSubmit` 直接 `router.push('/login')`，未调用注册接口。
- 当前页面没有 loading、字段错误、成功提示、验证码、邮箱验证、部门下拉、密码强度提示。
- 当前“返回登录”只做前端路由跳转 `/login`。
- 需要后端优先确认的字段：`account` 唯一规则、`department`/`departmentId` 口径、密码策略、注册审核状态。
- 需要后端优先确认的接口：`POST /api/auth/register`、注册配置接口、管理员审核接口。
