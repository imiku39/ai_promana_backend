# 后台管理首页后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/admin/AdminHome.vue`  
> 页面定位：后台管理总览页，聚合账号、角色、配置风险、审计事件、权限矩阵和 AI 管理建议。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 后台管理首页 |
| 前端路由 | `/admin` |
| 前端文件 | `src/views/admin/AdminHome.vue` |
| 所属模块 | 后台管理 / 管理总览 / 权限矩阵 / 角色模板 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 为管理员提供后台管理总览，包括活跃账号、角色模板变更申请、异常审计事件、AI 推荐规则采纳率。
- 展示角色使用分布、系统配置变更风险、最近审计事件。
- 支持查看权限矩阵弹窗、导出权限矩阵。
- 支持新建角色模板弹窗、保存模板、另存为模板。
- 支持后台上下文 AI 管理建议和 AI 权限策略草稿。

### 2.2 对接范围

- 后台总览统计与趋势数据。
- 角色使用分布与配置变更风险数据。
- 最近审计事件列表。
- 平台角色矩阵、项目角色矩阵、矩阵导出。
- 角色模板基础选项、新建模板、另存为模板。
- AI 管理建议、AI 权限策略应用/稍后处理。
- 顶部当前用户、通知未读数和全局搜索。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `AdminUsers.vue` | 管理用户、账号状态和角色 |
| `AdminRoles.vue` | 完整管理角色矩阵和角色模板 |
| `AdminProjectTemplates.vue` | 管理项目模板 |
| `AdminLogs.vue` | 查看审计日志详情 |
| `AdminSystem.vue` | 保存系统配置和通知/安全策略 |
| `Notifications.vue` | 顶部通知入口 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 可管理全部后台能力 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 受权限策略限制 |
| 项目负责人 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |
| 成员 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |

### 3.1 权限规则

- 页面入口权限：访问 `/admin` 需要登录态和 `admin:access`。
- 按钮级权限：
  - “查看权限矩阵”需要 `admin:permission-matrix:read`。
  - “导出矩阵”需要 `admin:permission-matrix:export`。
  - “新增角色模板”“保存模板”“另存为”需要 `admin:role-template:create`。
  - “应用 AI 建议”“应用策略”需要 `admin:ai-policy:apply`。
- 数据范围权限：管理员只可查看自己管理域下的账号、角色、审计事件；超级管理员可查看全局。
- 敏感字段脱敏规则：审计事件中的账号、邮箱、IP、Token、密钥等敏感字段需按系统配置脱敏。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 当前静态为系统管理员 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 当前静态为 5 |
| 后台总览 | 指标卡、图表、审计摘要 | 是 | `GET /api/admin/overview` | 首屏核心接口 |
| 权限矩阵 | 权限矩阵弹窗 | 否 | `GET /api/admin/permission-matrix` | 打开弹窗时加载 |
| 角色模板选项 | 新建模板弹窗 | 否 | `GET /api/admin/role-templates/options` | 打开弹窗时加载 |
| AI 管理建议 | 首页 AI 卡片和抽屉 | 否 | `GET /api/admin/ai-suggestions` | 可延迟加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 页面骨架/加载中 | 请求处理中 | 首屏、矩阵、模板选项 |
| empty | 空状态 | 无审计事件或无建议 | 分区块展示 |
| error | Toast / 错误占位 | 接口异常或无权限 | 标准错误结构 |
| exporting | 导出中 | 异步导出任务创建中 | 禁用导出按钮 |
| saving | 保存中 | 模板创建或另存处理中 | 防重复提交 |

## 5. 字段模型

### 5.1 后台总览字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| metrics[].key | string | 是 | 指标卡 | `activeAccounts` | 指标唯一标识 |
| metrics[].label | string | 是 | 指标卡 | `活跃账号数` | 指标名称 |
| metrics[].value | string/number | 是 | 指标卡 | `1284` | 指标值 |
| metrics[].status | string | 是 | 指标卡标签 | `正常` | 状态文案 |
| metrics[].statusType | string | 是 | 指标卡样式 | `success` | success/warning/danger/ai |
| roleUsage[].roleKey | string | 是 | 角色使用分布 | `pm` | 角色 key |
| roleUsage[].roleName | string | 是 | 角色使用分布 | `PM` | 角色名称 |
| roleUsage[].usageRate | number | 是 | 柱状高度 | `88` | 0-100 |
| configRisks[].label | string | 是 | 配置变更风险 | `权限变更操作` | 配置项名称 |
| configRisks[].riskLevel | string | 是 | 风险等级 | `high` | low/medium/high |
| configRisks[].riskRate | number | 是 | 条形宽度 | `84` | 0-100 |
| recentAudits[].id | string | 是 | 最近审计事件 | `audit_001` | 审计 ID |
| recentAudits[].title | string | 是 | 最近审计事件 | `修改系统配置` | 标题 |
| recentAudits[].description | string | 是 | 最近审计事件 | `管理员李工...` | 描述 |
| recentAudits[].occurredAt | string | 是 | 最近审计事件 | `2026-05-11T10:43:00+08:00` | 时间 |

### 5.2 权限矩阵字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| matrixType | string | 是 | 矩阵分区 | `platform` | platform/project |
| columns[].key | string | 是 | 表头 | `adminAccess` | 权限项 key |
| columns[].label | string | 是 | 表头 | `后台入口` | 权限项名称 |
| rows[].roleKey | string | 是 | 行 key | `super_admin` | 角色 key |
| rows[].roleName | string | 是 | 行标题 | `超级管理员` | 角色名称 |
| rows[].cells[].permissionKey | string | 是 | 单元格 | `adminAccess` | 权限项 |
| rows[].cells[].state | string | 是 | 单元格样式 | `allow` | allow/limited/deny |
| rows[].cells[].label | string | 是 | 单元格文案 | `允许` | 展示文案 |
| rows[].cells[].scope | string | 否 | 限制说明 | `self` | 限制范围 |

### 5.3 角色模板字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| templateKey | string | 是 | 模板列表 | `pm` | 模板 key |
| title | string | 是 | 模板名称 | `PM 模板` | 模板名称 |
| scope | string | 是 | 适用范围 | `项目内身份` | 平台/项目/组织 |
| description | string | 否 | 模板描述 | `项目负责人...` | 说明 |
| visibleModules | string[] | 是 | 可见页面 chip | `["overview","kanban"]` | 可见模块 |
| actionPermissions | string[] | 是 | 操作权限 chip | `["create-task"]` | 操作权限 |
| sourceTemplateKey | string | 否 | 另存为 | `pm` | 来源模板 |
| version | number | 是 | 保存 | `3` | 乐观锁 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| metricStatusType | `success` | 正常 | 成功色 | 正常指标 |
| metricStatusType | `warning` | 待处理 | 警告色 | 需要处理 |
| metricStatusType | `danger` | 关注 | 危险色 | 异常指标 |
| metricStatusType | `ai` | AI | AI 样式 | AI 指标 |
| riskLevel | `low` | 低 | primary | 低风险 |
| riskLevel | `medium` | 中 | warning | 中风险 |
| riskLevel | `high` | 高 | danger | 高风险 |
| permissionState | `allow` | 允许 | success | 完整权限 |
| permissionState | `limited` | 限制 | warning | 条件权限 |
| permissionState | `deny` | 禁止 | danger | 无权限 |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| activeAccountCount | number | 近 30 天有登录或操作的账号 | 指标卡 | 当前静态 1,284 |
| pendingRoleTemplateChangeCount | number | 待审批/待处理模板变更 | 指标卡 | 当前静态 12 |
| abnormalAuditEventCount | number | 高风险/失败/异常审计事件 | 指标卡 | 当前静态 4 |
| aiRuleAdoptionRate | number | 已采纳 AI 建议 / AI 建议总数 | 指标卡 | 当前静态 67% |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取后台管理总览 | GET | `/api/admin/overview` | 首屏指标和摘要 | P0 |
| API-002 | 获取权限矩阵 | GET | `/api/admin/permission-matrix` | 权限矩阵弹窗 | P0 |
| API-003 | 导出权限矩阵 | POST | `/api/admin/permission-matrix/export` | 导出 PDF/XLSX | P1 |
| API-004 | 获取角色模板选项 | GET | `/api/admin/role-templates/options` | 新建模板弹窗 | P0 |
| API-005 | 新建角色模板 | POST | `/api/admin/role-templates` | 保存新模板 | P0 |
| API-006 | 另存为角色模板 | POST | `/api/admin/role-templates/copy` | 模板副本 | P1 |
| API-007 | 获取 AI 管理建议 | GET | `/api/admin/ai-suggestions` | 首页/抽屉建议 | P1 |
| API-008 | 应用 AI 管理建议 | POST | `/api/admin/ai-suggestions/{suggestionId}/apply` | 采纳建议 | P1 |
| API-009 | 稍后处理 AI 建议 | POST | `/api/admin/ai-suggestions/{suggestionId}/defer` | 延后处理 | P2 |
| API-010 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部角标 | P0 |

## 7. 接口详情

### API-001 获取后台管理总览

**请求方式**

- Method: `GET`
- Path: `/api/admin/overview`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `权限` | 顶部搜索关键词 |
| range | query | string | 否 | `30d` | 统计周期 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "metrics": [
      { "key": "activeAccounts", "label": "活跃账号数", "value": 1284, "status": "正常", "statusType": "success" },
      { "key": "pendingRoleTemplates", "label": "角色模板变更申请", "value": 12, "status": "待处理", "statusType": "warning" },
      { "key": "abnormalAudits", "label": "异常审计事件", "value": 4, "status": "关注", "statusType": "danger" },
      { "key": "aiRuleAdoptionRate", "label": "推荐规则采纳率", "value": 67, "status": "AI", "statusType": "ai", "unit": "%" }
    ],
    "roleUsage": [
      { "roleKey": "pm", "roleName": "PM", "usageRate": 88 },
      { "roleKey": "dev", "roleName": "研发", "usageRate": 96 }
    ],
    "configRisks": [
      { "key": "permissionChange", "label": "权限变更操作", "riskLevel": "high", "riskRate": 84 }
    ],
    "recentAudits": [
      {
        "id": "audit_001",
        "title": "修改系统配置",
        "description": "管理员李工更新了通知通道策略，已生成审计记录。",
        "occurredAt": "2026-05-11T10:43:00+08:00",
        "riskLevel": "high"
      }
    ]
  }
}
```

### API-002 获取权限矩阵

**请求方式**

- Method: `GET`
- Path: `/api/admin/permission-matrix`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| matrixType | query | string | 否 | `all` | all/platform/project |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "platform": {
      "columns": [
        { "key": "adminAccess", "label": "后台入口" },
        { "key": "userManage", "label": "用户管理" }
      ],
      "rows": [
        {
          "roleKey": "super_admin",
          "roleName": "超级管理员",
          "cells": [
            { "permissionKey": "adminAccess", "state": "allow", "label": "允许" }
          ]
        }
      ]
    },
    "project": {
      "columns": [
        { "key": "createTask", "label": "创建任务" },
        { "key": "inviteMember", "label": "邀请成员" }
      ],
      "rows": []
    }
  }
}
```

### API-005 新建角色模板

**请求方式**

- Method: `POST`
- Path: `/api/admin/role-templates`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| title | body | string | 是 | `联调负责人模板` | 模板名称 |
| scope | body | string | 是 | `project` | 适用范围 |
| description | body | string | 否 | `适用于联调...` | 描述 |
| visibleModules | body | string[] | 是 | `["overview"]` | 可见模块 |
| actionPermissions | body | string[] | 是 | `["create-task"]` | 操作权限 |
| sourceTemplateKey | body | string | 否 | `pm` | 来源模板 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "templateId": "tpl_10001",
    "templateKey": "integration_owner",
    "version": 1,
    "createdAt": "2026-05-11T15:00:00+08:00"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入后台首页 | 页面加载 | `GET /api/admin/overview` | 当前用户、周期 | 渲染总览 | 错误占位 |
| 顶部搜索 | 搜索框 | `GET /api/admin/overview` 或后台搜索接口 | keyword | 更新结果 | Toast |
| 查看权限矩阵 | 页面按钮 | `GET /api/admin/permission-matrix` | matrixType | 打开弹窗 | Toast |
| 导出矩阵 | 矩阵弹窗 | `POST /api/admin/permission-matrix/export` | 当前矩阵筛选 | Toast/下载任务 | Toast |
| 新增角色模板 | 侧边栏按钮 | `GET /api/admin/role-templates/options` | 当前用户 | 打开弹窗 | Toast |
| 保存模板 | 弹窗主按钮 | `POST /api/admin/role-templates` | 表单 | Toast，刷新模板 | 表单错误 |
| 另存为模板 | 弹窗按钮 | `POST /api/admin/role-templates/copy` | 表单和来源模板 | Toast | 表单错误 |
| 应用 AI 建议 | AI 卡片按钮 | `POST /api/admin/ai-suggestions/{id}/apply` | suggestionId | Toast | Toast |
| 稍后处理 | AI 抽屉按钮 | `POST /api/admin/ai-suggestions/{id}/defer` | suggestionId | Toast | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| title | input | 是 | 2-50 字 | 名称唯一、长度合法 | 请输入模板名称 |
| scope | input/select | 是 | 枚举合法 | platform/project/org | 请选择适用范围 |
| description | textarea | 否 | 最长 500 字 | 长度合法 | 模板描述过长 |
| visibleModules | chip group | 是 | 至少 1 项 | 模块 key 合法 | 至少选择一个可见页面 |
| actionPermissions | chip group | 否 | 权限 key 合法 | 权限存在且可授予 | 操作权限无效 |
| sourceTemplateKey | template list | 否 | 模板存在 | 当前用户可读取 | 来源模板无效 |

### 9.1 提交规则

- 是否允许重复提交：保存、另存、导出、AI 应用处理中不允许重复提交。
- 是否需要二次确认：导出权限矩阵、应用高风险 AI 策略建议建议二次确认。
- 是否需要审计日志：需要，矩阵导出、模板创建、AI 策略应用均记录。
- 是否需要乐观锁或版本号：新建不需要；后续编辑模板需要 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 角色名称 | roleName | string | 否 | 矩阵行 |
| 权限项 | permissionKey | string | 否 | 矩阵列 |
| 权限状态 | state | string | 否 | allow/limited/deny |
| 审计标题 | title | string | 否 | 最近审计 |
| 发生时间 | occurredAt | string | 是 | 最近审计 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 总览/审计/角色搜索 |
| 统计周期 | range | string | `30d` | 指标统计范围 |
| 矩阵类型 | matrixType | string | `all` | all/platform/project |

### 10.3 分页规则

- 总览页指标不分页。
- 最近审计默认返回 5-10 条；完整列表跳转 `AdminLogs.vue`。
- 权限矩阵默认全量返回；角色/权限项较多时按矩阵类型分块懒加载。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出权限矩阵 | `POST /api/admin/permission-matrix/export` | pdf/xlsx | 不适用 | 异步任务或同步下载 | P1 |
| 导出审计摘要 | `POST /api/admin/overview/export` | xlsx/pdf | 不适用 | 异步任务 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知服务 | 顶部未读数、审批提醒 |
| AI 管理建议 | 是 | AI 管理策略服务 | 首页建议卡片 |
| AI 权限策略 | 是 | AI 管理策略服务 | 生成/应用权限策略草稿 |
| 审计日志 | 是 | 审计服务 | 记录模板、矩阵、AI 操作 |
| WebSocket / SSE | 可选 | 管理事件流 | 后续实时审计告警 |

## 13. 缓存与实时性

- 数据是否允许缓存：总览统计可缓存 30 秒；权限矩阵、模板选项可缓存 60 秒。
- 缓存时间：指标 30 秒，矩阵 60 秒，AI 建议按上下文短缓存。
- 页面返回时是否刷新：建议刷新总览和通知未读数。
- 是否需要轮询：首期不需要；异常审计事件可后续轮询或事件流。
- 是否需要 WebSocket / SSE：首期不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `ADMIN_PARAM_INVALID` | 参数错误 | Toast |
| 400 / `ROLE_TEMPLATE_VALIDATE_FAILED` | 模板字段错误 | 表单错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `ADMIN_FORBIDDEN` | 无后台权限 | 重定向工作台或无权限页 |
| 403 / `PERMISSION_MATRIX_EXPORT_FORBIDDEN` | 无导出权限 | Toast |
| 409 / `ROLE_TEMPLATE_NAME_DUPLICATED` | 模板名称重复 | 表单错误 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 进入 `/admin` 后，指标卡、角色使用分布、配置风险、最近审计事件均由接口返回。
- 权限矩阵弹窗的平台矩阵和项目矩阵由接口返回，不再使用静态数组。
- 新建角色模板弹窗的模板选项、可见模块、操作权限由接口返回。
- 保存模板、另存模板、导出矩阵、应用 AI 建议均有明确接口和错误码。
- 无后台权限用户访问 `/admin` 时被拦截，不可看到后台数据。
- 所有模板变更、矩阵导出、AI 策略应用均写入审计日志。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 后台总览指标统计周期固定 30 天还是支持切换？ | 产品/后端 | 待确认 |
| Q2 | 权限矩阵导出是同步下载还是异步任务？ | 后端 | 待确认 |
| Q3 | AI 权限策略应用是否需要审批流？ | 产品/后端/AI | 待确认 |
| Q4 | 角色模板新建后是否立即生效，还是进入草稿/审批状态？ | 产品/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`metricCards`、`roleUsageBars`、`configChangeRows`、`recentAuditItems`、`platformMatrixRows`、`projectMatrixRows`、`templateItems`、`visibilityChips`、`actionChips`。
- 当前页面中的 TODO/API 标记：全局搜索、通知中心、应用切换器、AI 抽屉、矩阵导出、新建模板保存/另存、AI 建议应用。
- 当前用户信息和通知角标为静态数据。
- 需要后端优先确认的字段：权限矩阵列定义、角色模板权限 key、AI 建议状态。
- 需要后端优先确认的接口：`GET /api/admin/overview`、`GET /api/admin/permission-matrix`、`POST /api/admin/role-templates`。

