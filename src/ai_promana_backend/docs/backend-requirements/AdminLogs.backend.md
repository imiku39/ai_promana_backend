# 审计日志后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/admin/AdminLogs.vue`  
> 页面定位：后台审计日志列表页，覆盖日志检索、动作筛选、导出日志。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 审计日志 |
| 前端路由 | `/admin/logs` |
| 前端文件 | `src/views/admin/AdminLogs.vue` |
| 所属模块 | 后台管理 / 审计日志 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 为管理员提供后台敏感操作、删除记录、系统配置改动的审计查询。
- 支持顶部关键词和表格关键词检索。
- 支持按动作类型筛选，如全部动作、删除、配置。
- 支持导出当前筛选条件下的审计日志。

### 2.2 对接范围

- 审计日志列表查询、关键词检索、动作类型筛选、分页排序。
- 审计动作类型枚举。
- 审计日志导出，当前前端已预留 `exportEndpoint=/api/admin/logs/export`。
- 顶部当前用户、通知未读数。
- 导出文件名从 `Content-Disposition` 读取。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `AdminHome.vue` | 首页最近审计事件跳转完整日志 |
| `AdminUsers.vue` | 用户管理操作写入审计日志 |
| `AdminRoles.vue` | 角色模板和权限矩阵操作写入审计日志 |
| `AdminProjectTemplates.vue` | 项目模板操作写入审计日志 |
| `AdminSystem.vue` | 系统配置保存/恢复默认写入审计日志 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 否 | 否 | 否 | 是 | 可查看全局审计 |
| 管理员 | 是 | 否 | 否 | 否 | 视权限 | 仅授权范围 |
| 项目负责人 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |
| 成员 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |

### 3.1 权限规则

- 页面入口权限：访问 `/admin/logs` 需要 `admin:access` 和 `admin:audit-log:read`。
- 按钮级权限：“导出日志”需要 `admin:audit-log:export`。
- 数据范围权限：管理员只能查看授权组织/项目/模块范围内审计；超级管理员可全局。
- 敏感字段脱敏规则：IP、邮箱、手机号、请求参数中的密钥/Token/密码必须脱敏。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 静态为系统管理员 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 静态为 5 |
| 审计日志列表 | 表格主体 | 是 | `GET /api/admin/logs` | 当前静态 auditLogs |
| 动作类型枚举 | 筛选 chip | 是 | `GET /api/admin/logs/options` | 当前静态 filterOptions |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 表格加载中 | 请求处理中 | 列表/枚举 |
| empty | 空表格 | 无匹配日志 | 需补空态 |
| error | Toast/错误占位 | 接口异常 | 标准错误 |
| exporting | 导出按钮禁用 | 导出请求处理中 | 当前已有 `isExporting` |

## 5. 字段模型

### 5.1 审计日志字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string | 是 | 表格 key | `log-20260426-1043` | 审计 ID |
| time | string | 是 | 时间列 | `2026-04-26 10:43` | 展示时间 |
| occurredAt | string | 是 | 排序字段 | `2026-04-26T10:43:00+08:00` | ISO 时间 |
| operatorId | string | 否 | 隐含字段 | `u_admin` | 操作者 ID |
| operator | string | 是 | 操作者列 | `系统管理员` | 操作者名称 |
| action | string | 是 | 动作列 | `删除模板` | 动作文案 |
| actionKey | string | 是 | 筛选/详情 | `delete_template` | 动作 key |
| target | string | 是 | 对象列 | `临时排障模板` | 操作对象 |
| targetType | string | 否 | 详情 | `project_template` | 对象类型 |
| targetId | string | 否 | 详情 | `tpl_001` | 对象 ID |
| result | string | 是 | 结果列 | `成功` | 展示文案 |
| resultStatus | string | 是 | 结果样式 | `success` | success/failure |
| type | string | 是 | 动作筛选 | `delete` | delete/config/other |
| ip | string | 否 | 详情 | `192.168.*.*` | 脱敏 IP |
| requestId | string | 否 | 排查 | `req_001` | 请求链路 |

### 5.2 导出字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | string | 否 | 导出参数 | `系统` | 表格关键词 |
| globalKeyword | string | 否 | 导出参数 | `权限` | 顶部关键词 |
| type | string | 否 | 导出参数 | `config` | 当前动作筛选 |
| startTime | string | 否 | 后续扩展 | `2026-04-01T00:00:00+08:00` | 开始时间 |
| endTime | string | 否 | 后续扩展 | `2026-04-30T23:59:59+08:00` | 结束时间 |

### 5.3 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| logType | `all` | 全部动作 | active chip | 前端筛选 |
| logType | `delete` | 删除 | danger | 删除操作 |
| logType | `config` | 配置 | warning | 配置/权限变更 |
| logType | `other` | 其他 | neutral | 登录/导出等 |
| resultStatus | `success` | 成功 | success | 操作成功 |
| resultStatus | `failure` | 失败 | danger | 操作失败 |

### 5.4 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| total | number | 当前筛选日志总数 | 分页 | 当前未展示 |
| failedCount | number | 筛选范围失败日志数 | 后续扩展 | 可用于告警 |
| highRiskCount | number | 高风险动作数量 | 后续扩展 | 可用于首页 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取审计日志列表 | GET | `/api/admin/logs` | 表格数据 | P0 |
| API-002 | 获取审计日志选项 | GET | `/api/admin/logs/options` | 动作类型枚举 | P0 |
| API-003 | 获取审计日志详情 | GET | `/api/admin/logs/{logId}` | 详情扩展 | P1 |
| API-004 | 导出审计日志 | GET | `/api/admin/logs/export` | 文件下载 | P0 |
| API-005 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部角标 | P0 |

## 7. 接口详情

### API-001 获取审计日志列表

**请求方式**

- Method: `GET`
- Path: `/api/admin/logs`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `系统管理员` | 操作者/动作/对象/结果 |
| globalKeyword | query | string | 否 | `权限` | 顶部搜索 |
| type | query | string | 否 | `config` | 动作类型 |
| startTime | query | string | 否 | `2026-04-01T00:00:00+08:00` | 开始时间 |
| endTime | query | string | 否 | `2026-04-30T23:59:59+08:00` | 结束时间 |
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
        "id": "log-20260426-1043",
        "time": "2026-04-26 10:43",
        "occurredAt": "2026-04-26T10:43:00+08:00",
        "operatorId": "u_admin",
        "operator": "系统管理员",
        "action": "删除模板",
        "actionKey": "delete_template",
        "target": "临时排障模板",
        "targetType": "project_template",
        "targetId": "tpl_temp",
        "result": "成功",
        "resultStatus": "success",
        "type": "delete"
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 5
    }
  }
}
```

### API-004 导出审计日志

**请求方式**

- Method: `GET`
- Path: `/api/admin/logs/export`
- Auth: 是
- Accept: `application/octet-stream`

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `删除` | 表格关键词 |
| globalKeyword | query | string | 否 | `权限` | 顶部关键词 |
| type | query | string | 否 | `delete` | 动作类型 |
| startTime | query | string | 否 | `2026-04-01T00:00:00+08:00` | 开始时间 |
| endTime | query | string | 否 | `2026-04-30T23:59:59+08:00` | 结束时间 |

**响应数据**

- 成功：返回文件流，响应头包含 `Content-Disposition`，建议文件名 `audit-logs-YYYY-MM-DD.xlsx`。
- 失败：返回标准 JSON 错误结构。

**异常情况**

| 场景 | 后端返回 | 前端处理 |
| --- | --- | --- |
| 无导出权限 | `403 AUDIT_LOG_EXPORT_FORBIDDEN` | Toast |
| 查询范围过大 | `400 AUDIT_LOG_EXPORT_RANGE_TOO_LARGE` | 提示缩小时间范围 |
| 文件生成失败 | `500 AUDIT_LOG_EXPORT_FAILED` | Toast |

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入审计日志 | 页面加载 | `GET /api/admin/logs`、`GET /api/admin/logs/options` | 当前用户 | 渲染表格 | 错误占位 |
| 顶部搜索 | topbar | `GET /api/admin/logs` | globalKeyword | 刷新表格 | Toast |
| 表格搜索 | toolbar | `GET /api/admin/logs` | keyword | 刷新表格 | Toast |
| 动作筛选 | chip | `GET /api/admin/logs` | type | 刷新表格 | Toast |
| 导出日志 | 侧边栏按钮 | `GET /api/admin/logs/export` | 当前筛选条件 | 下载文件 | Toast/alert |
| 打开通知中心 | 顶部图标 | `GET /api/notifications/unread-count`/路由 | 当前用户 | 跳转 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| keyword | input | 否 | 最长 100 字 | 长度合法、转义 | 关键词过长 |
| globalKeyword | input | 否 | 最长 100 字 | 长度合法、转义 | 关键词过长 |
| type | chip/select | 否 | 枚举 | 动作类型合法 | 动作类型无效 |
| startTime | date | 否 | 日期格式 | 范围合法 | 开始时间无效 |
| endTime | date | 否 | 日期格式 | 晚于开始时间 | 结束时间无效 |

### 9.1 提交规则

- 是否允许重复提交：导出处理中不允许重复点击。
- 是否需要二次确认：导出大范围日志建议二次确认。
- 是否需要审计日志：需要，审计日志导出本身也需要写审计。
- 是否需要乐观锁或版本号：不需要。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 时间 | occurredAt/time | string | 是 | 默认倒序 |
| 操作者 | operator | string | 是 | 支持搜索 |
| 动作 | action | string | 是 | 支持搜索/筛选 |
| 对象 | target | string | 否 | 支持搜索 |
| 结果 | resultStatus | string | 是 | success/failure |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 表格关键词 | keyword | string | 空 | 操作者、动作、对象、结果 |
| 顶部关键词 | globalKeyword | string | 空 | 全局搜索输入 |
| 动作类型 | type | string | all | delete/config/other |
| 开始时间 | startTime | string | 空 | 后续扩展 |
| 结束时间 | endTime | string | 空 | 后续扩展 |

### 10.3 分页规则

- 分页参数：`page`、`pageSize`。
- 默认页大小：20。
- 最大页大小：100。
- 排序参数：`sortBy=occurredAt`、`sortOrder=desc`。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出审计日志 | `GET /api/admin/logs/export` | xlsx/csv | 建议限制行数 | 同步下载或异步任务 | 当前前端支持 blob 下载 |
| 导出审计详情 | `GET /api/admin/logs/{id}/export` | json/pdf | 不适用 | 同步下载 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知服务 | 异常审计告警 |
| AI 建议 | 可选 | AI 风险分析 | 后续可做异常日志分析 |
| 审计日志 | 是 | 审计服务 | 页面核心能力 |
| WebSocket / SSE | 可选 | 审计事件流 | 后续实时告警 |

## 13. 缓存与实时性

- 数据是否允许缓存：审计日志不建议缓存；枚举可缓存 5 分钟。
- 缓存时间：动作类型枚举 5 分钟。
- 页面返回时是否刷新：需要刷新。
- 是否需要轮询：首期不需要。
- 是否需要 WebSocket / SSE：实时审计告警可后续接入。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `AUDIT_LOG_PARAM_INVALID` | 查询参数错误 | Toast |
| 400 / `AUDIT_LOG_EXPORT_RANGE_TOO_LARGE` | 导出范围过大 | 提示缩小范围 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `AUDIT_LOG_FORBIDDEN` | 无查看权限 | 无权限提示 |
| 403 / `AUDIT_LOG_EXPORT_FORBIDDEN` | 无导出权限 | Toast |
| 404 / `AUDIT_LOG_NOT_FOUND` | 日志不存在 | 刷新列表 |
| 500 / `AUDIT_LOG_EXPORT_FAILED` | 导出失败 | Toast |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 审计日志列表由接口返回，支持关键词、动作类型筛选、分页、按时间倒序。
- 后端返回字段可直接渲染时间、操作者、动作、对象、结果。
- 导出接口支持当前筛选条件，并返回可下载文件流。
- 导出失败、无权限、范围过大有明确错误码。
- 敏感字段按系统配置脱敏。
- 用户、角色、项目模板、系统配置等后台操作均可在日志中查询。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 审计日志导出最大允许多少行？ | 后端/安全 | 待确认 |
| Q2 | 是否需要审计详情弹窗展示请求参数差异？ | 产品/后端 | 待确认 |
| Q3 | 动作类型枚举是否只分 delete/config/other，还是按模块细分？ | 产品/后端 | 待确认 |
| Q4 | 导出审计日志是否必须异步任务？ | 后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`auditLogs`、`filterOptions`。
- 当前页面中的 TODO/API 标记：导出日志、全局搜索、日志关键词检索、动作类型枚举、审计日志列表、当前用户、通知、AI 抽屉。
- 当前导出功能已使用 `fetch` 请求 `exportEndpoint`，默认 `/api/admin/logs/export`，并支持 blob 下载。
- 当前搜索和筛选仍是前端本地 computed：`filteredLogs`。
- 需要后端优先确认的字段：`type`、`resultStatus`、`actionKey`、导出文件名。
- 需要后端优先确认的接口：`GET /api/admin/logs`、`GET /api/admin/logs/options`、`GET /api/admin/logs/export`。

