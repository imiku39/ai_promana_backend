# Endpoints 目录标准

`src/ai_promana_backend/api/v1/endpoints` 是当前后端接口的统一标准目录。

## 规则

- 所有接口新增、修改、删除，优先落在对应的 endpoint 模块中。
- `routes.py` 只负责聚合和挂载，不承载业务逻辑。
- 接口入参、返回体、约束和示例，统一放在 `schemas` 与对应 endpoint 中维护。
- 任何接口变化后，同步更新这里的模块索引和 `docs/backend-api-file-dependency-map.md`。

## 模块索引

| 模块 | 主要职责 |
| --- | --- |
| `admin.py` | 后台首页、用户管理、导入、AI 建议 |
| `daily_reports.py` | 工作台、日报、项目报表、全局报表 |
| `documents.py` | 项目文档、版本、附件、导出 |
| `logs.py` | 审计日志列表、详情、导出 |
| `managments.py` | 管理选项 |
| `milestones.py` | 项目排期、甘特、基线 |
| `notifications.py` | 通知、偏好、AI 通知建议 |
| `operation_logs.py` | 操作日志 |
| `pbc.py` | 个人工作台、日志、PBC 目标 |
| `project_members.py` | 项目成员、邀请、候选成员 |
| `projects.py` | 项目列表、详情、创建、编辑、归档 |
| `risks.py` | 风险列表、流转、导出 |
| `roles_permissions.py` | 权限矩阵、角色模板 |
| `search.py` | 全局搜索 |
| `system_settings.py` | 个人设置、账户安全、系统配置 |
| `tasks.py` | 任务、看板、评论、子任务 |
| `teams.py` | 团队和成员 |
| `templates.py` | 项目模板 |
| `users.py` | 登录、当前用户、刷新 |

## 维护顺序

1. 先改对应 endpoint 模块。
2. 再改 `__init__.py` 的导入与导出。
3. 再改 `routes.py` 的挂载。
4. 最后改依赖关系文档与后端需求文档。
