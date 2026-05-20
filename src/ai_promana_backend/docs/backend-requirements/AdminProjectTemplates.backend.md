# 项目模板管理后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/admin/AdminProjectTemplates.vue`  
> 页面定位：后台项目模板列表页，覆盖项目模板查看、新建、编辑、删除。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目模板管理 |
| 前端路由 | `/admin/project-templates` |
| 前端文件 | `src/views/admin/AdminProjectTemplates.vue` |
| 所属模块 | 后台管理 / 项目模板 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 管理项目创建时可复用的项目模板。
- 列表展示模板名称、描述、里程碑数、创建时间。
- 支持新建模板、编辑模板、删除模板。
- 支持返回后台首页和角色管理页面。

### 2.2 对接范围

- 项目模板列表查询、分页、排序。
- 项目模板新建、编辑、删除。
- 模板里程碑数量统计。
- 删除前影响范围校验。
- 后续可扩展模板详情、里程碑明细、任务预设、角色预设。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `AdminHome.vue` | 后台首页入口 |
| `AdminRoles.vue` | 模板可关联默认角色模板 |
| `Projects.vue` | 新建项目时可选择项目模板 |
| `ProjectGantt.vue` | 模板里程碑会影响项目甘特图 |
| `AdminLogs.vue` | 项目模板增删改写入审计日志 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 可管理全部模板 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 删除受影响范围限制 |
| 项目负责人 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |
| 成员 | 否 | 否 | 否 | 否 | 否 | 默认无后台入口 |

### 3.1 权限规则

- 页面入口权限：访问 `/admin/project-templates` 需要 `admin:access` 和 `admin:project-template:read`。
- 按钮级权限：
  - “新建模板”需要 `admin:project-template:create`。
  - “编辑”需要 `admin:project-template:update`。
  - “删除”需要 `admin:project-template:delete`。
- 数据范围权限：管理员只可管理自己组织域内模板；全局模板需超级管理员。
- 敏感字段脱敏规则：无明显敏感字段；审计记录按审计规则脱敏。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 项目模板列表 | 表格主体 | 是 | `GET /api/admin/project-templates` | 当前静态 templates |
| 模板统计 | 里程碑数 | 是 | 列表接口返回 | 可由后端聚合 |
| 模板选项 | 新建/编辑弹窗 | 否 | `GET /api/admin/project-templates/options` | 后续弹窗需要 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 表格加载中 | 请求处理中 | 列表/详情 |
| empty | 空表格 | 无项目模板 | 首期需补空态 |
| error | Toast/错误占位 | 接口异常 | 标准错误 |
| saving | 保存中 | 新建/编辑处理中 | 禁用按钮 |
| deleting | 删除中 | 删除请求处理中 | 禁用删除 |

## 5. 字段模型

### 5.1 项目模板字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| id | string/number | 是 | 表格 key | `tpl_001` | 模板 ID |
| name | string | 是 | 模板名称 | `需求迭代` | 模板名称 |
| description | string | 否 | 描述 | `适用于产品需求迭代的项目模板` | 描述 |
| milestoneCount | number | 是 | 里程碑数 | `5` | 里程碑数量 |
| createTime | string | 是 | 创建时间 | `2026-04-01` | 日期 |
| creatorId | string | 否 | 隐含字段 | `u_001` | 创建人 |
| creatorName | string | 否 | 后续扩展 | `系统管理员` | 创建人 |
| status | string | 是 | 后续扩展 | `enabled` | enabled/disabled |
| usedProjectCount | number | 否 | 删除校验 | `12` | 使用该模板的项目数 |
| version | number | 否 | 编辑保存 | `1` | 乐观锁 |

### 5.2 模板明细字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| milestones[].id | string | 是 | 里程碑配置 | `ms_001` | 里程碑 ID |
| milestones[].name | string | 是 | 里程碑配置 | `需求评审` | 名称 |
| milestones[].offsetDays | number | 是 | 里程碑配置 | `3` | 项目开始后的天数 |
| milestones[].deliverables | string[] | 否 | 交付物 | `["PRD"]` | 交付物 |
| defaultRoleTemplateIds | string[] | 否 | 角色预设 | `["tpl_pm"]` | 默认角色模板 |
| taskPresets | array | 否 | 任务预设 | `[]` | 后续扩展 |

### 5.3 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| templateStatus | `enabled` | 启用 | success | 可被项目使用 |
| templateStatus | `disabled` | 停用 | neutral | 不可新选 |
| templateStatus | `archived` | 已归档 | warning | 历史保留 |

### 5.4 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| milestoneCount | number | 模板下里程碑数量 | 表格 | 当前静态 5/4/3 |
| usedProjectCount | number | 已使用模板项目数量 | 删除校验 | 可选展示 |
| templateTotal | number | 筛选后模板总数 | 分页 | 后续扩展 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取项目模板列表 | GET | `/api/admin/project-templates` | 表格数据 | P0 |
| API-002 | 获取项目模板详情 | GET | `/api/admin/project-templates/{templateId}` | 编辑详情 | P0 |
| API-003 | 新建项目模板 | POST | `/api/admin/project-templates` | 新建模板 | P0 |
| API-004 | 更新项目模板 | PUT | `/api/admin/project-templates/{templateId}` | 编辑模板 | P0 |
| API-005 | 删除项目模板 | DELETE | `/api/admin/project-templates/{templateId}` | 删除模板 | P0 |
| API-006 | 删除影响校验 | GET | `/api/admin/project-templates/{templateId}/delete-check` | 删除前检查 | P1 |
| API-007 | 获取模板配置选项 | GET | `/api/admin/project-templates/options` | 里程碑/角色选项 | P1 |

## 7. 接口详情

### API-001 获取项目模板列表

**请求方式**

- Method: `GET`
- Path: `/api/admin/project-templates`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `需求` | 模板名称/描述 |
| status | query | string | 否 | `enabled` | 状态 |
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
        "id": "tpl_001",
        "name": "需求迭代",
        "description": "适用于产品需求迭代的项目模板",
        "milestoneCount": 5,
        "createTime": "2026-04-01",
        "status": "enabled",
        "usedProjectCount": 12,
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

### API-003 新建项目模板

**请求方式**

- Method: `POST`
- Path: `/api/admin/project-templates`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| name | body | string | 是 | `需求迭代` | 模板名称 |
| description | body | string | 否 | `适用于...` | 描述 |
| milestones | body | array | 是 | `[]` | 里程碑配置 |
| defaultRoleTemplateIds | body | string[] | 否 | `["tpl_pm"]` | 默认角色 |
| status | body | string | 否 | `enabled` | 默认启用 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "tpl_10001",
    "version": 1,
    "createdAt": "2026-05-11T16:00:00+08:00"
  }
}
```

### API-006 删除影响校验

**请求方式**

- Method: `GET`
- Path: `/api/admin/project-templates/{templateId}/delete-check`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "canDelete": false,
    "usedProjectCount": 12,
    "message": "当前模板已被 12 个项目使用，建议停用而不是删除。"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入项目模板页 | 页面加载 | `GET /api/admin/project-templates` | 当前用户 | 渲染表格 | 错误占位 |
| 新建模板 | 新建按钮 | `POST /api/admin/project-templates` | 表单 | Toast，刷新列表 | 表单错误 |
| 编辑模板 | 行按钮 | `GET /api/admin/project-templates/{id}`、`PUT /api/admin/project-templates/{id}` | templateId/表单 | Toast，刷新行 | 表单错误 |
| 删除模板 | 行按钮 | `GET /api/admin/project-templates/{id}/delete-check`、`DELETE /api/admin/project-templates/{id}` | templateId | Toast，刷新列表 | Toast |
| 返回后台首页 | Back Admin | 前端路由 | `/admin` | 跳转 | 无 |
| 进入角色管理 | Roles | 前端路由 | `/admin/roles` | 跳转 | 无 |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| name | input | 是 | 2-50 字 | 名称唯一 | 请输入模板名称 |
| description | textarea | 否 | 最长 500 字 | 长度合法 | 描述过长 |
| milestones | list/editor | 是 | 至少 1 个 | 名称、顺序、偏移合法 | 请配置里程碑 |
| status | select | 是 | 枚举合法 | 状态合法 | 状态无效 |
| defaultRoleTemplateIds | multi-select | 否 | 模板存在 | 当前用户可使用 | 角色模板无效 |
| version | hidden | 编辑必填 | 数字 | 乐观锁 | 模板已被更新 |

### 9.1 提交规则

- 是否允许重复提交：新建、编辑、删除期间不允许重复提交。
- 是否需要二次确认：删除模板必须二次确认；被项目使用时禁止删除或提示停用。
- 是否需要审计日志：需要，模板新增、编辑、删除都记录。
- 是否需要乐观锁或版本号：编辑需要 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 模板名称 | name | string | 是 | 支持搜索 |
| 描述 | description | string | 否 | 支持搜索 |
| 里程碑数 | milestoneCount | number | 是 | 后端聚合 |
| 创建时间 | createTime | string | 是 | 日期 |
| 操作 | actions | array | 否 | 后续可由后端返回 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 模板名称/描述 |
| 状态 | status | string | all | enabled/disabled/archived |

### 10.3 分页规则

- 分页参数：`page`、`pageSize`。
- 默认页大小：20。
- 最大页大小：100。
- 排序参数：`sortBy`、`sortOrder`，默认 `createTime desc`。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出项目模板 | `GET /api/admin/project-templates/export` | json/xlsx | 不适用 | 同步/异步 | P2 |
| 导入项目模板 | `POST /api/admin/project-templates/import` | json/xlsx | 待确认 | 上传预览 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 可选 | 通知服务 | 模板变更通知 |
| AI 建议 | 可选 | AI 模板服务 | 后续推荐模板结构 |
| 审计日志 | 是 | 审计服务 | 模板变更必记 |
| WebSocket / SSE | 否 | 无 | 首期不需要 |

## 13. 缓存与实时性

- 数据是否允许缓存：模板列表可缓存 60 秒；新增/编辑/删除后必须刷新。
- 缓存时间：60 秒。
- 页面返回时是否刷新：建议刷新。
- 是否需要轮询：不需要。
- 是否需要 WebSocket / SSE：不需要。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `PROJECT_TEMPLATE_VALIDATE_FAILED` | 字段错误 | 表单错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `PROJECT_TEMPLATE_FORBIDDEN` | 无权限 | 无权限提示 |
| 404 / `PROJECT_TEMPLATE_NOT_FOUND` | 模板不存在 | 刷新列表 |
| 409 / `PROJECT_TEMPLATE_NAME_DUPLICATED` | 名称重复 | 表单错误 |
| 409 / `PROJECT_TEMPLATE_IN_USE` | 模板被项目使用 | 禁止删除/建议停用 |
| 409 / `PROJECT_TEMPLATE_VERSION_CONFLICT` | 版本冲突 | 提示刷新 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 项目模板列表由接口返回，显示名称、描述、里程碑数、创建时间。
- 新建、编辑、删除按钮有明确接口支撑。
- 删除模板前可校验影响范围，被使用模板不可直接删除。
- 模板新增、编辑、删除均写入审计日志。
- 无权限、空数据、字段错误、名称重复、版本冲突都有明确错误码。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 项目模板是否需要配置完整里程碑明细和任务预设？ | 产品/后端 | 待确认 |
| Q2 | 被项目使用过的模板是否允许删除，还是只能停用？ | 产品/后端 | 待确认 |
| Q3 | 项目模板是否需要区分全局模板和组织模板？ | 产品/权限 | 待确认 |

## 17. 前端备注

- 当前页面中的 mock 数据位置：`templates`。
- 当前页面中的 TODO/API 标记：当前页面未写 TODO，但新建、编辑、删除按钮均未接业务逻辑。
- 当前页面样式与其他后台页不一致，后续前端可能继续统一。
- 需要后端优先确认的字段：里程碑明细、模板状态、使用项目数。
- 需要后端优先确认的接口：`GET /api/admin/project-templates`、`POST /api/admin/project-templates`、`DELETE /api/admin/project-templates/{templateId}`。

