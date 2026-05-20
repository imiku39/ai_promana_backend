# 系统配置后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/admin/AdminSystem.vue`  
> 页面定位：后台系统配置页，覆盖通知通道、安全策略、保存配置、恢复默认。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 系统配置 |
| 前端路由 | `/admin/system` |
| 前端文件 | `src/views/admin/AdminSystem.vue` |
| 所属模块 | 后台管理 / 系统配置 / 通知与安全策略 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 管理系统级通知通道配置，如站内通知、企业微信推送、邮件订阅。
- 管理系统安全策略，如敏感操作审计、敏感数据脱敏显示。
- 支持保存配置、恢复默认配置。
- 当前前端使用 `localStorage` 暂存，后续需要后端配置中心接管。

### 2.2 对接范围

- 加载系统配置分组、配置项和当前值。
- 保存系统配置。
- 恢复默认配置。
- 顶部当前用户、通知未读数。
- 配置变更审计日志。
- 后续可扩展配置搜索、配置历史和回滚。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `AdminHome.vue` | 首页显示配置变更风险 |
| `AdminLogs.vue` | 配置保存和恢复默认写入审计日志 |
| `Notifications.vue` | 通知通道影响通知发送 |
| `Settings.vue` | 个人设置受系统默认配置影响 |
| `AdminUsers.vue` | 敏感数据脱敏影响用户字段展示 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 否 | 是 | 否 | 是 | 可修改全部配置 |
| 管理员 | 是 | 否 | 视权限 | 否 | 视权限 | 受配置权限限制 |
| 项目负责人 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |
| 成员 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |

### 3.1 权限规则

- 页面入口权限：访问 `/admin/system` 需要 `admin:access` 和 `admin:system-config:read`。
- 按钮级权限：
  - “保存配置”需要 `admin:system-config:update`。
  - “恢复默认”需要 `admin:system-config:reset`。
  - 配置历史导出后续需要 `admin:system-config:export`。
- 数据范围权限：系统全局配置仅超级管理员可全量修改；普通管理员可按配置项授权。
- 敏感字段脱敏规则：配置项中若包含密钥、Webhook、Token，列表返回时必须脱敏，详情编辑需单独权限。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 静态为系统管理员 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 静态为 5 |
| 系统配置 | 配置分组和开关 | 是 | `GET /api/admin/system/config` | 替代 localStorage |
| 配置默认值 | 恢复默认 | 否 | `GET /api/admin/system/config/defaults` | 可合并到首屏 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 加载中 | 请求处理中 | 配置加载 |
| empty | 空配置 | 无配置项 | 兜底 |
| error | Toast/错误占位 | 接口异常 | 标准错误 |
| dirty | 本地已修改 | 配置尚未保存 | 后续可扩展 |
| saving | 保存中 | 写请求处理中 | 禁用保存按钮 |
| saved | 成功 Toast | 保存成功 | 当前已有成功 Toast |

## 5. 字段模型

### 5.1 配置分组字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| sections[].key | string | 是 | 配置卡 key | `notice` | 分组 key |
| sections[].title | string | 是 | 卡片标题 | `通知通道` | 分组标题 |
| sections[].caption | string | 否 | 分组说明 | `站内 / 邮件 / 企微 / 钉钉` | 说明 |
| sections[].items[].key | string | 是 | 开关 key | `siteNotice` | 配置项 key |
| sections[].items[].label | string | 是 | 配置项标题 | `站内通知` | 展示名称 |
| sections[].items[].description | string | 否 | 配置项描述 | `全局默认开启` | 描述 |
| sections[].items[].value | boolean | 是 | toggle 状态 | `true` | 当前值 |
| sections[].items[].disabled | boolean | 否 | 控件状态 | `false` | 无权限禁用 |
| sections[].items[].requiresRestart | boolean | 否 | 提示 | `false` | 是否需重启/刷新 |

### 5.2 当前配置字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| siteNotice | boolean | 是 | 站内通知开关 | `true` | 全局站内通知 |
| wecomPush | boolean | 是 | 企业微信推送 | `true` | 任务阻塞、评论、报表订阅 |
| emailSubscription | boolean | 是 | 邮件订阅 | `false` | 周报、导出、审计告警 |
| auditTrail | boolean | 是 | 敏感操作审计 | `true` | 删除、归档、角色变更 |
| maskSensitiveData | boolean | 是 | 敏感数据脱敏 | `true` | 邮箱、手机号脱敏 |
| version | number | 是 | 保存提交 | `4` | 乐观锁 |
| updatedAt | string | 否 | 配置状态 | `2026-05-11T16:10:00+08:00` | 更新时间 |

### 5.3 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| configSection | `notice` | 通知通道 | neutral | 通知配置 |
| configSection | `security` | 安全策略 | neutral | 安全配置 |
| configValueType | `boolean` | 开关 | toggle | 当前均为布尔 |
| configStatus | `enabled` | 开启 | on | true |
| configStatus | `disabled` | 关闭 | off | false |

### 5.4 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| enabledCount | number | 开启配置项数量 | 后续扩展 | 可选 |
| changedCount | number | 本次变更项数量 | 保存提示 | 可选 |
| highRiskChangedCount | number | 高风险配置变更数量 | 二次确认 | 可选 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取系统配置 | GET | `/api/admin/system/config` | 首屏配置 | P0 |
| API-002 | 保存系统配置 | PUT | `/api/admin/system/config` | 保存开关 | P0 |
| API-003 | 获取默认配置 | GET | `/api/admin/system/config/defaults` | 恢复默认前预览 | P1 |
| API-004 | 恢复默认配置 | POST | `/api/admin/system/config/reset` | 恢复默认 | P0 |
| API-005 | 获取配置历史 | GET | `/api/admin/system/config/history` | 后续审计 | P2 |
| API-006 | 获取通知未读数 | GET | `/api/notifications/unread-count` | 顶部角标 | P0 |

## 7. 接口详情

### API-001 获取系统配置

**请求方式**

- Method: `GET`
- Path: `/api/admin/system/config`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `通知` | 配置搜索 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "sections": [
      {
        "key": "notice",
        "title": "通知通道",
        "caption": "站内 / 邮件 / 企微 / 钉钉",
        "items": [
          {
            "key": "siteNotice",
            "label": "站内通知",
            "description": "全局默认开启",
            "value": true,
            "disabled": false
          },
          {
            "key": "wecomPush",
            "label": "企业微信推送",
            "description": "任务阻塞、评论、报表订阅",
            "value": true,
            "disabled": false
          }
        ]
      }
    ],
    "config": {
      "siteNotice": true,
      "wecomPush": true,
      "emailSubscription": false,
      "auditTrail": true,
      "maskSensitiveData": true
    },
    "version": 4
  }
}
```

### API-002 保存系统配置

**请求方式**

- Method: `PUT`
- Path: `/api/admin/system/config`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| config.siteNotice | body | boolean | 是 | `true` | 站内通知 |
| config.wecomPush | body | boolean | 是 | `true` | 企微推送 |
| config.emailSubscription | body | boolean | 是 | `false` | 邮件订阅 |
| config.auditTrail | body | boolean | 是 | `true` | 审计开关 |
| config.maskSensitiveData | body | boolean | 是 | `true` | 脱敏开关 |
| version | body | number | 是 | `4` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "version": 5,
    "changedKeys": ["emailSubscription"],
    "updatedAt": "2026-05-11T16:20:00+08:00"
  }
}
```

### API-004 恢复默认配置

**请求方式**

- Method: `POST`
- Path: `/api/admin/system/config/reset`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keys | body | string[] | 否 | `["notice"]` | 为空表示全部恢复 |
| version | body | number | 是 | `5` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "config": {
      "siteNotice": true,
      "wecomPush": false,
      "emailSubscription": false,
      "auditTrail": true,
      "maskSensitiveData": false
    },
    "version": 6,
    "updatedAt": "2026-05-11T16:25:00+08:00"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入系统配置 | 页面加载 | `GET /api/admin/system/config` | 当前用户 | 渲染配置 | 错误占位 |
| 搜索配置项 | 顶部搜索 | `GET /api/admin/system/config` | keyword | 过滤配置 | Toast |
| 切换开关 | toggle | 不立即调用或调用保存 | key/value | 本地变更 | 无 |
| 保存配置 | 侧边栏/页面按钮 | `PUT /api/admin/system/config` | 当前配置和 version | 成功 Toast | Toast/表单错误 |
| 恢复默认 | 页面按钮 | `POST /api/admin/system/config/reset` | keys/version | 成功 Toast | Toast |
| 打开通知中心 | 顶部图标 | 路由/通知接口 | 当前用户 | 跳转 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| siteNotice | toggle | 是 | boolean | 配置项存在且可修改 | 配置项无效 |
| wecomPush | toggle | 是 | boolean | 通道可用 | 企微通道不可用 |
| emailSubscription | toggle | 是 | boolean | 邮件服务可用 | 邮件服务不可用 |
| auditTrail | toggle | 是 | boolean | 高风险配置限制 | 无权关闭审计 |
| maskSensitiveData | toggle | 是 | boolean | 高风险配置限制 | 无权关闭脱敏 |
| version | hidden | 是 | number | 乐观锁 | 配置已更新，请刷新 |

### 9.1 提交规则

- 是否允许重复提交：保存/恢复默认处理中不允许重复提交。
- 是否需要二次确认：关闭敏感操作审计、关闭敏感数据脱敏、恢复默认需要二次确认。
- 是否需要审计日志：需要，保存和恢复默认都记录变更前后摘要。
- 是否需要乐观锁或版本号：需要 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 分组 | section.title | string | 否 | 配置卡片 |
| 配置项 | item.label | string | 否 | 行标题 |
| 描述 | item.description | string | 否 | 行描述 |
| 当前值 | item.value | boolean | 否 | toggle |
| 是否禁用 | item.disabled | boolean | 否 | 权限控制 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 搜索配置项、策略或通知通道 |
| 分组 | sectionKey | string | all | notice/security |

### 10.3 分页规则

- 配置项数量较少，不分页。
- 配置历史接口后续支持分页，默认 20 条。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出系统配置 | `GET /api/admin/system/config/export` | json/xlsx | 不适用 | 同步下载 | P2 |
| 导入系统配置 | `POST /api/admin/system/config/import` | json | 待确认 | 上传预览 | P2 |
| 导出配置历史 | `GET /api/admin/system/config/history/export` | xlsx | 不适用 | 异步任务 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知服务 | 配置变更通知管理员 |
| 邮件/企微通知 | 是 | 通知服务 | 配置本身控制通道 |
| AI 建议 | 可选 | AI 配置建议 | 后续推荐安全策略 |
| 审计日志 | 是 | 审计服务 | 配置变更必记 |
| WebSocket / SSE | 否 | 无 | 首期不需要 |

## 13. 缓存与实时性

- 数据是否允许缓存：系统配置可短缓存 30 秒；保存后必须刷新或使用响应覆盖本地。
- 缓存时间：30 秒。
- 页面返回时是否刷新：建议刷新。
- 是否需要轮询：不需要。
- 是否需要 WebSocket / SSE：首期不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `SYSTEM_CONFIG_VALIDATE_FAILED` | 配置字段错误 | 表单错误/Toast |
| 400 / `SYSTEM_CONFIG_KEY_INVALID` | 配置项无效 | Toast |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `SYSTEM_CONFIG_FORBIDDEN` | 无配置权限 | 无权限提示 |
| 403 / `SYSTEM_CONFIG_HIGH_RISK_FORBIDDEN` | 无权修改高风险配置 | Toast |
| 409 / `SYSTEM_CONFIG_VERSION_CONFLICT` | 配置版本冲突 | 提示刷新 |
| 500 / `SYSTEM_CONFIG_SAVE_FAILED` | 保存失败 | Toast |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 系统配置分组、配置项和当前值由接口返回，不再依赖 `localStorage`。
- 保存配置时提交完整配置和版本号，成功后更新本地版本。
- 恢复默认配置由后端返回默认值并写入审计日志。
- 关闭审计、关闭脱敏等高风险配置有权限控制和明确错误码。
- 无权限、版本冲突、配置项无效、服务异常均有明确处理。
- 顶部搜索可按配置名称/描述筛选或请求后端过滤。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 系统配置是否全局唯一，还是按组织/租户隔离？ | 产品/后端 | 待确认 |
| Q2 | 关闭敏感操作审计和脱敏是否允许普通管理员操作？ | 安全/产品 | 待确认 |
| Q3 | 恢复默认是恢复全部配置，还是支持分组恢复？ | 产品/后端 | 待确认 |
| Q4 | 配置保存是否需要审批流或双人确认？ | 安全/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`settingSections`、`initialSettingState`、`resetSettingState`。
- 当前页面中的 TODO/API 标记：系统配置保存、恢复默认、配置加载、搜索、当前用户、通知、AI 抽屉。
- 当前配置持久化使用 `localStorage` 的 `systemConfig`，后续应由接口替代。
- 当前保存和恢复默认只触发 `emit` 并显示本地 Toast。
- 需要后端优先确认的字段：配置 key、默认值、是否可关闭审计/脱敏、版本号。
- 需要后端优先确认的接口：`GET /api/admin/system/config`、`PUT /api/admin/system/config`、`POST /api/admin/system/config/reset`。

