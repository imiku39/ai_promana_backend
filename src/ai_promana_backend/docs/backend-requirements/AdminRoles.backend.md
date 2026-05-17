# 角色管理后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/admin/AdminRoles.vue`  
> 页面定位：后台角色管理页，覆盖平台角色、项目角色模板、权限矩阵、模板编辑和新建。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 角色管理 |
| 前端路由 | `/admin/roles` |
| 前端文件 | `src/views/admin/AdminRoles.vue` |
| 所属模块 | 后台管理 / 角色权限 / 项目角色模板 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示平台角色和项目角色模板的权限摘要。
- 查看完整平台权限矩阵和项目权限矩阵。
- 编辑已有项目角色模板，如 PM、研发、QA、协作者。
- 新建角色模板或基于现有模板另存为副本。
- 导出角色功能矩阵。

### 2.2 对接范围

- 角色管理首屏概览卡片和权限摘要表。
- 平台角色矩阵和项目角色矩阵。
- 项目角色模板列表、详情、编辑保存、另存为。
- 新建角色模板。
- 模块可见权限、操作权限枚举。
- 顶部当前用户、通知未读数和搜索。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `AdminHome.vue` | 首页可查看权限矩阵和新建模板 |
| `AdminUsers.vue` | 用户角色分配依赖角色定义 |
| `AdminProjectTemplates.vue` | 项目模板使用角色模板配置默认权限 |
| `AdminLogs.vue` | 角色模板变更写入审计日志 |
| `ProjectMembers.vue` | 项目成员角色来源 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 可管理全部角色 |
| 管理员 | 是 | 视权限 | 视权限 | 视权限 | 是 | 不可越权授予高权限 |
| 项目负责人 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |
| 成员 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |

### 3.1 权限规则

- 页面入口权限：访问 `/admin/roles` 需要 `admin:access` 和 `admin:role:read`。
- 按钮级权限：
  - 查看矩阵需要 `admin:permission-matrix:read`。
  - 导出矩阵需要 `admin:permission-matrix:export`。
  - 编辑模板需要 `admin:role-template:update`。
  - 新建/另存模板需要 `admin:role-template:create`。
  - 删除模板后续需要 `admin:role-template:delete`。
- 数据范围权限：管理员仅可编辑自己管理域内的项目角色模板；平台内置角色只读。
- 敏感字段脱敏规则：权限变更记录中的操作者、审批备注按审计脱敏规则处理。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 当前用户 | 顶部用户卡片 | 是 | `GET /api/auth/me` | 静态为系统管理员 |
| 通知未读数 | 顶部通知角标 | 是 | `GET /api/notifications/unread-count` | 静态为 5 |
| 角色概览 | 两张概览卡片 | 是 | `GET /api/admin/roles/overview` | 平台角色/项目模板 |
| 权限摘要 | 摘要表格 | 是 | `GET /api/admin/roles/summary-permissions` | 首屏展示 |
| 模板库 | 编辑模板弹窗 | 是 | `GET /api/admin/role-templates` | 当前静态 templateLibrary |
| 权限选项 | chip 枚举 | 是 | `GET /api/admin/role-templates/options` | 可见模块/操作权限 |
| 权限矩阵 | 矩阵弹窗 | 否 | `GET /api/admin/permission-matrix` | 打开时加载 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 加载中 | 请求处理中 | 首屏/弹窗 |
| empty | 空状态 | 无模板或无权限项 | 表格/模板区 |
| error | Toast/错误占位 | 接口异常 | 标准错误 |
| dirty | 存在未保存更改 | 编辑表单本地已变更 | 当前已有状态文案 |
| synced | 当前模板已同步 | 后端版本一致 | 当前已有状态文案 |
| saving | 保存中 | 写请求处理中 | 禁用保存按钮 |

## 5. 字段模型

### 5.1 角色概览字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| cards[].key | string | 是 | 概览卡 | `platformRoles` | 卡片 key |
| cards[].title | string | 是 | 概览卡 | `平台角色` | 标题 |
| cards[].description | string | 是 | 概览卡 | `超级管理员...` | 描述 |
| cards[].buttonLabel | string | 是 | 按钮 | `查看矩阵` | 按钮文案 |
| cards[].action | string | 是 | 按钮动作 | `matrix` | matrix/edit |

### 5.2 权限矩阵字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| matrixType | string | 是 | 分区 | `platform` | platform/project |
| columns[].key | string | 是 | 表头 | `adminAccess` | 权限项 |
| columns[].label | string | 是 | 表头 | `后台入口` | 展示文案 |
| rows[].roleKey | string | 是 | 行 key | `pm` | 角色 key |
| rows[].roleName | string | 是 | 行标题 | `PM` | 角色名称 |
| rows[].cells[].state | string | 是 | 单元格 | `allow` | allow/limited/deny |
| rows[].cells[].label | string | 是 | 单元格文案 | `允许` | 展示文案 |
| rows[].cells[].icon | string | 否 | 图标 | `check_circle` | 前端图标 |

### 5.3 角色模板字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| templateId | string | 是 | 模板 ID | `tpl_pm` | 唯一标识 |
| templateKey | string | 是 | 模板列表 key | `pm` | 模板 key |
| title | string | 是 | 模板名称 | `PM 模板` | 名称 |
| scope | string | 是 | 适用范围 | `项目内身份` | 展示或枚举 |
| description | string | 否 | 模板说明 | `默认用于项目负责人...` | 描述 |
| visibleModules | string[] | 是 | 可见页面 chip | `["overview","kanban"]` | 模块权限 |
| actionPermissions | string[] | 是 | 操作权限 chip | `["create-task"]` | 操作权限 |
| isBuiltin | boolean | 是 | 操作限制 | `true` | 内置模板限制删除 |
| version | number | 是 | 保存 | `2` | 乐观锁 |
| updatedAt | string | 否 | 状态 | `2026-05-11T15:30:00+08:00` | 更新时间 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| platformRole | `super_admin` | 超级管理员 | neutral | 平台最高权限 |
| platformRole | `admin` | 系统管理员 | neutral | 后台管理员 |
| platformRole | `user` | 普通用户 | neutral | 无后台入口 |
| projectRole | `pm` | PM | neutral | 项目负责人 |
| projectRole | `dev` | 研发 | neutral | 研发成员 |
| projectRole | `qa` | QA | neutral | 测试成员 |
| projectRole | `product` | 产品 | neutral | 产品成员 |
| projectRole | `collab` | 协作者 | neutral | 只读协作 |
| permissionState | `allow` | 允许 | success | 允许 |
| permissionState | `limited` | 限制 | warning | 条件允许 |
| permissionState | `deny` | 禁止 | danger | 禁止 |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| platformRoleCount | number | 平台角色数量 | 概览 | 可选 |
| projectTemplateCount | number | 项目角色模板数量 | 概览 | 可选 |
| pendingChangeCount | number | 待审批模板变更 | 状态提示 | 可选 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取角色管理概览 | GET | `/api/admin/roles/overview` | 首屏卡片 | P0 |
| API-002 | 获取权限摘要 | GET | `/api/admin/roles/summary-permissions` | 摘要表 | P0 |
| API-003 | 获取权限矩阵 | GET | `/api/admin/permission-matrix` | 矩阵弹窗 | P0 |
| API-004 | 导出权限矩阵 | POST | `/api/admin/permission-matrix/export` | 导出矩阵 | P1 |
| API-005 | 获取角色模板列表 | GET | `/api/admin/role-templates` | 模板库 | P0 |
| API-006 | 获取角色模板详情 | GET | `/api/admin/role-templates/{templateId}` | 编辑弹窗 | P0 |
| API-007 | 更新角色模板 | PUT | `/api/admin/role-templates/{templateId}` | 保存编辑 | P0 |
| API-008 | 另存角色模板 | POST | `/api/admin/role-templates/{templateId}/copy` | 另存为 | P1 |
| API-009 | 新建角色模板 | POST | `/api/admin/role-templates` | 新建模板 | P0 |
| API-010 | 获取模板选项 | GET | `/api/admin/role-templates/options` | 权限 chip | P0 |

## 7. 接口详情

### API-005 获取角色模板列表

**请求方式**

- Method: `GET`
- Path: `/api/admin/role-templates`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `PM` | 模板搜索 |
| scope | query | string | 否 | `project` | 适用范围 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "templateId": "tpl_pm",
        "templateKey": "pm",
        "title": "PM 模板",
        "scope": "项目内身份",
        "description": "默认用于项目负责人。",
        "visibleModules": ["overview", "kanban", "gantt", "risk", "members", "reports"],
        "actionPermissions": ["create-task", "assign-owner", "export-report"],
        "isBuiltin": true,
        "version": 3
      }
    ]
  }
}
```

### API-007 更新角色模板

**请求方式**

- Method: `PUT`
- Path: `/api/admin/role-templates/{templateId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| templateId | path | string | 是 | `tpl_pm` | 模板 ID |
| title | body | string | 是 | `PM 模板` | 名称 |
| scope | body | string | 是 | `project` | 范围 |
| description | body | string | 否 | `默认用于...` | 描述 |
| visibleModules | body | string[] | 是 | `["overview"]` | 可见模块 |
| actionPermissions | body | string[] | 是 | `["create-task"]` | 操作权限 |
| version | body | number | 是 | `3` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "templateId": "tpl_pm",
    "version": 4,
    "updatedAt": "2026-05-11T15:40:00+08:00"
  }
}
```

### API-010 获取模板选项

**请求方式**

- Method: `GET`
- Path: `/api/admin/role-templates/options`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "visibleModules": [
      { "key": "overview", "label": "项目详情" },
      { "key": "kanban", "label": "项目看板" },
      { "key": "gantt", "label": "项目甘特图" },
      { "key": "risk", "label": "风险看板" },
      { "key": "members", "label": "成员管理" },
      { "key": "reports", "label": "项目报表" },
      { "key": "admin", "label": "后台管理" }
    ],
    "actionPermissions": [
      { "key": "create-task", "label": "创建任务" },
      { "key": "assign-owner", "label": "分配负责人" },
      { "key": "export-report", "label": "导出报表" }
    ],
    "scopes": [
      { "key": "project", "label": "项目内身份" },
      { "key": "platform", "label": "平台身份" }
    ]
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入角色管理 | 页面加载 | `GET /api/admin/roles/overview`、`GET /api/admin/role-templates` | 当前用户 | 渲染页面 | 错误占位 |
| 查看矩阵 | 概览按钮 | `GET /api/admin/permission-matrix` | matrixType | 打开弹窗 | Toast |
| 导出矩阵 | 弹窗按钮 | `POST /api/admin/permission-matrix/export` | 当前矩阵 | Toast/下载 | Toast |
| 打开编辑模板 | 概览按钮 | `GET /api/admin/role-templates/{id}` | templateId | 填充表单 | Toast |
| 切换编辑模板 | 侧边模板 | `GET /api/admin/role-templates/{id}` | templateId | 切换表单 | Toast |
| 保存编辑模板 | 编辑弹窗 | `PUT /api/admin/role-templates/{id}` | 表单/version | Toast，更新状态 | 表单错误 |
| 另存模板 | 编辑弹窗 | `POST /api/admin/role-templates/{id}/copy` | 表单 | Toast | 表单错误 |
| 新建模板 | 侧边按钮 | `GET /api/admin/role-templates/options` | 当前用户 | 打开弹窗 | Toast |
| 保存新模板 | 新建弹窗 | `POST /api/admin/role-templates` | 表单 | Toast，刷新模板 | 表单错误 |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| title | input | 是 | 2-50 字 | 名称唯一、长度合法 | 请输入模板名称 |
| scope | input/select | 是 | 枚举合法 | 范围合法 | 请输入适用范围 |
| description | textarea | 否 | 最长 500 字 | 长度合法 | 描述过长 |
| visibleModules | chip group | 是 | 至少一项 | 模块 key 合法 | 至少选择一个可见页面 |
| actionPermissions | chip group | 否 | 权限 key 合法 | 不得越权授予 | 操作权限无效 |
| version | hidden | 编辑必填 | 数字 | 乐观锁 | 模板已被更新，请刷新 |

### 9.1 提交规则

- 是否允许重复提交：保存、另存、新建、导出期间不允许重复提交。
- 是否需要二次确认：授予后台管理、删除模板、导出矩阵建议二次确认。
- 是否需要审计日志：需要，角色模板所有写操作和矩阵导出都记录。
- 是否需要乐观锁或版本号：编辑模板必须传 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 模板名称 | title | string | 是 | 模板列表 |
| 适用范围 | scope | string | 是 | 平台/项目 |
| 可见模块 | visibleModules | array | 否 | chip |
| 操作权限 | actionPermissions | array | 否 | chip |
| 更新时间 | updatedAt | string | 是 | 后续扩展 |
| 是否内置 | isBuiltin | boolean | 是 | 控制删除 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 模板名称/描述 |
| 范围 | scope | string | all | platform/project |
| 是否内置 | isBuiltin | boolean | 空 | 内置模板筛选 |

### 10.3 分页规则

- 角色模板数量少时可全量返回。
- 超过 100 个模板时支持 `page`、`pageSize`。
- 默认排序：内置模板优先，更新时间倒序。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出权限矩阵 | `POST /api/admin/permission-matrix/export` | pdf/xlsx | 不适用 | 异步任务或同步下载 | P1 |
| 导入角色模板 | `POST /api/admin/role-templates/import` | json/xlsx | 待确认 | 上传预览 | P2 |
| 导出角色模板 | `GET /api/admin/role-templates/export` | json/xlsx | 不适用 | 同步/异步 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知服务 | 模板审批、权限变更提醒 |
| AI 建议 | 可选 | AI 权限服务 | 后续可推荐最小权限 |
| 审计日志 | 是 | 审计服务 | 权限变更必记 |
| WebSocket / SSE | 否 | 无 | 首期不需要 |

## 13. 缓存与实时性

- 数据是否允许缓存：角色模板和权限选项可缓存 60 秒；编辑保存后必须刷新。
- 缓存时间：模板列表 60 秒，权限选项 5 分钟。
- 页面返回时是否刷新：建议刷新模板列表和权限摘要。
- 是否需要轮询：不需要。
- 是否需要 WebSocket / SSE：首期不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `ROLE_TEMPLATE_VALIDATE_FAILED` | 模板字段错误 | 表单错误 |
| 400 / `PERMISSION_KEY_INVALID` | 权限 key 无效 | 表单错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `ADMIN_ROLE_FORBIDDEN` | 无角色管理权限 | 无权限提示 |
| 403 / `PERMISSION_GRANT_FORBIDDEN` | 越权授予权限 | 表单错误 |
| 404 / `ROLE_TEMPLATE_NOT_FOUND` | 模板不存在 | 关闭弹窗并刷新 |
| 409 / `ROLE_TEMPLATE_NAME_DUPLICATED` | 名称重复 | 表单错误 |
| 409 / `ROLE_TEMPLATE_VERSION_CONFLICT` | 版本冲突 | 提示刷新 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 角色概览、权限摘要、模板库由接口返回。
- 权限矩阵弹窗的平台和项目矩阵由接口返回并可导出。
- 编辑模板时切换模板可加载对应详情，修改 chip 后状态显示未保存。
- 保存编辑模板必须传 `version`，版本冲突有明确提示。
- 新建模板和另存模板可以提交完整字段，并刷新模板列表。
- 后端返回的权限 key 与前端 chip 枚举一致。
- 角色模板变更写入审计日志。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 平台角色是否允许前端编辑，还是仅项目角色模板可编辑？ | 产品/权限 | 待确认 |
| Q2 | 新建模板是否需要审批流？ | 产品/后端 | 待确认 |
| Q3 | 授予“后台管理”可见权限是否需要超级管理员二次确认？ | 产品/安全 | 待确认 |
| Q4 | 权限矩阵列是否由后端完全驱动？ | 前端/后端 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`overviewCards`、`summaryPermissionRows`、`platformMatrixRows`、`projectMatrixRows`、`templateItems`、`visibilityChips`、`actionChips`、`templateLibrary`。
- 当前页面中的 TODO/API 标记：角色/权限搜索、通知、应用切换器、AI 抽屉、矩阵导出、模板保存、另存、新建。
- 当前编辑模板直接改本地 `templateLibrary`，未接后端。
- 需要后端优先确认的字段：权限矩阵列、模板 `visibleModules` 和 `actionPermissions` key。
- 需要后端优先确认的接口：`GET /api/admin/role-templates`、`PUT /api/admin/role-templates/{templateId}`、`GET /api/admin/permission-matrix`。

