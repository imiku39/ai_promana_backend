# 项目文档后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/ProjectDocs.vue`，当前主要由 `views/ProjectDetail.vue` 的 `docs` tab 承载  
> 页面定位：项目文档列表、版本记录、AI 摘要和文档补齐建议。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目文档 |
| 前端路由 | `/project/:id/docs` |
| 前端文件 | `src/views/ProjectDocs.vue`、`src/views/ProjectDetail.vue` |
| 所属模块 | 项目管理 / 项目详情 / 文档 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示项目文档卡片，包括文档标题、描述、状态标签、更新时间、标签或责任人。
- 支持文档列表、版本记录、AI 摘要、新建与编辑动作。
- 展示文档页空状态，引导扩展为真实文档中心。
- 通过 AI 助手生成文档提纲、摘要、补齐建议，并关联项目任务。

### 2.2 对接范围

- 项目文档列表查询、搜索、筛选、分页。
- 文档详情、版本记录、创建、编辑、删除、归档。
- 文档附件上传、预览、下载。
- AI 摘要、文档提纲生成、文档与任务/里程碑关联。
- 权限控制、审计日志、文档访问范围。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `ProjectDetail.vue` | 当前文档 tab 的主要承载页 |
| `ProjectKanban.vue` | 文档可关联任务 |
| `ProjectGantt.vue` | 文档可关联里程碑 |
| `ProjectReports.vue` | 报表可引用文档摘要 |
| `Notifications.vue` | 文档更新通知 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全量文档 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 组织范围 |
| 项目负责人 | 是 | 是 | 是 | 是 | 是 | 可管理项目文档 |
| 项目成员 | 是 | 是 | 视权限 | 否 | 是 | 可编辑授权文档 |
| 协作者 | 是 | 否 | 否 | 否 | 否 | 只读 |

### 3.1 权限规则

- 页面入口权限：需要 `project:doc:read`。
- 按钮级权限：
  - 新建文档需要 `project:doc:create`。
  - 编辑文档需要 `project:doc:update`。
  - 删除/归档文档需要 `project:doc:delete` 或 `project:doc:archive`。
  - 下载/导出需要 `project:doc:download`。
  - AI 摘要/提纲需要 `ai:doc:generate`。
- 数据范围权限：按项目成员、文档可见范围、密级过滤。
- 敏感字段脱敏规则：无权限不返回密级文档内容、附件下载地址、内部评论。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 项目详情头部 | 项目名称和状态 | 是 | `GET /api/projects/{projectId}` | 共用 |
| 文档统计 | 文档数量、待补充数 | 否 | `GET /api/projects/{projectId}/docs/summary` | P1 |
| 文档列表 | 文档卡片 | 是 | `GET /api/projects/{projectId}/docs` | 当前 `docList` |
| 文档分类/标签 | 筛选选项 | 否 | `GET /api/projects/{projectId}/docs/options` | P1 |
| AI 文档建议 | AI 抽屉/卡片 | 否 | `GET /api/ai/project-doc-suggestions` | P1 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 文档加载 | 请求处理中 | 局部 loading |
| empty | 文档页空状态 | 无文档或首版占位 | 当前有空状态 |
| error | Toast / 错误占位 | 接口异常 | 标准错误 |
| latest | 最新版本标签 | 当前最新 | 文档状态 |
| aiSummary | AI 摘要标签 | 已生成摘要 | 文档能力 |
| incomplete | 待补充标签 | 文档缺失关键内容 | 文档状态 |

## 5. 字段模型

### 5.1 文档字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| docId | string | 是 | 文档 key | `doc_001` | 文档 ID |
| title | string | 是 | 卡片标题 | `需求评审纪要` | 文档标题 |
| description | string | 否 | 卡片描述 | `记录需求边界...` | 摘要 |
| status | string | 是 | 标签 | `latest` | 文档状态 |
| statusLabel | string | 是 | 标签中文 | `最新版本` | 展示 |
| tags | string[] | 否 | 标签/元信息 | `["联调","风险"]` | 文档标签 |
| owner.id | string | 否 | 责任人 | `u_10003` | 负责人 |
| owner.name | string | 否 | 责任人 | `QA 组` | 展示 |
| latestVersion | string | 是 | 版本记录 | `v3` | 最新版本 |
| updatedAt | string | 是 | 更新时间 | `2026-05-11T10:40:00+08:00` | 更新时间 |
| updatedBy.name | string | 否 | 更新人 | `王志强` | 展示 |
| visibility | string | 是 | 权限 | `project_members` | 可见范围 |
| fileType | string | 否 | 文件类型 | `markdown` | markdown/pdf/docx |
| hasAiSummary | boolean | 是 | AI 摘要标签 | `true` | 是否有摘要 |
| linkedTaskIds | string[] | 否 | 关联任务 | `["task_001"]` | 关联任务 |
| linkedMilestoneIds | string[] | 否 | 关联里程碑 | `["m_001"]` | 关联里程碑 |
| permissions | string[] | 否 | 操作权限 | `["edit","download"]` | 当前用户可操作 |
| version | number | 是 | 编辑版本 | `5` | 乐观锁 |

### 5.2 文档版本字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| versionId | string | 是 | 版本 key | `docv_001` | 版本 ID |
| versionName | string | 是 | 版本号 | `v3` | 版本名称 |
| changeSummary | string | 否 | 变更摘要 | `补充联调风险` | 摘要 |
| createdAt | string | 是 | 时间 | `2026-05-11T10:40:00+08:00` | 创建时间 |
| createdBy.name | string | 是 | 更新人 | `王志强` | 用户 |
| downloadUrl | string | 否 | 下载 | `https://...` | 有权限返回 |

### 5.3 AI 文档建议字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| suggestionId | string | 是 | AI 建议 | `sug_doc_001` | 建议 ID |
| title | string | 是 | 标题 | `文档建议` | 展示 |
| content | string | 是 | 内容 | `建议优先补齐回归样本池说明` | 建议内容 |
| targetDocId | string | 否 | 关联文档 | `doc_003` | 目标文档 |
| actions | array | 否 | 操作 | `[]` | 生成提纲/摘要 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| docStatus | `latest` | 最新版本 | success | 最新 |
| docStatus | `ai_summary` | AI 摘要 | ai | 已生成摘要 |
| docStatus | `incomplete` | 待补充 | warning | 缺内容 |
| docStatus | `archived` | 已归档 | neutral | 归档 |
| visibility | `project_members` | 项目成员 | neutral | 项目内可见 |
| visibility | `owners_only` | 负责人可见 | warning | 限制 |
| visibility | `public` | 公开 | success | 组织内公开 |
| fileType | `markdown` | Markdown | neutral | 文本 |
| fileType | `pdf` | PDF | neutral | PDF |
| fileType | `docx` | Word | neutral | Word |

### 5.5 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| docTotal | number | 当前项目文档总数 | 可选统计 | P1 |
| incompleteCount | number | 状态为 incomplete 的文档数 | 可选统计 | P1 |
| aiSummaryCount | number | 已生成 AI 摘要的文档数 | 可选统计 | P1 |
| latestUpdatedAt | string | 最新更新时间 | 可选统计 | P1 |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取文档列表 | GET | `/api/projects/{projectId}/docs` | 文档卡片 | P0 |
| API-002 | 获取文档详情 | GET | `/api/projects/{projectId}/docs/{docId}` | 详情/预览 | P1 |
| API-003 | 获取文档版本 | GET | `/api/projects/{projectId}/docs/{docId}/versions` | 版本记录 | P1 |
| API-004 | 新建文档 | POST | `/api/projects/{projectId}/docs` | 新建 | P1 |
| API-005 | 更新文档 | PUT | `/api/projects/{projectId}/docs/{docId}` | 编辑 | P1 |
| API-006 | 删除/归档文档 | DELETE | `/api/projects/{projectId}/docs/{docId}` | 删除/归档 | P1 |
| API-007 | 上传文档附件 | POST | `/api/projects/{projectId}/docs/{docId}/attachments` | 上传 | P1 |
| API-008 | 生成 AI 文档摘要 | POST | `/api/ai/project-docs/{docId}/summary` | AI 摘要 | P1 |
| API-009 | 获取 AI 文档建议 | GET | `/api/ai/project-doc-suggestions` | AI 建议 | P1 |
| API-010 | 采纳 AI 文档建议 | POST | `/api/ai/project-doc-suggestions/{suggestionId}/apply` | 生成提纲/摘要 | P1 |

## 7. 接口详情

### API-001 获取文档列表

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/docs`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `联调` | 标题/描述搜索 |
| status | query | string | 否 | `incomplete` | 文档状态 |
| tag | query | string | 否 | `风险` | 标签 |
| ownerId | query | string | 否 | `u_10003` | 责任人 |
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
        "docId": "doc_001",
        "title": "需求评审纪要",
        "description": "记录需求边界、时间计划和依赖说明，供 PM、研发与 QA 对齐使用。",
        "status": "latest",
        "statusLabel": "最新版本",
        "tags": ["需求", "评审"],
        "owner": { "id": "u_10001", "name": "王志强" },
        "latestVersion": "v3",
        "updatedAt": "2026-05-11T10:40:00+08:00",
        "updatedBy": { "id": "u_10001", "name": "王志强" },
        "visibility": "project_members",
        "fileType": "markdown",
        "hasAiSummary": false,
        "linkedTaskIds": ["task_001"],
        "linkedMilestoneIds": ["m_001"],
        "permissions": ["read", "edit", "download"],
        "version": 5
      }
    ],
    "pagination": { "page": 1, "pageSize": 20, "total": 3 }
  }
}
```

### API-005 更新文档

**请求方式**

- Method: `PUT`
- Path: `/api/projects/{projectId}/docs/{docId}`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| title | body | string | 是 | `联调验证说明` | 标题 |
| content | body | string | 否 | `# 联调验证` | 文档内容 |
| description | body | string | 否 | `包含联调阶段条件` | 摘要 |
| tags | body | string[] | 否 | `["联调"]` | 标签 |
| visibility | body | string | 是 | `project_members` | 可见范围 |
| linkedTaskIds | body | string[] | 否 | `["task_001"]` | 关联任务 |
| linkedMilestoneIds | body | string[] | 否 | `["m_001"]` | 关联里程碑 |
| version | body | number | 是 | `5` | 乐观锁 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "docId": "doc_002",
    "latestVersion": "v4",
    "version": 6,
    "updatedAt": "2026-05-11T12:00:00+08:00"
  }
}
```

### API-008 生成 AI 文档摘要

**请求方式**

- Method: `POST`
- Path: `/api/ai/project-docs/{docId}/summary`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| docId | path | string | 是 | `doc_002` | 文档 ID |
| summaryType | body | string | 否 | `brief` | brief/detailed |
| saveToDoc | body | boolean | 否 | `true` | 是否保存摘要 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "summaryId": "summary_001",
    "docId": "doc_002",
    "summary": "本文档说明当前联调阶段的前置条件、关键风险和任务引用。",
    "saved": true
  }
}
```

### API-010 采纳 AI 文档建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/project-doc-suggestions/{suggestionId}/apply`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "createdDocId": "doc_004",
    "updatedDocIds": ["doc_003"],
    "message": "已生成回归样本池说明提纲。"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入文档页 | tab 加载 | `GET /docs` | projectId | 渲染文档卡片 | 错误占位 |
| 搜索/筛选文档 | 搜索/筛选 | `GET /docs` | keyword/status/tag | 更新列表 | Toast |
| 点击文档卡 | 文档卡 | `GET /docs/{docId}` | docId | 打开详情/预览 | Toast |
| 新建文档 | 按钮 | `POST /docs` | 表单 | Toast，刷新列表 | 表单错误 |
| 编辑文档 | 详情页 | `PUT /docs/{docId}` | 表单 | Toast，刷新卡片 | 表单错误 |
| 查看版本 | 详情页 | `GET /docs/{docId}/versions` | docId | 渲染版本 | Toast |
| 生成 AI 摘要 | 文档卡/详情 | `POST /ai/project-docs/{docId}/summary` | docId | 展示摘要 | Toast |
| 采纳 AI 建议 | AI 抽屉 | `POST /ai/project-doc-suggestions/{id}/apply` | suggestionId | 生成提纲/摘要 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| title | input | 是 | 2-120 字 | 标题合法 | 请输入文档标题 |
| content | editor | 否 | 最大长度待定 | 内容合法 | 文档内容过长 |
| description | textarea | 否 | 最长 300 字 | 长度合法 | 摘要过长 |
| tags | tag selector | 否 | 最多 20 个 | 标签合法 | 标签无效 |
| visibility | select | 是 | 枚举 | 权限合法 | 请选择可见范围 |
| linkedTaskIds | selector | 否 | 任务数组 | 任务存在 | 关联任务无效 |
| linkedMilestoneIds | selector | 否 | 里程碑数组 | 里程碑存在 | 关联里程碑无效 |
| attachment | upload | 否 | 类型/大小限制 | 文件安全校验 | 附件上传失败 |

### 9.1 提交规则

- 是否允许重复提交：不允许。
- 是否需要二次确认：删除/归档文档、覆盖保存 AI 摘要需要二次确认。
- 是否需要审计日志：需要，创建、编辑、删除、上传、下载、AI 生成记录。
- 是否需要乐观锁或版本号：需要，编辑文档使用 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 标题 | title | string | 否 | 支持搜索 |
| 描述 | description | string | 否 | 摘要 |
| 状态 | status | string | 是 | 最新/AI 摘要/待补充 |
| 标签 | tags | array | 否 | 支持筛选 |
| 责任人 | owner.name | string | 是 | 可筛选 |
| 版本 | latestVersion | string | 是 | 版本 |
| 更新时间 | updatedAt | string | 是 | 默认排序 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 标题/描述 |
| 状态 | status | string | all | latest/ai_summary/incomplete |
| 标签 | tag | string | 空 | 标签 |
| 责任人 | ownerId | string | 空 | 用户 |

### 10.3 分页规则

- 默认页大小：20。
- 最大页大小：100。
- 默认排序：更新时间倒序、状态权重。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 上传附件 | `POST /api/projects/{projectId}/docs/{docId}/attachments` | md/pdf/docx/xlsx/png/jpg | 待确认 | 上传后安全扫描 | P1 |
| 下载文档 | `GET /api/projects/{projectId}/docs/{docId}/download` | 原文件 | 不适用 | 鉴权临时链接 | P1 |
| 导出文档 | `POST /api/projects/{projectId}/docs/{docId}/export` | md/pdf/docx | 不适用 | 异步任务 | P1 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 文档更新、@成员、补齐提醒 |
| AI 摘要/提纲 | 是 | AI 文档服务 | 摘要、提纲、补齐建议 |
| 审计日志 | 是 | 审计日志服务 | 文档读写下载 |
| WebSocket / SSE | 可选 | 文档协作服务 | 后续多人编辑 |

## 13. 缓存与实时性

- 数据是否允许缓存：文档列表可缓存 60 秒；文档详情按版本缓存。
- 缓存时间：编辑/上传/AI 摘要后立即失效。
- 页面返回时是否刷新：建议刷新文档列表。
- 是否需要轮询：AI 生成和导出任务可轮询任务状态。
- 是否需要 WebSocket / SSE：首期不需要，多人协作后续接。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `DOC_VALIDATE_FAILED` | 文档字段错误 | 表单错误 |
| 400 / `DOC_FILE_TYPE_INVALID` | 文件类型不支持 | 上传错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `DOC_FORBIDDEN` | 无文档权限 | 无权限提示 |
| 404 / `DOC_NOT_FOUND` | 文档不存在 | 刷新列表 |
| 409 / `DOC_VERSION_CONFLICT` | 版本冲突 | 提示刷新 |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 文档列表由接口返回，支持标题、描述、状态、版本、更新时间、责任人等字段。
- 文档搜索、状态筛选、标签筛选、分页可用。
- 新建、编辑、删除/归档、版本记录、上传附件和下载有接口支撑。
- AI 摘要、生成提纲、补齐建议可执行并记录结果。
- 文档权限、密级、版本冲突和审计日志有明确规则。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 项目文档内容存储使用 Markdown、富文本还是文件对象？ | 产品/后端 | 待确认 |
| Q2 | 是否需要首期支持多人协同编辑？ | 产品/前端/后端 | 待确认 |
| Q3 | 附件上传大小和支持类型限制是多少？ | 后端/安全 | 待确认 |
| Q4 | AI 摘要是否自动保存为文档字段，还是作为独立摘要记录？ | 产品/AI/后端 | 待确认 |

## 17. 前端备注

- 当前主承载数据在 `ProjectDetail.vue` 的 `docList` 和 AI 文档建议。
- `ProjectDocs.vue` 当前是固定 `currentTab = 'docs'` 的独立占位页，未在路由中单独挂载。
- 当前文档页只展示卡片和空状态，新建、编辑、版本、AI 摘要均未接接口。
