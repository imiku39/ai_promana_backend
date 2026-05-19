# 后端 API 文件依赖关系图

> 记录时间：2026-05-19  
> 适用仓库：`C:\Users\34395\Desktop\ai_manager_backend-master`  
> 目的：后续对 API 做增删、合并、改名、落库时，先按本文档确认文件依赖和影响范围。

## 1. 当前结论

- 当前后端是 `FastAPI + PyMySQL + Pydantic`，入口是 `main.py`。
- 当前没有形成 service/repository 分层，大多数接口直接写在 `api/v1/endpoints/*.py` 中。
- 当前真实数据库访问主要集中在 `users.py`，其余业务模块多数使用 `_mock.py` 返回联调用 mock 数据。
- `database_setup.py` 是当前建表与补列入口，包含 `TABLE_SQL`、`INDEX_DEFINITIONS`、`columns_to_add` 三层结构。
- 代码当前可以通过语法检查和 OpenAPI 生成：
  - `python -B -m compileall -q database_setup.py main.py src\ai_promana_backend`
  - `import main; main.app.openapi()` 生成成功，当前 OpenAPI 约 203 个 path，应用内 APIRoute 约 233 条。
- 当前接口明显偏多，主要冗余集中在 `/api/auth`、`/api/settings`、`/api/admin`、`/api/projects`、`/api/ai` 这些共享前缀。

## 2. 入口与启动链路

```text
main.py
  ├─ 创建 FastAPI app
  ├─ 注册 CORS 中间件
  ├─ include_router(api_v1_router)
  │    └─ api_v1_router 来自 src/ai_promana_backend/api/v1/routes.py
  └─ GET / 健康检查
```

`main.py` 依赖：

- `ai_promana_backend.api.v1.routes.router`
- `ai_promana_backend.config.settings`
- `fastapi.FastAPI`
- `fastapi.middleware.cors.CORSMiddleware`

启动参数来源：

- `settings.APP_HOST`
- `settings.APP_PORT`
- `settings.DEBUG`

## 3. 配置、数据库、认证公共依赖

| 文件 | 作用 | 被哪些模块依赖 | 当前风险 |
| --- | --- | --- | --- |
| `src/ai_promana_backend/config.py` | 读取 `.env`，提供 MySQL、JWT、App 配置 | `main.py`、`database.py`、`security.py`、`database_setup.py` | `.env` 中 MySQL 密码错误会导致初始化和真实 DB 接口失败 |
| `src/ai_promana_backend/database.py` | 提供 `get_connection()` 和 FastAPI 依赖 `get_db()` | `users.py` | 当前只有少量真实落库接口使用 |
| `src/ai_promana_backend/core/security.py` | 密码哈希、JWT 签发、JWT 解析 | `users.py`、`system_settings.py` | settings 里的 `SECRET_KEY` 仍是默认占位值，需要部署时替换 |
| `src/ai_promana_backend/core/dependencies.py` | 预留依赖文件 | 暂无实际内容 | 后续可放当前用户、权限校验、分页等公共依赖 |
| `src/ai_promana_backend/middleware/*.py` | 预留中间件文件 | 当前没有在 `main.py` 注册 | 后续操作日志、请求追踪要先接入 `main.py` |

## 4. 路由聚合文件

核心文件：`src/ai_promana_backend/api/v1/routes.py`

```text
router
  ├─ api_router: prefix="/api"
  └─ v1_router: prefix="/api/v1"
```

`/api` 是当前主接口前缀，`/api/v1` 目前挂载用户登录接口：

- `/api/v1/users/login`

后续删除或改名接口时，必须先检查 `routes.py` 中的 `include_router(...)` 是否还挂着对应 router。

## 5. Endpoint 模块关系总览

| 模块 | Router 变量 | 挂载前缀 | 主要接口范围 | 当前数据来源 | 建议对应表 |
| --- | --- | --- | --- | --- | --- |
| `users.py` | `router`, `auth_router` | `/api/v1/users`, `/api/auth` | 登录、当前用户、刷新 | `users` 表 + `_mock` 兜底 | `users`, `user_sessions` |
| `daily_reports.py` | `router`, `dashboard_router`, `project_router`, `reports_router`, `ai_router` | `/api/ai/daily-report`, `/api/dashboard`, `/api/projects`, `/api/reports`, `/api/ai` | 工作台、日报、项目报表、全局报表、AI 报表建议 | `_mock` | `daily_reports`, `report_subscriptions`, `projects`, `tasks` |
| `projects.py` | `router`, `ai_router` | `/api/projects`, `/api/ai` | 项目列表、详情、创建、编辑、归档、基线、AI 项目建议 | `_mock` | `projects`, `baseline_versions`, `project_members` |
| `project_members.py` | `router`, `ai_router` | `/api/projects`, `/api/ai` | 项目成员、候选成员、邀请、移除、AI 成员建议 | `_mock` | `project_members`, `users`, `user_workload` |
| `tasks.py` | `router`, `project_router`, `ai_router` | `/api/tasks`, `/api/projects`, `/api/ai` | 任务详情、评论、子任务、项目看板、AI 任务建议 | `_mock` | `tasks`, `task_comments`, `task_dependencies`, `pbc_objectives` |
| `milestones.py` | `router`, `ai_router` | `/api/projects`, `/api/ai` | 甘特、排期、基线、依赖、AI 排期建议 | `_mock` | `milestones`, `tasks`, `task_dependencies`, `baseline_versions` |
| `risks.py` | `router`, `ai_router` | `/api/projects`, `/api/ai` | 风险列表、风险流转、风险导出 | `_mock` | `risks`, `tasks`, `projects` |
| `documents.py` | `router`, `ai_router` | `/api/projects`, `/api/ai` | 项目文档、版本、附件、下载、导出、AI 摘要 | `_mock` | `documents`, `document_versions`, `document_attachments` |
| `notifications.py` | `router`, `preferences_router`, `ai_router` | `/api/notifications`, `/api/notification-preferences`, `/api/ai` | 通知列表、未读、分类、已读、处理、偏好、AI 通知建议 | `_mock` | `notifications`, `notification_preferences` |
| `system_settings.py` | `settings_router`, `admin_router` | `/api/settings`, `/api/admin` | 个人设置、改密、系统配置、通知通道 | `_mock` | `user_settings`, `user_sessions`, `system_settings`, `system_setting_history` |
| `admin.py` | `router`, `ai_router` | `/api/admin`, `/api/ai` | 后台首页、用户管理、导入用户、后台 AI 建议 | `_mock` | `users`, `roles_permissions`, `operation_logs` |
| `roles_permissions.py` | `router` | `/api/admin` | 权限矩阵、角色模板 | `_mock` | `roles_permissions`, `role_templates` |
| `templates.py` | `router` | `/api/admin` | 项目模板 | `_mock` | `project_templates`, `role_templates`, `projects` |
| `logs.py` | `router` | `/api/admin` | 审计日志列表、详情、导出 | `_mock` | `operation_logs`, `async_jobs` |
| `operation_logs.py` | `router` | `/api/operation-logs` | 操作日志列表 | `_mock` | `operation_logs` |
| `pbc.py` | `router`, `ai_router` | `/api/workbench`, `/api/ai` | 个人工作台、日志、个人看板、PBC 目标、AI 工作台建议 | `_mock` | `pbc_objectives`, `tasks`, `task_comments` |
| `teams.py` | `router` | `/api/teams` | 团队、团队成员 | `_mock` | `teams`, `users` |
| `search.py` | `router` | `/api` | 全局搜索 | `_mock` | 多表搜索 |
| `managments.py` | `router` | `/api/management` | 管理端通用选项 | `_mock` | 选项型配置表或 mock |
| `_mock.py` | 无 router | 无 | 所有 mock 数据和统一响应格式 | 内存常量 | 后续应被 service/repository 替代 |

## 6. 共享依赖文件

### `_mock.py`

当前大多数模块依赖 `_mock.py`：

- 统一响应：`api_response(...)`
- 分页：`paged(...)`
- 导出任务：`export_task(...)`
- 当前用户：`current_user()`
- 静态数据：`users()`、`projects()`、`tasks()`、`members()`、`risks()`、`documents()`、`notifications()`、`role_templates()`、`project_templates()`
- AI 建议：`ai_suggestions(scope)`
- 权限矩阵：`platform_matrix()`、`project_matrix()`

后续真实落库时，不建议继续让 endpoint 直接依赖 `_mock.py`。建议逐步替换为：

```text
endpoints/*.py
  └─ services/*.py
       └─ repositories/*.py 或 database.py
```

### `schemas/user.py`

主要服务用户登录：

- `UserLogin`
- `UserOut`
- `LoginResponse`

### `schemas/request_bodies.py`

当前用于补充 Swagger Request body 示例，已被部分接口引用。

注意：该文件当前覆盖了项目、成员、排期、任务、风险、文档、通知、设置等多类请求体。后续如果删除接口，要同时检查对应模型是否还被引用，避免残留模型越来越多。

## 7. 主要重复和冲突区域

### `/api/auth`

来源：

- `users.auth_router`

当前职责混在一起：

- `users.py` 管登录、当前用户、刷新。
- `system_settings.py` 的改密已并入 `/api/settings/change-password`，不再占用 `/api/auth`。

建议后续整理为：

- `auth.py`：登录、注册、刷新、退出、第三方登录。
- `account_security.py` 或 `settings.py`：改密、设备会话。

### `/api/settings`

来源：

- `system_settings.settings_router`

- `/api/settings/me`
- `/api/settings/reset`
- `/api/settings/defaults`
- `/api/settings/search`

`/api/user/settings/*` 兼容路由已删除，后续仅保留 `/api/settings/*` 作为个人设置入口。

### `/api/admin`

来源：

- `admin.py`
- `system_settings.py`
- `roles_permissions.py`
- `templates.py`
- `logs.py`

当前后台管理接口按页面拆散在多个文件中，但共享同一个 `/api/admin` 前缀。后续调整后台接口时，需要先确认目标接口属于：

- 用户管理：`admin.py`
- 系统配置：`system_settings.py`
- 角色权限：`roles_permissions.py`
- 项目模板：`templates.py`
- 审计日志：`logs.py`

### `/api/projects`

来源：

- `projects.py`
- `project_members.py`
- `tasks.py`
- `milestones.py`
- `risks.py`
- `documents.py`
- `daily_reports.py`

这是当前最复杂的聚合前缀。删除或改名项目子页面接口时，要确认影响范围：

- 项目主信息：`projects.py`
- 成员页：`project_members.py`
- 看板页：`tasks.py`
- 甘特页：`milestones.py`
- 风险页：`risks.py`
- 文档页：`documents.py`
- 报表页：`daily_reports.py`

### `/api/ai`

来源：

- `daily_reports.py`
- `projects.py`
- `project_members.py`
- `tasks.py`
- `milestones.py`
- `risks.py`
- `documents.py`
- `notifications.py`
- `system_settings.py`
- `admin.py`
- `pbc.py`

当前 AI 建议接口分散在各页面文件里，但统一挂到 `/api/ai`。如果后续要简化，可以考虑建立单独的 `ai.py` 或 `ai_suggestions.py`，再用 `scope` 区分页面来源。

## 8. 数据库建表文件关系

核心文件：`database_setup.py`

```text
database_setup.py
  ├─ import pymysql
  ├─ import settings from ai_promana_backend.config
  ├─ TABLE_SQL: 创建主表和辅助表
  ├─ INDEX_DEFINITIONS: 补充索引
  ├─ _index_exists(...)
  ├─ _column_exists(...)
  ├─ _create_index_if_not_exists(...)
  └─ setup_database()
       ├─ 连接 MySQL，不指定 database
       ├─ CREATE DATABASE IF NOT EXISTS settings.MYSQL_DATABASE
       ├─ USE database
       ├─ 执行 TABLE_SQL
       ├─ 执行 columns_to_add 补列
       └─ 执行 INDEX_DEFINITIONS 补索引
```

当前建表文件依赖：

- `pymysql`
- `ai_promana_backend.config.settings`

不要在没有确认 `.env` MySQL 账号密码前直接执行 `database_setup.py`，此前已出现过：

```text
(1045, "Access denied for user 'root'@'localhost' (using password: YES)")
```

这说明 MySQL 服务能连上，但用户名或密码不对。

## 9. 数据表分组

### 用户、认证、设置

- `users`
- `user_sessions`
- `user_settings`
- `notification_preferences`
- `system_settings`
- `system_setting_history`

关联接口：

- `users.py`
- `system_settings.py`
- `notifications.py`

### 项目、成员、任务、排期

- `projects`
- `teams`
- `project_members`
- `tasks`
- `task_dependencies`
- `task_comments`
- `milestones`
- `baseline_versions`
- `user_workload`

关联接口：

- `projects.py`
- `project_members.py`
- `tasks.py`
- `milestones.py`
- `teams.py`
- `pbc.py`

### 风险、文档、报表

- `risks`
- `documents`
- `document_versions`
- `document_attachments`
- `daily_reports`
- `report_subscriptions`

关联接口：

- `risks.py`
- `documents.py`
- `daily_reports.py`

### 管理后台、权限、模板、审计

- `roles_permissions`
- `role_templates`
- `project_templates`
- `operation_logs`
- `system_metrics`

关联接口：

- `admin.py`
- `roles_permissions.py`
- `templates.py`
- `logs.py`
- `operation_logs.py`
- `system_settings.py`

### 异步、AI、资源申请

- `async_jobs`
- `ai_suggestion_logs`
- `compute_requests`
- `pbc_objectives`

关联接口：

- `daily_reports.py`
- `documents.py`
- `notifications.py`
- `projects.py`
- `pbc.py`
- 后续所有导入、导出、AI 建议采纳接口

## 10. 完整路由分布索引

### `users.py`

- `GET /api/auth/me`
- `POST /api/auth/refresh`
- `POST /api/v1/users/login`

### `daily_reports.py`

- `GET /api/dashboard/overview`
- `POST /api/dashboard/morning-report/export`
- `POST /api/ai/daily-report/generate`
- `GET /api/ai/daily-report/latest`
- `GET /api/projects/{projectId}/reports/page-data`
- `GET /api/projects/{projectId}/reports/options`
- `GET /api/projects/{projectId}/reports/overview`
- `GET /api/projects/{projectId}/reports/ai-insight`
- `GET /api/projects/{projectId}/reports/burndown`
- `GET /api/projects/{projectId}/reports/work-hours`
- `GET /api/projects/{projectId}/reports/bugs`
- `POST /api/projects/{projectId}/reports/export`
- `POST /api/projects/{projectId}/reports/subscriptions`
- `GET /api/reports/global/overview`
- `GET /api/reports/global/project-health`
- `GET /api/reports/global/options`
- `POST /api/reports/global/export`
- `POST /api/reports/global/subscriptions`
- `GET /api/reports/global/subscriptions`
- `GET /api/reports/overview`
- `GET /api/reports/options`
- `GET /api/ai/report-suggestions`
- `POST /api/ai/feedback`
- `GET /api/ai/global-report-suggestions`
- `POST /api/ai/global-report-weekly`
- `POST /api/ai/global-report-suggestions/{suggestionId}/apply`

### `projects.py`

- `GET /api/projects/summary`
- `GET /api/projects`
- `GET /api/projects/create-options`
- `POST /api/projects/drafts`
- `POST /api/projects`
- `GET /api/projects/{projectId}`
- `GET /api/projects/{projectId}/overview`
- `GET /api/projects/{projectId}/edit-form`
- `PUT /api/projects/{projectId}`
- `POST /api/projects/{projectId}/draft`
- `POST /api/projects/{projectId}/archive`
- `POST /api/projects/{projectId}/baseline`
- `GET /api/ai/project-matrix-suggestions`
- `POST /api/ai/project-suggestions/{suggestionId}/apply`

### `project_members.py`

- `GET /api/projects/{projectId}/members/page-data`
- `GET /api/projects/{projectId}/members/summary`
- `GET /api/projects/{projectId}/members`
- `GET /api/projects/{projectId}/members/workload-heatmap`
- `GET /api/projects/{projectId}/member-candidates`
- `POST /api/projects/{projectId}/member-invitations`
- `PATCH /api/projects/{projectId}/members/{memberId}`
- `DELETE /api/projects/{projectId}/members/{memberId}`
- `GET /api/ai/project-member-suggestions`
- `POST /api/ai/project-member-suggestions/{suggestionId}/apply`

### `tasks.py`

- `POST /api/tasks/drafts`
- `POST /api/tasks`
- `GET /api/tasks/{taskId}`
- `PUT /api/tasks/{taskId}`
- `PATCH /api/tasks/{taskId}`
- `DELETE /api/tasks/{taskId}`
- `GET /api/tasks/{taskId}/transition-options`
- `POST /api/tasks/{taskId}/transition`
- `GET /api/tasks/{taskId}/comments`
- `POST /api/tasks/{taskId}/comments`
- `DELETE /api/tasks/{taskId}/comments/{commentId}`
- `POST /api/tasks/{taskId}/subtasks`
- `PATCH /api/tasks/{taskId}/subtasks/{subtaskId}`
- `DELETE /api/tasks/{taskId}/subtasks/{subtaskId}`
- `GET /api/projects/{projectId}/kanban/summary`
- `GET /api/projects/{projectId}/kanban`
- `GET /api/projects/{projectId}/kanban/flow-rules`
- `GET /api/projects/{projectId}/kanban/options`
- `GET /api/projects/{projectId}/kanban/page-data`
- `POST /api/projects/{projectId}/tasks`
- `PUT /api/projects/{projectId}/tasks/{taskId}`
- `POST /api/projects/{projectId}/tasks/{taskId}/transition`
- `PATCH /api/projects/{projectId}/kanban/order`
- `GET /api/ai/project-kanban-suggestions`
- `POST /api/ai/project-kanban-suggestions/{suggestionId}/apply`
- `GET /api/ai/task-suggestions`
- `POST /api/ai/task-suggestions/{suggestionId}/apply`
- `GET /api/ai/tasks/{taskId}/suggestions`
- `POST /api/ai/tasks/{taskId}/suggestions/{suggestionId}/apply`

### `milestones.py`

- `GET /api/projects/{projectId}/gantt/summary`
- `GET /api/projects/{projectId}/gantt`
- `GET /api/projects/{projectId}/gantt/page-data`
- `PATCH /api/projects/{projectId}/schedule/items/{itemId}`
- `GET /api/projects/{projectId}/baselines`
- `GET /api/projects/{projectId}/dependencies`
- `PUT /api/projects/{projectId}/dependencies`
- `GET /api/ai/project-schedule-suggestions`
- `POST /api/ai/project-schedule-suggestions/{suggestionId}/apply`

### `risks.py`

- `GET /api/projects/{projectId}/risks/summary`
- `GET /api/projects/{projectId}/risks/options`
- `GET /api/projects/{projectId}/risks`
- `POST /api/projects/{projectId}/risks`
- `PUT /api/projects/{projectId}/risks/{riskId}`
- `POST /api/projects/{projectId}/risks/{riskId}/transition`
- `POST /api/projects/{projectId}/risks/batch-resolve`
- `POST /api/projects/{projectId}/risks/export`
- `POST /api/ai/project-risk-insights/{insightId}/apply`

### `documents.py`

- `GET /api/projects/{projectId}/docs/summary`
- `GET /api/projects/{projectId}/docs/options`
- `GET /api/projects/{projectId}/docs/page-data`
- `GET /api/projects/{projectId}/docs`
- `GET /api/projects/{projectId}/docs/{docId}`
- `GET /api/projects/{projectId}/docs/{docId}/versions`
- `POST /api/projects/{projectId}/docs`
- `PUT /api/projects/{projectId}/docs/{docId}`
- `DELETE /api/projects/{projectId}/docs/{docId}`
- `POST /api/projects/{projectId}/docs/{docId}/attachments`
- `GET /api/projects/{projectId}/docs/{docId}/download`
- `POST /api/projects/{projectId}/docs/{docId}/export`
- `POST /api/ai/project-docs/{docId}/summary`
- `GET /api/ai/project-doc-suggestions`
- `POST /api/ai/project-doc-suggestions/{suggestionId}/apply`

### `notifications.py`

- `GET /api/notifications/unread-count`
- `GET /api/notifications/summary`
- `GET /api/notifications/categories`
- `GET /api/notifications`
- `POST /api/notifications/read-batch`
- `GET /api/notifications/process-advice`
- `GET /api/notifications/entry-guide`
- `POST /api/notifications/export`
- `GET /api/notifications/{notificationId}`
- `POST /api/notifications/{notificationId}/read`
- `POST /api/notifications/{notificationId}/handle`
- `GET /api/notification-preferences/me`
- `PUT /api/notification-preferences/me`
- `GET /api/ai/notification-suggestions`
- `POST /api/ai/notification-suggestions/{suggestionId}/apply`

### `system_settings.py`

- `GET /api/settings/me`
- `PUT /api/settings/me`
- `POST /api/settings/reset`
- `GET /api/settings/defaults`
- `GET /api/settings/search`
- `POST /api/settings/change-password`
- `GET /api/admin/system-config`
- `PUT /api/admin/system-config`
- `POST /api/admin/system-config/reset`
- `GET /api/admin/system-config/defaults`
- `GET /api/admin/system-config/history`
- `GET /api/admin/notification-channels`
- `PUT /api/admin/notification-channels`

### `admin.py`

- `GET /api/admin/overview`
- `GET /api/admin/users`
- `GET /api/admin/users/options`
- `GET /api/admin/users/create-options`
- `POST /api/admin/users`
- `PATCH /api/admin/users/{userId}`
- `PUT /api/admin/users/{userId}`
- `GET /api/admin/users/import/template`
- `POST /api/admin/users/import/preview`
- `POST /api/admin/ai-suggestions/{suggestionId}/apply`
- `POST /api/admin/ai-suggestions/{suggestionId}/defer`
- `GET /api/ai/admin-suggestions`
- `POST /api/ai/admin-suggestions/{suggestionId}/apply`
- `GET /api/ai/ai-suggestions`
- `POST /api/ai/ai-suggestions/{suggestionId}/apply`
- `POST /api/ai/ai-suggestions/{suggestionId}/defer`

### `roles_permissions.py`

- `GET /api/admin/roles/overview`
- `GET /api/admin/roles/summary-permissions`
- `GET /api/admin/permission-matrix`
- `POST /api/admin/permission-matrix/export`
- `GET /api/admin/role-templates`
- `GET /api/admin/role-templates/options`
- `GET /api/admin/role-templates/export`
- `POST /api/admin/role-templates/import`
- `GET /api/admin/role-templates/{templateId}`
- `POST /api/admin/role-templates`
- `PUT /api/admin/role-templates/{templateId}`
- `POST /api/admin/role-templates/copy`
- `POST /api/admin/role-templates/{templateId}/copy`

### `templates.py`

- `GET /api/admin/project-templates`
- `GET /api/admin/project-templates/options`
- `GET /api/admin/project-templates/export`
- `POST /api/admin/project-templates/import`
- `GET /api/admin/project-templates/{templateId}/delete-check`
- `GET /api/admin/project-templates/{templateId}`
- `POST /api/admin/project-templates`
- `PUT /api/admin/project-templates/{templateId}`
- `DELETE /api/admin/project-templates/{templateId}`

### `logs.py`

- `GET /api/admin/logs`
- `GET /api/admin/logs/options`
- `GET /api/admin/logs/export`
- `POST /api/admin/logs/export`
- `GET /api/admin/logs/{logId}/export`
- `GET /api/admin/logs/{logId}`

### `pbc.py`

- `GET /api/workbench/overview`
- `GET /api/workbench/logs/today`
- `PUT /api/workbench/logs/today`
- `GET /api/workbench/logs/interactions`
- `GET /api/workbench/kanban`
- `GET /api/workbench/pbc`
- `POST /api/workbench/pbc/{goalId}/bind-tasks`
- `GET /api/workbench/task-create-options`
- `GET /api/workbench/pbc-objectives`
- `POST /api/workbench/pbc-objectives`
- `POST /api/ai/workbench/log-draft`
- `GET /api/ai/workbench-suggestions`
- `POST /api/ai/workbench-suggestions/{suggestionId}/apply`

### 其他模块

- `GET /api/search` 来自 `search.py`
- `GET /api/teams` 来自 `teams.py`
- `GET /api/teams/{teamId}/members` 来自 `teams.py`
- `GET /api/operation-logs` 来自 `operation_logs.py`
- `GET /api/management/options` 来自 `managments.py`
- `GET /` 来自 `main.py`

## 11. 后续改动规则

### 删除接口前

1. 在 `routes.py` 确认所属 router 是否仍需挂载。
2. 在对应 endpoint 文件删除路由函数。
3. 检查是否有专用 Pydantic 请求体模型可删除。
4. 检查 `_mock.py` 是否有只服务该接口的静态数据或 helper。
5. 检查 `database_setup.py` 中是否已有表或字段只服务该接口。
6. 重新生成 OpenAPI，确认 path 数量变化符合预期。

### 合并接口前

1. 优先合并同语义重复接口，保留一组正式路径。
2. 对已删除的兼容路径直接清理，不再新增转调封装。
3. 保留前端仍在使用的一组正式路径。
4. 新增接口时优先挂到既有文件的标准前缀下。

### 新增真实数据库接口前

1. 先确认 `database_setup.py` 是否已有表和字段。
2. 如果已有表但字段不够，优先在 `columns_to_add` 追加补列，不直接破坏原表。
3. endpoint 不建议直接写大量 SQL，建议先新建 service/repository 层。
4. 必须统一返回格式，当前可继续使用 `_mock.api_response(...)`，后续可抽到公共 response helper。

### 拆分模块建议

当前可以逐步拆成：

```text
src/ai_promana_backend/
  api/v1/endpoints/
    auth.py
    settings.py
    projects.py
    project_members.py
    project_tasks.py
    project_schedule.py
    project_risks.py
    project_docs.py
    reports.py
    notifications.py
    admin_users.py
    admin_roles.py
    admin_templates.py
    admin_logs.py
    ai_suggestions.py
  services/
  repositories/
  schemas/
```

短期不必一次性重构，优先处理重复路径和真实落库接口。

## 12. 当前需要特别注意的问题

- 工作区当前有未提交改动，本文档以当前文件内容为准。
- `schemas/request_bodies.py` 是当前新增的请求体集中模型文件，后续如果决定重构接口，需要一起维护。
- 部分旧注释或 Pydantic `description` 存在编码乱码，不影响语法检查，但会影响 Swagger 可读性。
- `users.py` 同时存在真实 DB 逻辑和 mock 兜底逻辑，后续登录注册要优先统一。
- `database_setup.py` 没有显式外键约束，主要靠字段名和索引表达关系；后续改库时要注意业务层一致性。

---

## 13. 接口删减追踪 (2026-05-19)

> **说明**：已执行删除的项标注 ~~删除线~~，后续任务清单中**不应再次出现**已删除项。
> ⚠️ **重复提示**：部分项在多轮清单中重复，标注 🔁 提醒只删一次。

### 第一轮：邮箱/手机号相关删减

| # | 删除项 | 文件:行号 | 状态 |
|---|--------|-----------|------|
| E1 | `GET /api/auth/register/check-email` 路由 + `check_register_email()` | users.py L433-436 | ⬜ |
| E2 | `_is_email_available()` 函数 | users.py L343-356 | ⬜ |
| E3 | 注册时邮箱/手机号查重逻辑 | users.py L47-57 | ⬜ |
| E4 | `PUT /api/settings/me` 中 email 格式校验 `"@" in email` | system_settings.py L535-536 | ⬜ |
| E5 | `PUT /api/settings/me` 中 phone 格式校验 `_is_phone_like()` | system_settings.py L537-538 | ⬜ |
| E6 | `_is_phone_like()` 函数 | system_settings.py L673-675 | ⬜ |
| E7 | `GET /api/settings/me` 返回体中 profile 的 email/phone 字段 | system_settings.py L30-31 | ⬜ |
| E8 | `POST /api/admin/users` 中 email 校验逻辑 | admin.py L123 | ⬜ |
| E9 | `PATCH /api/admin/users/{userId}` 中 email 校验逻辑 | admin.py L138 | ⬜ |
| E10 | `POST /api/admin/users/import/preview` 中邮箱逐行校验 | admin.py L192 | ⬜ |
| E11 | `GET /api/projects/{id}/members` 中 email 关键字搜索 | project_members.py L132 | ⬜ |
| E12 | `GET /api/projects/{id}/member-candidates` 中 email 关键字搜索 | project_members.py L132 | ⬜ |
| E13 | `GET /api/admin/system-config` 中 `emailSubscription` 配置项 | system_settings.py L452-455 | ⬜ |
| E14 | `GET /api/admin/system-config` 中 `maskSensitiveData` 配置项 | system_settings.py L474-477 | ⬜ |
| E15 | `GET /api/notification-preferences/me` 中 `emailEnabled` / email 通道 | notifications.py L456/L461 | ⬜ |

### 第二轮：用户注册相关删减

| # | 删除项 | 文件:行号 | 状态 |
|---|--------|-----------|------|
| R1 | `POST /api/v1/users/register` 路由 + `register_user()` | users.py | ✅ 已删除 |
| R2 | `POST /api/auth/register` 路由 + `auth_register()` | users.py | ✅ 已删除 |
| R3 | `GET /api/auth/register/config` 路由 + `get_register_config()` | users.py | ✅ 已删除 |
| R4 | `GET /api/auth/register/check-account` 路由 + `check_register_account()` | users.py | ✅ 已删除 |
| R5 | 🔁 `GET /api/auth/register/check-email` → **已被 E1 覆盖** | users.py | ✅ 已确认不存在 |
| R6 | `_register_db_user()` 函数 | users.py | ✅ 已删除 |
| R7 | `_is_account_available()` 函数 | users.py | ✅ 已删除 |
| R8 | 🔁 `_is_email_available()` → **已被 E2 覆盖** | users.py | ✅ 已确认不存在 |
| R9 | `schemas/user.py` 中 `UserCreate` 类 | schemas/user.py | ✅ 已删除 |
| R10 | `schemas/user.py` 中 `AuthRegisterRequest` 类 | schemas/user.py | ✅ 已删除 |

### 重复项提醒

| 重复项 | 第一轮编号 | 第二轮编号 | 执行时 |
|--------|-----------|-----------|--------|
| `check_register_email` 路由 + 函数 | E1 | R5 | **只删一次** |
| `_is_email_available()` 函数 | E2 | R8 | **只删一次** |

### 保留项

- `POST /api/admin/users`（admin.py L123）— 唯一创建用户入口，管理员后台注册
- `POST /api/v1/users/login` — 用户登录（用户名+密码），返回 email/phone
- `GET /api/auth/me` — 获取当前用户信息
- `POST /api/auth/refresh` — 刷新 token
- `POST /api/settings/change-password` — 修改密码
- 注册写入 phone/email 到 users 表的核心 INSERT — 移入 admin.py 的创建用户流程

### 第三轮：登录/第三方/会话接口删减

| # | 删除项 | 文件:行号 | 状态 |
|---|--------|-----------|------|
| L1 | `POST /api/auth/login` + `auth_login()` | users.py L342-353 | ✅ 已删除 |
| L2 | `POST /api/auth/logout` + `logout()` | users.py L442-445 | ✅ 已删除 |
| L3 | `GET /api/auth/providers` + `list_auth_providers()` | users.py L449-456 | ✅ 已删除 |
| L4 | `POST /api/auth/social/start` + `start_social_login()` | users.py L460-471 | ✅ 已删除 |
| L5 | `POST /api/auth/social/confirm` + `confirm_social_login()` | users.py L475-486 | ✅ 已删除 |
| L6 | `_auth_response_payload()` | users.py L168-195 | ✅ 已删除 |
| L7 | `_role_name()` | users.py L198-206 | ✅ 已删除 |
| L8 | `_db_user_to_current_user()` | users.py L218-234 | ✅ 已删除 |
| L9 | `_permissions_for_role()` | users.py L237-240 | ✅ 已删除 |
| L10 | `_find_login_user()` | users.py L243-270 | ✅ 已删除 |
| L11 | `AuthLoginRequest` Schema | schemas/user.py | ✅ 已删除 |
| L12 | `LogoutRequest` Schema | schemas/request_bodies.py | ✅ 已删除 |
| L13 | `SocialLoginStartRequest` Schema | schemas/request_bodies.py | ✅ 已删除 |
| L14 | `SocialLoginConfirmRequest` Schema | schemas/request_bodies.py | ✅ 已删除 |
| L15 | `GET /api/settings/sessions` + `list_sessions()` | system_settings.py L90-92 | ✅ 已删除 |
| L16 | `GET /api/settings/sessions/summary` + `get_sessions_summary()` | system_settings.py L95-97 | ✅ 已删除 |
| L17 | `DELETE /api/settings/sessions/{id}` + `revoke_session()` | system_settings.py L100-102 | ✅ 已删除 |
| L18 | `GET /api/auth/sessions` + `list_auth_sessions()` | system_settings.py L138-140 | ✅ 已删除 |
| L19 | `GET /api/auth/sessions/summary` + `get_auth_sessions_summary()` | system_settings.py L143-145 | ✅ 已删除 |
| L20 | `DELETE /api/auth/sessions/{id}` + `revoke_auth_session()` | system_settings.py L148-150 | ✅ 已删除 |
| L21 | `_sessions()` 辅助函数 | system_settings.py L562-595 | ✅ 已删除 |
| L22 | `_sessions_summary()` 辅助函数 | system_settings.py L597-604 | ✅ 已删除 |
| L23 | `_revoke_session_payload()` 辅助函数 | system_settings.py L607-611 | ✅ 已删除 |

### 第三轮重复检查

| 对比 | 结果 |
|------|------|
| L1~L23 vs E1~E15 | **无重复** |
| L1~L23 vs R1~R10 | **无重复** — R1/R2 是注册接口，L1~L5 是登录/退出/第三方，互不覆盖 |
| L11~L14 vs R9/R10 | **无重复** — 本轮已删除，保留历史记录 |

### 第四轮：冲突/负载/算力接口删减

| # | 删除/修改项 | 文件:行号 | 类型 | 状态 |
|---|-----------|-----------|------|------|
| C1 | `GET /api/projects/{projectId}/risks/resource-heatmap` + 函数 | risks.py L25-40 | 整条删除 | ✅ |
| C2 | `GET /api/projects/{projectId}/risks/page-data` + `get_project_risks_page()` | risks.py L77-130 | 整条删除 | ✅ |
| C3 | `GET /api/ai/project-risk-insights` + `get_project_risk_insights()` | risks.py L139-155 | 整条删除 | ✅ |
| C4 | `GET /api/reports/global/resource-load` + `get_global_resource_load()` | daily_reports.py L229-241 | 整条删除 | ✅ |
| C5 | `GET /api/projects/{projectId}/reports/block-load` + 函数 | daily_reports.py L164-166 | 整条删除 | ✅ |
| C6 | `GET /api/projects/{projectId}/members/page-data` — 删 `heatmap`/`workloadHeatmap` 字段 | project_members.py L47-48 | 保留改 | ✅ |
| C7 | `GET /api/reports/global/overview` — 删 `resourceLoad` 字段 | daily_reports.py L562 | 保留改 | ✅ |
| C8 | `GET /api/reports/global/overview` — 删 `summary.overloadedResourceCount` | daily_reports.py L565 | 保留改 | ✅ |
| C9 | `GET /api/reports/global/overview` — 删 `aiInsight.conflictProjectCount`/`conflictResource` | daily_reports.py L578-579 | 保留改 | ✅ |
| C10 | `GET /api/ai/global-report-suggestions` — 删 QA 资源冲突文案 | daily_reports.py L663-673 | 保留改 | ✅ |
| C11 | `_resource_heatmap()` 辅助函数 | risks.py L309-334 | 整条删除 | ✅ |
| C12 | `_global_resource_load()` 辅助函数 | daily_reports.py L604-637 | 整条删除 | ✅ |
| C13 | `_project_report_block_load()` 辅助函数 | daily_reports.py L525-530 | 整条删除 | ✅ |

### 第四轮重复检查

| 对比 | 结果 |
|------|------|
| C1~C13 vs E1~E15 | **无重复** |
| C1~C13 vs R1~R10 | **无重复** |
| C1~C13 vs L1~L23 | **无重复** |

### 第四轮保留项

- `GET /api/projects/{projectId}/members/workload-heatmap` — 成员负载热力图
- `GET /api/reports/global/overview` — 全局报表总览（已去 resourceLoad/conflict）
- `GET /api/ai/global-report-suggestions` — AI 全局报表建议（已去冲突文案）
- `GET /api/projects/{projectId}/members/page-data` — 成员页聚合（已去 heatmap）
- `_workload_heatmap_rows()`、`_global_project_health()`、`_global_ai_insight()`（已去 conflict 字段）

### 第五轮：配置接口删减

| # | 删除项 | 文件:行号 | 类型 | 状态 |
|---|--------|-----------|------|------|
| S1 | `GET /api/user/settings` + `get_user_settings()` | system_settings.py L90-93 | 整条删除 | ✅ |
| S2 | `PUT /api/user/settings` + `save_user_settings()` | system_settings.py L95-98 | 整条删除 | ✅ |
| S3 | `POST /api/user/settings/reset` + `reset_user_settings()` | system_settings.py L100-103 | 整条删除 | ✅ |
| S4 | `GET /api/user/settings/defaults` + `get_user_settings_defaults()` | system_settings.py L105-108 | 整条删除 | ✅ |
| S5 | `GET /api/user/settings/search` + `search_user_settings()` | system_settings.py L110-113 | 整条删除 | ✅ |
| S6 | `GET /api/admin/system/config/export` + 函数 | system_settings.py L229-238 | 整条删除 | ✅ |
| S7 | `POST /api/admin/system/config/import` + 函数 | system_settings.py L240-250 | 整条删除 | ✅ |
| S8 | `GET /api/admin/system/config/history/export` + 函数 | system_settings.py L252-260 | 整条删除 | ✅ |
| S9 | `GET /api/ai/settings-suggestions` + 函数 | system_settings.py L300-328 | 整条删除 | ✅ |
| S10 | `POST /api/ai/settings-suggestions/{id}/apply` + 函数 | system_settings.py L330-348 | 整条删除 | ✅ |
| S11 | `_settings_suggestion_items()` 辅助函数 | system_settings.py L577-593 | 整条删除 | ✅ |

### 第五轮重复检查

| 对比 | 结果 |
|------|------|
| S1~S11 vs E1~E15 | **无重复** |
| S1~S11 vs R1~R10 | **无重复** |
| S1~S11 vs L1~L23 | **无重复** |
| S1~S11 vs C1~C13 | **无重复** |

### 第五轮保留项

- `/api/settings/*` — 个人设置 5 个接口（含 change-password）
- `/api/admin/system-config` + `/api/admin/system/config` — 系统配置核心（读取/保存/默认/重置/历史）
- `/api/admin/notification-channels` — 通知通道配置
- `/api/notification-preferences/me` — 通知偏好
- `/api/management/options` — 管理端通用选项

### 第六轮：激活/停用用户接口删减

| # | 删除项 | 文件:行号 | 类型 | 状态 |
|---|--------|-----------|------|------|
| A1 | `POST /api/admin/users/{userId}/activate` + `activate_admin_user()` | admin.py L174-176 | 整条删除 | ✅ |
| A2 | `POST /api/admin/users/{userId}/disable` + `disable_admin_user()` | admin.py L179-181 | 整条删除 | ✅ |
| A3 | `PATCH /api/admin/users/{userId}/status` + `update_admin_user_status()` | admin.py L160-172 | 整条删除 | ✅ |
| A4 | `AdminUserStatusRequest` Schema | schemas/request_bodies.py | 整条删除 | ✅ |

### 第六轮重复检查

| 对比 | 结果 |
|------|------|
| A1~A4 vs E1~E15 | **无重复** |
| A1~A4 vs R1~R10 | **无重复** |
| A1~A4 vs L1~L23 | **无重复** |
| A1~A4 vs C1~C13 | **无重复** |
| A1~A4 vs S1~S11 | **无重复** |

### 第六轮保留项

- `_status_label()` — 用户列表/创建/编辑仍在使用
- `_status_type()` — 用户列表/创建/编辑仍在使用
