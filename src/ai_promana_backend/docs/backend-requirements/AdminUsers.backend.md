# 用户管理后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/admin/AdminUsers.vue`  
> 页面定位：后台用户管理页，覆盖用户列表、角色筛选、新增用户、批量导入、用户操作。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 用户管理 |
| 前端路由 | `/admin/users` |
| 前端文件 | `src/views/admin/AdminUsers.vue` |
| 所属模块 | 后台管理 / 用户管理 / 批量导入 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 后台管理员查看和管理系统用户。
- 支持按关键词和角色筛选用户列表。
- 支持新增单个用户，设置姓名、邮箱、部门、入职日期、角色、状态、备注。
- 支持下载导入模板、上传 Excel、解析预览、确认批量导入用户。
- 支持用户行级操作，如编辑、停用、激活。

### 2.2 对接范围

- 用户列表查询、关键词搜索、角色筛选、分页排序。
- 角色/部门/状态枚举选项。
- 新增用户提交。
- 用户编辑、停用、激活等行级操作。
- 用户导入模板下载、文件上传解析、预览、确认导入。
- 顶部当前用户和通知未读数。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `AdminHome.vue` | 后台首页可进入用户管理 |
| `AdminRoles.vue` | 用户角色枚举和权限来源 |
| `AdminLogs.vue` | 用户新增、停用、激活、导入写入审计日志 |
| `AdminSystem.vue` | 脱敏、通知、安全配置影响用户管理 |
| `Notifications.vue` | 用户邀请和激活提醒 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 可管理所有用户 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 不能操作超级管理员 |
| 项目负责人 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |
| 成员 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |

### 3.1 权限规则

- 页面入口权限：访问 `/admin/users` 需要 `admin:access` 和 `admin:user:read`。
- 按钮级权限：
  - “新增用户”需要 `admin:user:create`。
  - “批量导入”需要 `admin:user:import`。
  - “编辑”需要 `admin:user:update`。
  - “停用”需要 `admin:user:disable`。
  - “激活”需要 `admin:user:activate`。
- 数据范围权限：普通管理员只能管理所在组织或授权部门下用户；超级管理员全局。
- 敏感字段脱敏规则：邮箱、手机号、外部账号、最近登录 IP 按系统脱敏策略返回。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 静态为系统管理员 |
| 通知未读数 | 顶部角标 | 是 | `GET /api/notifications/unread-count` | 静态为 5 |
| 用户列表 | 表格主体 | 是 | `GET /api/admin/users` | 支持筛选分页 |
| 用户筛选选项 | 角色/部门/状态 | 是 | `GET /api/admin/users/options` | 首屏或弹窗复用 |
| 新增用户默认值 | 新增弹窗 | 否 | `GET /api/admin/users/create-options` | 打开弹窗时加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 表格加载中 | 请求处理中 | 列表/选项 |
| empty | “暂无匹配用户” | 无匹配用户 | 当前已有空行 |
| error | Toast/错误占位 | 接口异常 | 标准错误 |
| importing | 导入中 | 文件解析或导入处理中 | 禁用确认按钮 |
| saving | 新增/编辑/状态变更中 | 写操作处理中 | 防重复提交 |

## 5. 字段模型

### 5.1 用户字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 表格 key | `user-zhang` | 用户 ID |
| name | string | 是 | 用户名列 | `张工` | 用户姓名 |
| email | string | 是 | 邮箱列 | `zhang@example.com` | 登录邮箱 |
| departmentId | string | 否 | 部门 | `dept_rd` | 部门 ID |
| departmentName | string | 是 | 部门列 | `研发中心` | 部门名称 |
| roleKey | string | 是 | 角色筛选 | `user` | admin/user |
| roleLabel | string | 是 | 角色列 | `普通用户` | 角色名称 |
| status | string | 是 | 状态列 | `active` | active/pending/disabled |
| statusLabel | string | 是 | 状态文案 | `正常` | 展示文案 |
| statusType | string | 是 | 状态样式 | `success` | success/warning/danger |
| joinDate | string | 否 | 加入时间 | `2026-04-01` | 入职/加入日期 |
| actions | array | 是 | 操作按钮 | `[]` | 后端根据权限返回 |
| version | number | 否 | 编辑提交 | `1` | 乐观锁 |

### 5.2 新增用户表单字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | string | 是 | 姓名 | `赵经理` | 2-30 字 |
| email | string | 是 | 邮箱 | `zhao@example.com` | 唯一 |
| departmentId | string | 否 | 部门 | `dept_product` | 建议用 ID |
| departmentName | string | 否 | 部门输入 | `产品部` | 当前前端为文本 |
| joinDate | string | 否 | 加入日期 | `2026-04-28` | 日期 |
| roleKey | string | 是 | 角色 | `user` | admin/user |
| status | string | 是 | 初始状态 | `pending` | 默认待激活 |
| note | string | 否 | 备注 | `外部协作账号` | 最长 500 字 |
| sendInvite | boolean | 否 | 邀请通知 | `true` | 是否发送激活通知 |

### 5.3 批量导入字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| importTaskId | string | 是 | 导入预览 | `imp_001` | 上传解析任务 ID |
| fileName | string | 是 | 文件名 | `users.xlsx` | 上传文件 |
| totalCount | number | 是 | 预览统计 | `3` | 总行数 |
| validCount | number | 是 | 预览统计 | `3` | 可导入行数 |
| invalidCount | number | 是 | 预览统计 | `0` | 错误行数 |
| rows[].name | string | 是 | 预览表 | `赵经理` | 姓名 |
| rows[].email | string | 是 | 预览表 | `zhao@example.com` | 邮箱 |
| rows[].departmentName | string | 否 | 预览表 | `产品部` | 部门 |
| rows[].roleLabel | string | 是 | 预览表 | `普通用户` | 角色 |
| rows[].errors | string[] | 否 | 错误提示 | `[]` | 行级错误 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| roleKey | `admin` | 管理员 | neutral | 后台管理员 |
| roleKey | `user` | 普通用户 | neutral | 普通账号 |
| userStatus | `active` | 正常 | success | 可登录 |
| userStatus | `pending` | 待激活 | warning | 已创建未激活 |
| userStatus | `disabled` | 已停用 | danger | 不可登录 |
| userAction | `edit` | 编辑 | neutral | 编辑用户 |
| userAction | `disable` | 停用 | warning | 停用账号 |
| userAction | `activate` | 激活 | success | 激活账号 |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| total | number | 筛选后总数 | 分页 | 当前未展示分页 |
| activeCount | number | 正常用户数 | 可选统计 | 后续扩展 |
| pendingCount | number | 待激活用户数 | 可选统计 | 后续扩展 |
| adminCount | number | 管理员数量 | 可选统计 | 后续扩展 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取用户列表 | GET | `/api/admin/users` | 表格数据 | P0 |
| API-002 | 获取用户管理选项 | GET | `/api/admin/users/options` | 角色/部门/状态枚举 | P0 |
| API-003 | 新增用户 | POST | `/api/admin/users` | 新增用户弹窗 | P0 |
| API-004 | 更新用户 | PUT | `/api/admin/users/{userId}` | 编辑用户 | P1 |
| API-005 | 激活用户 | POST | `/api/admin/users/{userId}/activate` | 行级激活 | P0 |
| API-006 | 停用用户 | POST | `/api/admin/users/{userId}/disable` | 行级停用 | P0 |
| API-007 | 下载用户导入模板 | GET | `/api/admin/users/import-template` | 下载模板 | P1 |
| API-008 | 上传并解析导入文件 | POST | `/api/admin/users/import/preview` | Excel 预览 | P0 |
| API-009 | 确认批量导入用户 | POST | `/api/admin/users/import/confirm` | 批量入库 | P0 |
| API-010 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部角标 | P0 |

## 7. 接口详情

### API-001 获取用户列表

**请求方式**

- Method: `GET`
- Path: `/api/admin/users`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `张工` | 姓名/邮箱/部门 |
| roleKey | query | string | 否 | `admin` | 角色筛选 |
| status | query | string | 否 | `active` | 状态筛选 |
| page | query | number | 否 | `1` | 页码 |
| pageSize | query | number | 否 | `20` | 页大小 |
| sortBy | query | string | 否 | `joinDate` | 排序字段 |
| sortOrder | query | string | 否 | `desc` | asc/desc |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": "user-zhang",
        "name": "张工",
        "email": "zhang@example.com",
        "departmentId": "dept_rd",
        "departmentName": "研发中心",
        "roleKey": "user",
        "roleLabel": "普通用户",
        "status": "active",
        "statusLabel": "正常",
        "statusType": "success",
        "joinDate": "2026-04-01",
        "actions": [
          { "key": "edit", "label": "编辑", "enabled": true },
          { "key": "disable", "label": "停用", "enabled": true }
        ],
        "version": 1
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 3
    }
  }
}
```

### API-003 新增用户

**请求方式**

- Method: `POST`
- Path: `/api/admin/users`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | body | string | 是 | `赵经理` | 姓名 |
| email | body | string | 是 | `zhao@example.com` | 邮箱 |
| departmentId | body | string | 否 | `dept_product` | 部门 |
| roleKey | body | string | 是 | `user` | 角色 |
| status | body | string | 是 | `pending` | 初始状态 |
| joinDate | body | string | 否 | `2026-04-28` | 加入日期 |
| note | body | string | 否 | `外部协作` | 备注 |
| sendInvite | body | boolean | 否 | `true` | 发送邀请 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "user-zhao",
    "status": "pending",
    "inviteSent": true,
    "createdAt": "2026-05-11T15:20:00+08:00"
  }
}
```

### API-008 上传并解析导入文件

**请求方式**

- Method: `POST`
- Path: `/api/admin/users/import/preview`
- Auth: 是
- Content-Type: `multipart/form-data`

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| file | body | file | 是 | `users.xlsx` | Excel 文件 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "importTaskId": "imp_10001",
    "fileName": "users.xlsx",
    "totalCount": 3,
    "validCount": 3,
    "invalidCount": 0,
    "rows": [
      {
        "rowNo": 2,
        "name": "赵经理",
        "email": "zhao@example.com",
        "departmentName": "产品部",
        "roleKey": "user",
        "roleLabel": "普通用户",
        "errors": []
      }
    ]
  }
}
```

### API-009 确认批量导入用户

**请求方式**

- Method: `POST`
- Path: `/api/admin/users/import/confirm`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| importTaskId | body | string | 是 | `imp_10001` | 预览任务 |
| conflictStrategy | body | string | 否 | `skip` | skip/overwrite |
| sendInvite | body | boolean | 否 | `true` | 发送邀请 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "createdCount": 3,
    "updatedCount": 0,
    "skippedCount": 0,
    "failedCount": 0
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入用户管理 | 页面加载 | `GET /api/admin/users`、`GET /api/admin/users/options` | 当前用户 | 渲染列表 | 错误占位 |
| 顶部/表格搜索 | 搜索框 | `GET /api/admin/users` | keyword | 刷新列表 | Toast |
| 角色筛选 | chip | `GET /api/admin/users` | roleKey | 刷新列表 | Toast |
| 打开新增用户 | 新增按钮 | `GET /api/admin/users/options` | 当前用户 | 打开弹窗 | Toast |
| 提交新增用户 | 弹窗表单 | `POST /api/admin/users` | 表单 | Toast，刷新列表 | 表单错误 |
| 编辑用户 | 行操作 | `PUT /api/admin/users/{id}` | 用户 ID、表单 | Toast，刷新行 | 表单错误 |
| 停用用户 | 行操作 | `POST /api/admin/users/{id}/disable` | 用户 ID | Toast，刷新行 | Toast |
| 激活用户 | 行操作 | `POST /api/admin/users/{id}/activate` | 用户 ID | Toast，刷新行 | Toast |
| 下载模板 | 导入弹窗 | `GET /api/admin/users/import-template` | 无 | 下载文件 | Toast |
| 上传文件预览 | 上传区 | `POST /api/admin/users/import/preview` | file | 显示预览 | 行级错误 |
| 确认导入 | 导入弹窗 | `POST /api/admin/users/import/confirm` | importTaskId | Toast，刷新列表 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| name | input | 是 | 2-30 字 | 非空、长度合法 | 请输入姓名 |
| email | email input | 是 | 邮箱格式 | 唯一、域名策略 | 请输入有效邮箱 |
| departmentId | select/input | 否 | 部门存在 | 部门有效 | 部门无效 |
| joinDate | date/input | 否 | 日期格式 | 不晚于当前日期或按规则 | 加入时间无效 |
| roleKey | select | 是 | 角色枚举 | 当前管理员可分配 | 角色无权限 |
| status | select | 是 | 状态枚举 | 初始状态合法 | 状态无效 |
| note | textarea | 否 | 最长 500 字 | 长度合法 | 备注过长 |
| file | upload | 是 | xls/xlsx | 文件安全扫描、格式解析 | 请上传 Excel 文件 |

### 9.1 提交规则

- 是否允许重复提交：新增、导入确认、激活、停用期间不允许重复提交。
- 是否需要二次确认：停用用户、覆盖导入、赋予管理员角色需要二次确认。
- 是否需要审计日志：需要，新增、编辑、激活、停用、导入都记录。
- 是否需要乐观锁或版本号：编辑用户需要 `version`；新增不需要。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 姓名 | name | string | 是 | 支持搜索 |
| 邮箱 | email | string | 是 | 支持搜索、脱敏 |
| 部门 | departmentName | string | 是 | 支持搜索 |
| 角色 | roleLabel | string | 是 | 支持筛选 |
| 状态 | statusLabel | string | 是 | 支持筛选 |
| 加入时间 | joinDate | string | 是 | 日期排序 |
| 操作 | actions | array | 否 | 后端按权限返回 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 姓名、邮箱、部门、状态 |
| 角色 | roleKey | string | all | admin/user |
| 状态 | status | string | all | active/pending/disabled |
| 部门 | departmentId | string | 空 | 后续扩展 |

### 10.3 分页规则

- 分页参数：`page`、`pageSize`。
- 默认页大小：20。
- 最大页大小：100。
- 排序参数：`sortBy`、`sortOrder`，默认 `joinDate desc`。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 下载导入模板 | `GET /api/admin/users/import-template` | xlsx | 不适用 | 同步下载 | P1 |
| 上传导入文件 | `POST /api/admin/users/import/preview` | xls/xlsx | 建议 10MB | 上传并预览 | P0 |
| 确认导入 | `POST /api/admin/users/import/confirm` | 不适用 | 单次建议 5000 行 | 异步/同步 | P0 |
| 导出用户列表 | `GET /api/admin/users/export` | xlsx/csv | 不适用 | 异步任务 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知服务 | 新增用户、激活、导入结果 |
| 邮件/企微通知 | 可选 | 通知服务 | 邀请激活 |
| AI 建议 | 暂不必须 | AI 管理服务 | 可建议异常账号 |
| 审计日志 | 是 | 审计服务 | 用户管理操作必记 |
| WebSocket / SSE | 否 | 无 | 首期不需要 |

## 13. 缓存与实时性

- 数据是否允许缓存：用户列表不建议长缓存；选项可缓存 60 秒。
- 缓存时间：用户选项 60 秒。
- 页面返回时是否刷新：需要刷新用户列表和通知未读数。
- 是否需要轮询：不需要。
- 是否需要 WebSocket / SSE：首期不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `USER_VALIDATE_FAILED` | 用户字段错误 | 表单错误 |
| 400 / `USER_IMPORT_FILE_INVALID` | 文件格式错误 | 上传错误 |
| 400 / `USER_IMPORT_ROW_INVALID` | 导入行错误 | 预览行级错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `ADMIN_USER_FORBIDDEN` | 无用户管理权限 | 无权限提示 |
| 403 / `ROLE_ASSIGN_FORBIDDEN` | 无权分配角色 | 表单错误 |
| 404 / `USER_NOT_FOUND` | 用户不存在 | 刷新列表 |
| 409 / `USER_EMAIL_DUPLICATED` | 邮箱重复 | 表单错误 |
| 409 / `USER_VERSION_CONFLICT` | 编辑版本冲突 | 提示刷新 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 用户列表由接口返回，支持关键词、角色、状态筛选和分页。
- 新增用户弹窗可提交完整字段，邮箱重复、角色无权限、字段错误有明确提示。
- 行级编辑、激活、停用操作由后端返回可用 actions 控制。
- 导入模板可下载，Excel 上传后返回预览数据和行级错误。
- 确认导入后列表刷新，并返回新增、更新、跳过、失败数量。
- 用户管理所有写操作写入审计日志。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 当前新增用户部门是文本还是必须选择已有部门 ID？ | 产品/后端 | 待确认 |
| Q2 | 用户角色是否只有 admin/user，还是接入完整平台角色？ | 产品/权限 | 待确认 |
| Q3 | 批量导入遇到重复邮箱默认跳过、覆盖还是报错？ | 产品/后端 | 待确认 |
| Q4 | 新增用户后是否默认发送邮件/企微激活通知？ | 产品/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`users`、`importPreviewRows`、`filterOptions`、`createUserForm`。
- 当前页面中的 TODO/API 标记：用户列表、用户搜索、角色筛选、新增用户、批量导入、模板下载、当前用户、通知、AI 抽屉。
- 当前导入预览是前端本地模拟，未真实读取 Excel。
- 当前“编辑/停用/激活”只展示 Toast，未接接口。
- 需要后端优先确认的字段：用户角色枚举、用户状态枚举、部门模型、导入文件列。
- 需要后端优先确认的接口：`GET /api/admin/users`、`POST /api/admin/users`、`POST /api/admin/users/import/preview`、`POST /api/admin/users/import/confirm`。

