# 登录页后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/Login.vue`

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 登录页 |
| 前端路由 | `/login` |
| 前端文件 | `src/views/Login.vue` |
| 所属模块 | 认证与账号体系 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-10 |
| 更新日期 | 2026-05-10 |

## 2. 页面目标

### 2.1 页面用途

- 支持研发协作系统用户通过账号密码登录平台。
- 登录成功后写入认证凭据和当前用户角色，跳转到 `/dashboard`。
- 支持“记住我”登录时长策略。
- 预留第三方登录入口，目前前端展示为指纹登录和扫码登录按钮。
- 支持跳转注册页 `/register`，注册流程由注册页需求文档单独描述。

### 2.2 对接范围

- 账号密码登录接口。
- 登录成功后的 token、用户信息、角色、权限返回结构。
- 当前登录用户信息查询接口，供顶部用户卡片和权限路由复用。
- 退出登录接口，供其他页面清理会话时调用。
- 第三方登录发起与回调确认接口，当前可作为 P1 能力。
- 登录失败、账号锁定、禁用、待审核等异常状态。
- 登录审计日志与安全风控规则。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `Register.vue` | 登录页点击“还没有账户？去注册”跳转注册页 |
| `Dashboard.vue` | 登录成功默认跳转工作台 |
| `UserProfileHoverCard.vue` | 退出登录、当前用户信息展示依赖认证状态 |
| `router/index.js` | 后续需要基于 token、role、permissions 做路由守卫 |

## 3. 角色与权限

| 角色 | 可查看登录页 | 可登录 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 未登录用户 | 是 | 是 | 否 | 否 | 否 | 登录页公开可访问 |
| 超级管理员 | 是 | 是 | 否 | 否 | 否 | 登录成功后可进入后台管理 |
| 管理员 | 是 | 是 | 否 | 否 | 否 | 登录成功后按权限进入系统 |
| 项目负责人 | 是 | 是 | 否 | 否 | 否 | 登录成功后进入业务页面 |
| 成员 | 是 | 是 | 否 | 否 | 否 | 登录成功后进入业务页面 |

### 3.1 权限规则

- 页面入口权限：`/login` 不需要 token；如果已登录访问 `/login`，前端可根据 `/api/auth/me` 或本地 token 跳转到 `/dashboard`。
- 登录接口权限：不需要登录态，但需要频率限制和安全校验。
- 按钮级权限：登录页本身无按钮级权限控制。
- 数据范围权限：登录成功后返回用户角色、权限列表、数据范围，后续页面按权限渲染。
- 敏感字段脱敏规则：后端不得返回密码、密码盐、密保答案等敏感信息。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 登录表单 | 用户输入账号密码 | 是 | 前端本地状态 | `username`、`password`、`rememberMe` |
| 认证状态 | 判断是否已登录 | 否 | `GET /api/auth/me` | 可用于已登录用户访问登录页时自动跳转 |
| 第三方登录配置 | 控制第三方入口是否展示 | 否 | `GET /api/auth/providers` | 当前前端静态展示两个图标，后续可改为后端配置 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| idle | 表单可输入 | 未发起请求 | 默认状态 |
| loading | 登录按钮 loading / 禁用重复提交 | 登录请求处理中 | 后续前端接接口时补充 |
| success | 跳转 `/dashboard` | 登录成功 | 写入 token、role、user |
| invalid | 表单错误提示 | 参数缺失或格式错误 | 例如账号为空、密码为空 |
| error | Toast 或表单错误 | 账号密码错误、账号禁用、服务异常 | 需要明确错误码 |

## 5. 字段模型

### 5.1 登录请求字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| username | string | 是 | 用户名输入框 | `RD0001` | 研发工号、账号或邮箱，具体口径待后端确认 |
| password | string | 是 | 密码输入框 | `******` | 明文经 HTTPS 传输，后端做密码校验 |
| rememberMe | boolean | 否 | 记住我复选框 | `true` | 控制登录态有效期 |
| loginType | string | 否 | 隐含字段 | `password` | 默认为账号密码登录 |

### 5.2 登录响应用户字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| accessToken | string | 是 | 本地认证凭据 | `eyJ...` | API 请求使用，建议 JWT 或不透明 token |
| refreshToken | string | 建议 | 本地认证凭据 | `rf_...` | 用于刷新 accessToken |
| expiresIn | number | 是 | 认证逻辑 | `7200` | accessToken 有效秒数 |
| tokenType | string | 是 | 认证逻辑 | `Bearer` | 请求头使用 |
| user.id | string | 是 | 当前用户 | `u_10001` | 用户唯一标识 |
| user.username | string | 是 | 当前用户 | `RD0001` | 登录账号 |
| user.name | string | 是 | 用户卡片 | `王志强` | 用户姓名 |
| user.avatar | string | 否 | 用户卡片 | `https://...` | 头像 URL |
| user.department | string | 否 | 用户卡片 | `材料科学部` | 部门 |
| user.role | string | 是 | 权限判断 | `super_admin` | 当前主角色 |
| user.roleName | string | 是 | 展示 | `超级管理员` | 角色中文名 |
| permissions | string[] | 是 | 路由/按钮权限 | `["admin:access"]` | 权限码列表 |
| redirectPath | string | 否 | 登录后跳转 | `/dashboard` | 后端可按角色建议默认首页 |

### 5.3 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| role | `super_admin` | 超级管理员 | 无 | 当前前端 mock 默认值 |
| role | `admin` | 管理员 | 无 | 可访问后台管理 |
| role | `pm` | 项目负责人 | 无 | 项目管理角色 |
| role | `developer` | 研发 | 无 | 研发成员 |
| role | `qa` | 测试 | 无 | QA 成员 |
| role | `product` | 产品 | 无 | 产品成员 |
| role | `collaborator` | 协作者 | 无 | 外部或协同成员 |
| accountStatus | `active` | 正常 | 成功 | 允许登录 |
| accountStatus | `disabled` | 已禁用 | 错误 | 不允许登录 |
| accountStatus | `locked` | 已锁定 | 警告 | 失败次数过多 |
| accountStatus | `pending` | 待审核 | 警告 | 注册后未审核 |

### 5.4 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| failedAttempts | number | 当前账号连续失败次数 | 登录失败提示 | 可选返回 |
| lockedUntil | string | 锁定截止时间 | 登录失败提示 | ISO 时间字符串 |
| lastLoginAt | string | 上次登录时间 | 后续用户卡片/审计 | 可选返回 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 账号密码登录 | POST | `/api/auth/login` | 登录页核心提交 | P0 |
| API-002 | 获取当前登录用户 | GET | `/api/auth/me` | 登录态校验与用户信息获取 | P0 |
| API-003 | 刷新 Token | POST | `/api/auth/refresh` | 延长会话 | P0 |
| API-004 | 退出登录 | POST | `/api/auth/logout` | 清理服务端会话 | P0 |
| API-005 | 获取第三方登录方式 | GET | `/api/auth/providers` | 控制第三方登录入口 | P1 |
| API-006 | 发起第三方登录 | POST | `/api/auth/social/start` | 指纹/扫码登录发起 | P1 |
| API-007 | 确认第三方登录 | POST | `/api/auth/social/confirm` | 扫码或外部认证回调确认 | P1 |

## 7. 接口详情

### API-001 账号密码登录

**请求方式**

- Method: `POST`
- Path: `/api/auth/login`
- Auth: 否

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| username | body | string | 是 | `RD0001` | 研发工号、账号或邮箱 |
| password | body | string | 是 | `Password@123` | 密码 |
| rememberMe | body | boolean | 否 | `true` | 是否延长登录有效期 |
| deviceId | body | string | 否 | `web-uuid` | 浏览器设备标识，后续会话管理使用 |
| clientType | body | string | 否 | `web` | 客户端类型 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "accessToken": "eyJhbGciOi...",
    "refreshToken": "rf_9f8e7d",
    "expiresIn": 7200,
    "tokenType": "Bearer",
    "user": {
      "id": "u_10001",
      "username": "RD0001",
      "name": "王志强",
      "avatar": "https://example.com/avatar/u_10001.png",
      "department": "材料科学部",
      "role": "super_admin",
      "roleName": "超级管理员",
      "accountStatus": "active"
    },
    "permissions": ["admin:access", "project:read", "project:write"],
    "redirectPath": "/dashboard"
  }
}
```

**响应字段说明**

| 字段名 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| accessToken | string | 是 | `eyJ...` | 前端保存后作为接口认证凭据 |
| refreshToken | string | 建议 | `rf_...` | 用于刷新 token |
| expiresIn | number | 是 | `7200` | accessToken 有效秒数 |
| tokenType | string | 是 | `Bearer` | 请求头类型 |
| user | object | 是 | `{}` | 当前用户基础信息 |
| user.role | string | 是 | `super_admin` | 替换当前前端 mock 的 `userRole` |
| permissions | string[] | 是 | `["admin:access"]` | 前端路由和按钮权限使用 |
| redirectPath | string | 否 | `/dashboard` | 登录成功后跳转路径 |

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 参数缺失 | `400 AUTH_PARAM_INVALID` | 表单字段错误提示 |
| 账号或密码错误 | `401 AUTH_BAD_CREDENTIALS` | 提示账号或密码错误 |
| 账号已禁用 | `403 AUTH_ACCOUNT_DISABLED` | 提示联系管理员 |
| 账号待审核 | `403 AUTH_ACCOUNT_PENDING` | 提示等待管理员审核 |
| 账号锁定 | `423 AUTH_ACCOUNT_LOCKED` | 提示锁定截止时间 |
| 频率过高 | `429 AUTH_TOO_MANY_ATTEMPTS` | 提示稍后重试 |
| 服务异常 | `500 COMMON_SERVER_ERROR` | Toast 提示登录失败 |

### API-002 获取当前登录用户

**请求方式**

- Method: `GET`
- Path: `/api/auth/me`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| Authorization | header | string | 是 | `Bearer eyJ...` | accessToken |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "u_10001",
    "username": "RD0001",
    "name": "王志强",
    "avatar": "https://example.com/avatar/u_10001.png",
    "department": "材料科学部",
    "role": "super_admin",
    "roleName": "超级管理员",
    "permissions": ["admin:access", "project:read", "project:write"]
  }
}
```

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| token 缺失 | `401 AUTH_TOKEN_MISSING` | 清理本地状态并跳转登录 |
| token 过期 | `401 AUTH_TOKEN_EXPIRED` | 尝试刷新 token，失败后跳转登录 |
| token 无效 | `401 AUTH_TOKEN_INVALID` | 清理本地状态并跳转登录 |

### API-003 刷新 Token

**请求方式**

- Method: `POST`
- Path: `/api/auth/refresh`
- Auth: 否，使用 refreshToken

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| refreshToken | body | string | 是 | `rf_9f8e7d` | 登录响应返回 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "accessToken": "eyJhbGciOi...",
    "refreshToken": "rf_new",
    "expiresIn": 7200,
    "tokenType": "Bearer"
  }
}
```

### API-004 退出登录

**请求方式**

- Method: `POST`
- Path: `/api/auth/logout`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| refreshToken | body | string | 否 | `rf_9f8e7d` | 用于服务端失效当前会话 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": true
}
```

### API-005 获取第三方登录方式

**请求方式**

- Method: `GET`
- Path: `/api/auth/providers`
- Auth: 否

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "provider": "fingerprint",
      "name": "指纹登录",
      "enabled": true
    },
    {
      "provider": "qr_code_scanner",
      "name": "扫码登录",
      "enabled": true
    }
  ]
}
```

### API-006 发起第三方登录

**请求方式**

- Method: `POST`
- Path: `/api/auth/social/start`
- Auth: 否

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| provider | body | string | 是 | `qr_code_scanner` | 第三方登录方式 |
| redirectUri | body | string | 否 | `https://app.example.com/login/callback` | 回调地址 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "provider": "qr_code_scanner",
    "authUrl": "https://sso.example.com/authorize?...",
    "qrCodeUrl": "https://example.com/qrcode/session_123.png",
    "sessionId": "session_123",
    "expiresIn": 180
  }
}
```

### API-007 确认第三方登录

**请求方式**

- Method: `POST`
- Path: `/api/auth/social/confirm`
- Auth: 否

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| provider | body | string | 是 | `qr_code_scanner` | 第三方登录方式 |
| code | body | string | 否 | `oauth_code` | 外部回调授权码 |
| sessionId | body | string | 否 | `session_123` | 扫码会话 ID |

**响应数据**

同 API-001 登录成功响应结构。

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 输入账号 | 用户名输入框 | 无 | `loginForm.username` | 本地更新 | 前端校验提示 |
| 输入密码 | 密码输入框 | 无 | `loginForm.password` | 本地更新 | 前端校验提示 |
| 勾选记住我 | 记住我复选框 | 无 | `loginForm.rememberMe` | 本地更新 | 无 |
| 点击立即登录 | 登录按钮 | `POST /api/auth/login` | 表单 | 保存 token、角色、用户信息，跳转 `/dashboard` | 展示错误提示 |
| 点击注册入口 | “还没有账户？去注册” | 无 | 无 | 跳转 `/register` | 无 |
| 点击指纹登录 | 第三方图标按钮 | `POST /api/auth/social/start` | `provider=fingerprint` | 发起外部认证 | 展示失败提示 |
| 点击扫码登录 | 第三方图标按钮 | `POST /api/auth/social/start` | `provider=qr_code_scanner` | 展示二维码或跳转认证页 | 展示失败提示 |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| username | input text | 是 | 非空，长度 2-64 | 账号存在性、状态检查 | 请输入研发工号 |
| password | input password | 是 | 非空，长度 6-128 | 密码哈希校验 | 请输入安全密码 |
| rememberMe | checkbox | 否 | boolean | 控制 token 有效期 | 无 |

### 9.1 提交规则

- 是否允许重复提交：不允许，登录请求期间前端禁用登录按钮。
- 是否需要二次确认：不需要。
- 是否需要审计日志：需要，成功和失败都应记录登录审计日志。
- 是否需要验证码：当前 UI 未展示，后端可在连续失败后返回 `captchaRequired=true`，后续前端再补验证码控件。
- 是否需要乐观锁或版本号：不需要。

## 10. 列表、筛选、分页与排序

登录页无列表、筛选、分页、排序能力。

## 11. 文件、导入、导出

登录页无文件上传、导入、导出能力。

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 否 | 无 | 登录页不展示通知 |
| AI 建议 | 否 | 无 | 登录页不需要 AI 能力 |
| 审计日志 | 是 | 审计日志服务 | 记录登录成功、失败、退出、token 刷新异常 |
| WebSocket / SSE | 否 | 无 | 登录页不需要实时连接 |
| 第三方登录 | 是 | SSO / OAuth / 企业扫码服务 | 当前两个图标预留入口 |

## 13. 缓存与实时性

- 数据是否允许缓存：用户认证信息可存储在 localStorage 或更安全的 Cookie 中，具体由安全方案确认。
- 缓存时间：`rememberMe=false` 建议短会话，例如 2 小时；`rememberMe=true` 可延长，例如 7 天或 30 天，待安全策略确认。
- 页面返回时是否刷新：访问 `/login` 时如已有有效 token，可调用 `/api/auth/me` 校验并跳转。
- 是否需要轮询：第三方扫码登录可选择短轮询或 WebSocket，当前建议先用短轮询确认扫码状态。
- 是否需要 WebSocket / SSE：账号密码登录不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 保存认证信息并跳转 |
| 400 / `AUTH_PARAM_INVALID` | 参数错误 | 展示字段错误 |
| 401 / `AUTH_BAD_CREDENTIALS` | 账号或密码错误 | 展示登录失败提示 |
| 401 / `AUTH_TOKEN_EXPIRED` | token 过期 | 尝试刷新，失败后跳转登录 |
| 403 / `AUTH_ACCOUNT_DISABLED` | 账号禁用 | 提示联系管理员 |
| 403 / `AUTH_ACCOUNT_PENDING` | 账号待审核 | 提示等待审核 |
| 423 / `AUTH_ACCOUNT_LOCKED` | 账号锁定 | 展示锁定截止时间 |
| 429 / `AUTH_TOO_MANY_ATTEMPTS` | 请求过于频繁 | 禁用短时间重试并提示 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | 展示登录失败提示 |

## 15. 验收标准

- 输入正确账号密码后，后端返回 token、用户信息、角色和权限，前端可跳转 `/dashboard`。
- 当前前端 `localStorage.setItem('token', 'mock-token')` 和 `localStorage.setItem('userRole', 'super_admin')` 可替换为真实接口返回值。
- 输入错误密码、禁用账号、待审核账号、锁定账号时，后端返回明确错误码和可展示文案。
- `rememberMe` 能影响 token 或 refreshToken 的有效期。
- `/api/auth/me` 可用于刷新页面后的登录态恢复。
- `/api/auth/logout` 可用于退出登录时清理服务端会话。
- 所有登录成功、失败、退出行为均写入审计日志。
- 后端不返回密码、密码盐等敏感字段。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | `username` 具体支持研发工号、邮箱、手机号中的哪些登录标识？ | 后端 | 待确认 |
| Q2 | token 存储方案使用 localStorage、sessionStorage 还是 HttpOnly Cookie？ | 前后端 | 待确认 |
| Q3 | `rememberMe=true` 的有效期是多少？ | 后端/安全 | 待确认 |
| Q4 | 第三方登录具体接入企微、钉钉、企业 SSO 还是浏览器生物识别？ | 产品/后端 | 待确认 |
| Q5 | 连续登录失败后是否强制验证码？验证码 UI 是否需要本期补充？ | 产品/后端 | 待确认 |
| Q6 | 登录成功后默认跳转路径由前端固定 `/dashboard`，还是由后端 `redirectPath` 决定？ | 前后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`src/views/Login.vue` 的 `handleSubmit`。
- 当前 mock 行为：写入 `token=mock-token`、`userRole=super_admin`，然后 `router.push('/dashboard')`。
- 当前第三方登录行为：`handleSocialLogin(provider)` 仅 `console.log`，未接真实接口。
- 当前页面没有 loading、错误提示、验证码、忘记密码入口，后续接入接口时建议补充对应 UI 状态。
- 当前路由守卫读取 `localStorage.getItem('userRole')` 判断后台权限，后续应改为基于登录响应中的 `permissions` 或 `/api/auth/me`。
