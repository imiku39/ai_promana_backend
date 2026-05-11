# 项目成员后端需求对接文档

> 模板来源：`docs/backend-requirements/00_backend_requirement_template.md`  
> 对应前端页面：`views/ProjectMembers.vue`，当前主要由 `views/ProjectDetail.vue` 的 `members` tab 承载  
> 页面定位：项目成员、成员负载、邀请流程和 AI 分配建议。

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 页面名称 | 项目成员 |
| 前端路由 | `/project/:id/members` |
| 前端文件 | `src/views/ProjectMembers.vue`、`src/views/ProjectDetail.vue` |
| 所属模块 | 项目管理 / 项目详情 / 成员 |
| 需求状态 | 草稿 |
| 前端负责人 | 待补充 |
| 后端负责人 | 待补充 |
| 创建日期 | 2026-05-11 |
| 更新日期 | 2026-05-11 |

## 2. 页面目标

### 2.1 页面用途

- 展示项目成员列表、角色、加入状态、当前任务数、预估工时和负载率。
- 展示项目成员统计：项目成员数、超阈值负载人数、AI 推荐采纳率。
- 展示邀请流程状态和未来一周成员负载热力图。
- 支持成员邀请、角色调整、移除成员、负载调度和 AI 分配建议采纳。

### 2.2 对接范围

- 项目基础信息复用 `GET /api/projects/{projectId}`。
- 成员列表、统计指标、邀请流程、负载热力图。
- 组织成员搜索、发送邀请、接受/拒绝邀请状态回写。
- 项目角色调整、移除成员、成员负载阈值判断。
- AI 智能分配建议和采纳动作。

### 2.3 关联页面

| 页面 | 关系说明 |
| --- | --- |
| `ProjectDetail.vue` | 当前成员 tab 的主要承载页 |
| `ProjectKanban.vue` | 成员任务数和任务负责人来自看板任务 |
| `ProjectReports.vue` | 负载和采纳率进入报表统计 |
| `Notifications.vue` | 成员邀请和角色变更通知 |

## 3. 角色与权限

| 角色 | 可查看 | 可新增 | 可编辑 | 可删除 | 可导出 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 超级管理员 | 是 | 是 | 是 | 是 | 是 | 全部成员管理 |
| 管理员 | 是 | 是 | 是 | 视权限 | 是 | 组织范围内 |
| 项目负责人 | 是 | 是 | 是 | 是 | 是 | 可管理本项目成员 |
| 项目成员 | 是 | 否 | 否 | 否 | 否 | 查看成员与负载 |
| 协作者 | 是 | 否 | 否 | 否 | 否 | 只读授权成员 |

### 3.1 权限规则

- 页面入口权限：需要 `project:member:read`。
- 按钮级权限：
  - 邀请成员需要 `project:member:invite`。
  - 调整角色需要 `project:member:role:update`。
  - 移除成员需要 `project:member:remove`。
  - 采纳 AI 分配建议需要 `ai:member-suggestion:apply` 和对应任务分配权限。
- 数据范围权限：组织搜索只能返回当前用户有权限邀请的用户。
- 敏感字段脱敏规则：普通成员不返回成员手机号、邮箱、完整排班明细等隐私字段。

## 4. 页面数据总览

### 4.1 首屏加载数据

| 数据块 | 用途 | 是否必需 | 来源接口 | 备注 |
| --- | --- | --- | --- | --- |
| 项目详情头部 | 项目名称、状态、成员数 | 是 | `GET /api/projects/{projectId}` | 与详情页共用 |
| 成员统计 | 三个指标卡 | 是 | `GET /api/projects/{projectId}/members/summary` | 成员数、超载、采纳率 |
| 成员列表 | 成员表格 | 是 | `GET /api/projects/{projectId}/members` | 支持分页和筛选 |
| 邀请流程 | 邀请步骤和状态 | 是 | `GET /api/projects/{projectId}/member-invitations/flow` | 当前静态步骤 |
| 负载热力图 | 未来一周负载 | 是 | `GET /api/projects/{projectId}/members/workload-heatmap` | 按成员/日期 |
| AI 分配建议 | 侧边建议卡 | 否 | `GET /api/ai/project-member-suggestions` | 按项目上下文 |

### 4.2 页面状态

| 状态 | 前端展示 | 后端含义 | 备注 |
| --- | --- | --- | --- |
| loading | 成员列表加载 | 请求处理中 | 局部 loading |
| empty | 暂无成员 | 项目无成员或筛选为空 | 展示邀请入口 |
| error | Toast / 错误占位 | 接口异常 | 标准错误结构 |
| pendingInvite | 待接受 | 邀请未确认 | 成员状态 |
| overloaded | 超阈值负载 | 负载率超过阈值 | 默认阈值 80% |

## 5. 字段模型

### 5.1 成员字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| memberId | string | 是 | 成员行 key | `pm_001` | 项目成员关系 ID |
| userId | string | 是 | 操作参数 | `u_10001` | 用户 ID |
| name | string | 是 | 成员姓名 | `王志强` | 展示名称 |
| avatar | string | 否 | 头像 | `https://...` | 头像地址 |
| department | string | 是 | 部门 | `材料科学部` | 所属部门 |
| role | string | 是 | 项目职责 | `负责人` | 业务角色名称 |
| projectRole | string | 是 | 角色标签 | `pm` | PM / DEV / QA 等 |
| roleLabel | string | 是 | 角色中文 | `PM` | 展示标签 |
| joinStatus | string | 是 | 加入状态 | `joined` | 已加入、待接受 |
| taskCount | number | 是 | 当前任务 | `6` | 当前负责任务数 |
| estimateHours | number | 否 | 预估工时 | `44` | 建议统一小时 |
| estimateDisplay | string | 否 | 预估展示 | `5.5d` | 可前端格式化 |
| loadRate | number | 是 | 负载标签 | `82` | 0-100 |
| loadLevel | string | 是 | 负载样式 | `warning` | neutral/success/warning/danger |
| permissions | string[] | 否 | 行操作 | `["remove"]` | 当前用户对该成员可操作项 |

### 5.2 统计字段

| 字段名 | 类型 | 计算口径 | 前端展示位置 | 备注 |
| --- | --- | --- | --- | --- |
| memberTotal | number | 当前项目有效成员和待接受成员 | 项目成员卡 | 是否含待接受需确认 |
| pendingInviteCount | number | 未接受邀请数 | 项目成员趋势 | 当前展示 2 |
| overloadedCount | number | loadRate > 阈值的人数 | 超阈值负载卡 | 默认 80% |
| aiSuggestionAdoptionRate | number | 本周采纳次数 / AI 建议次数 | AI 推荐采纳率卡 | 百分比 |
| weeklyAdoptionCount | number | 本周采纳次数 | 趋势说明 | 当前展示 6 |

### 5.3 负载热力图字段

| 字段名 | 类型 | 必填 | 前端展示位置 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| userId | string | 是 | 行 key | `u_10001` | 成员 ID |
| name | string | 是 | 行名 | `王志强` | 成员姓名 |
| cells | array | 是 | 周一到周日色块 | `[2,4,5,4,3,1,0]` | 0-5 负载等级 |
| dailyLoads[].date | string | 是 | 日期 | `2026-05-11` | 具体日期 |
| dailyLoads[].loadRate | number | 是 | 负载率 | `86` | 0-100 |

### 5.4 枚举字段

| 枚举名 | 值 | 中文展示 | 颜色/状态样式 | 说明 |
| --- | --- | --- | --- | --- |
| projectRole | `pm` | PM | primary | 项目负责人/管理 |
| projectRole | `dev` | 研发 | tertiary | 研发成员 |
| projectRole | `qa` | QA | success | 测试/质量 |
| joinStatus | `joined` | 已加入 | success | 已接受 |
| joinStatus | `pending` | 待接受 | warning | 邀请中 |
| joinStatus | `rejected` | 已拒绝 | danger | 拒绝邀请 |
| loadLevel | `neutral` | 低负载 | neutral | < 50% |
| loadLevel | `success` | 正常 | success | 50%-70% |
| loadLevel | `warning` | 偏高 | warning | 70%-90% |
| loadLevel | `danger` | 超载 | danger | > 90% |

## 6. 接口清单

| 编号 | 接口名称 | 方法 | 路径 | 用途 | 优先级 |
| --- | --- | --- | --- | --- | --- |
| API-001 | 获取成员统计 | GET | `/api/projects/{projectId}/members/summary` | 指标卡 | P0 |
| API-002 | 获取成员列表 | GET | `/api/projects/{projectId}/members` | 成员表格 | P0 |
| API-003 | 获取负载热力图 | GET | `/api/projects/{projectId}/members/workload-heatmap` | 未来一周热力图 | P0 |
| API-004 | 搜索可邀请成员 | GET | `/api/projects/{projectId}/member-candidates` | 邀请弹窗/搜索 | P1 |
| API-005 | 发送成员邀请 | POST | `/api/projects/{projectId}/member-invitations` | 邀请成员 | P1 |
| API-006 | 调整成员角色 | PATCH | `/api/projects/{projectId}/members/{memberId}` | 角色调整 | P1 |
| API-007 | 移除项目成员 | DELETE | `/api/projects/{projectId}/members/{memberId}` | 移除成员 | P1 |
| API-008 | 获取 AI 成员建议 | GET | `/api/ai/project-member-suggestions` | AI 分配建议 | P1 |
| API-009 | 采纳 AI 成员建议 | POST | `/api/ai/project-member-suggestions/{suggestionId}/apply` | 分配调整 | P1 |

## 7. 接口详情

### API-001 获取成员统计

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/members/summary`
- Auth: 是

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "memberTotal": 12,
    "pendingInviteCount": 2,
    "overloadedCount": 3,
    "overloadThreshold": 80,
    "aiSuggestionAdoptionRate": 67,
    "weeklyAdoptionCount": 6
  }
}
```

### API-002 获取成员列表

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/members`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| keyword | query | string | 否 | `王` | 姓名、部门、角色搜索 |
| role | query | string | 否 | `qa` | 项目角色 |
| joinStatus | query | string | 否 | `pending` | 加入状态 |
| loadLevel | query | string | 否 | `danger` | 负载等级 |
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
        "memberId": "pm_001",
        "userId": "u_10001",
        "name": "王志强",
        "avatar": "https://example.com/avatar.png",
        "department": "材料科学部",
        "role": "负责人",
        "projectRole": "pm",
        "roleLabel": "PM",
        "joinStatus": "joined",
        "joinStatusLabel": "已加入",
        "taskCount": 6,
        "estimateHours": 44,
        "estimateDisplay": "5.5d",
        "loadRate": 82,
        "loadLevel": "warning",
        "permissions": ["role:update", "remove"]
      }
    ],
    "pagination": { "page": 1, "pageSize": 20, "total": 12 }
  }
}
```

### API-003 获取负载热力图

**请求方式**

- Method: `GET`
- Path: `/api/projects/{projectId}/members/workload-heatmap`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| startDate | query | string | 否 | `2026-05-11` | 周开始日期 |
| days | query | number | 否 | `7` | 天数，默认 7 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    "rows": [
      {
        "userId": "u_10001",
        "name": "王志强",
        "cells": [2, 4, 5, 4, 3, 1, 0],
        "dailyLoads": [
          { "date": "2026-05-11", "loadRate": 65, "level": 2 },
          { "date": "2026-05-12", "loadRate": 86, "level": 4 }
        ]
      }
    ]
  }
}
```

### API-005 发送成员邀请

**请求方式**

- Method: `POST`
- Path: `/api/projects/{projectId}/member-invitations`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| userIds | body | string[] | 是 | `["u_10004"]` | 被邀请用户 |
| projectRole | body | string | 是 | `dev` | 项目角色 |
| message | body | string | 否 | `邀请加入项目` | 邀请备注 |
| notifyChannels | body | string[] | 否 | `["in_app","dingtalk"]` | 通知渠道 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "invitationIds": ["invite_001"],
    "createdAt": "2026-05-11T10:40:00+08:00"
  }
}
```

### API-009 采纳 AI 成员建议

**请求方式**

- Method: `POST`
- Path: `/api/ai/project-member-suggestions/{suggestionId}/apply`
- Auth: 是

**请求参数**

| 参数名 | 位置 | 类型 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- | --- |
| suggestionId | path | string | 是 | `sug_member_001` | 建议 ID |
| actionKey | body | string | 是 | `reassign_tasks` | 动作 |
| dryRun | body | boolean | 否 | `false` | 是否仅预览 |

**响应数据**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "applied": true,
    "changedTasks": ["task_001", "task_002"],
    "message": "已将 2 个任务调整给 QA 成员。"
  }
}
```

## 8. 页面交互与接口映射

| 前端交互 | 触发位置 | 调用接口 | 请求参数来源 | 成功反馈 | 失败反馈 |
| --- | --- | --- | --- | --- | --- |
| 进入成员页 | tab 加载 | `GET /members/summary`、`GET /members`、`GET /workload-heatmap` | projectId | 渲染页面 | 错误占位 |
| 搜索成员 | 搜索框 | `GET /members` | keyword | 更新列表 | Toast |
| 点击待接受筛选 | 状态 chip | `GET /members` | joinStatus | 更新列表 | Toast |
| 邀请成员 | 邀请弹窗 | `POST /member-invitations` | 表单 | Toast，刷新列表 | 表单错误 |
| 调整角色 | 成员行菜单 | `PATCH /members/{memberId}` | memberId、role | Toast，刷新行 | Toast |
| 移除成员 | 成员行菜单 | `DELETE /members/{memberId}` | memberId | Toast，刷新列表 | Toast |
| 采纳 AI 分配 | AI 卡片 | `POST /ai/project-member-suggestions/{id}/apply` | suggestionId | Toast，刷新任务和负载 | Toast |

## 9. 表单与校验

| 字段 | 前端控件 | 必填 | 校验规则 | 后端校验 | 错误提示 |
| --- | --- | --- | --- | --- | --- |
| userIds | selector | 是 | 至少 1 个 | 用户存在且可邀请 | 请选择成员 |
| projectRole | select | 是 | 枚举值 | 角色合法 | 请选择项目角色 |
| message | textarea | 否 | 最长 300 字 | 长度合法 | 邀请备注过长 |
| notifyChannels | checkbox | 否 | 枚举数组 | 渠道合法 | 通知渠道无效 |

### 9.1 提交规则

- 是否允许重复提交：不允许。
- 是否需要二次确认：移除成员、批量 AI 调整需要二次确认。
- 是否需要审计日志：需要，邀请、角色调整、移除、AI 采纳都记录。
- 是否需要乐观锁或版本号：角色调整可使用成员关系 `version`。

## 10. 列表、筛选、分页与排序

### 10.1 列表字段

| 列名 | 字段名 | 类型 | 是否支持排序 | 备注 |
| --- | --- | --- | --- | --- |
| 成员 | name | string | 否 | 支持搜索 |
| 部门 | department | string | 否 | 支持筛选可选 |
| 项目角色 | projectRole | string | 是 | PM/研发/QA |
| 加入状态 | joinStatus | string | 是 | 已加入/待接受 |
| 当前任务 | taskCount | number | 是 | 任务数 |
| 预估工时 | estimateHours | number | 是 | 小时 |
| 负载 | loadRate | number | 是 | 0-100 |

### 10.2 筛选条件

| 筛选项 | 参数名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| 关键词 | keyword | string | 空 | 搜索成员、部门、角色 |
| 项目角色 | role | string | all | pm/dev/qa |
| 加入状态 | joinStatus | string | all | joined/pending |
| 负载等级 | loadLevel | string | all | neutral/success/warning/danger |

### 10.3 分页规则

- 默认页大小：20。
- 最大页大小：100。
- 默认排序：项目角色权重、加入状态、负载率倒序。

## 11. 文件、导入、导出

| 功能 | 接口 | 文件类型 | 大小限制 | 处理方式 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 导出成员负载 | `POST /api/projects/{projectId}/members/export` | xlsx / csv | 不适用 | 异步任务 | P2 |
| 批量导入成员 | `POST /api/projects/{projectId}/members/import` | xlsx / csv | 待确认 | 上传并预览 | P2 |

## 12. 通知、消息与 AI 能力

| 能力 | 是否需要后端 | 接口/服务 | 说明 |
| --- | --- | --- | --- |
| 站内通知 | 是 | 通知中心服务 | 成员邀请、移除、角色变更 |
| AI 分配建议 | 是 | AI 建议服务 | 负载平衡、任务转派 |
| 审计日志 | 是 | 审计日志服务 | 成员管理操作 |
| WebSocket / SSE | 可选 | 项目事件流 | 实时展示邀请接受状态 |

## 13. 缓存与实时性

- 数据是否允许缓存：成员列表可短缓存 30 秒；邀请状态应刷新。
- 缓存时间：负载热力图 60 秒。
- 页面返回时是否刷新：建议刷新成员列表、统计、热力图。
- 是否需要轮询：邀请状态可 30 秒轮询或页面返回刷新。
- 是否需要 WebSocket / SSE：首期不必需，后续可用于邀请状态实时更新。

## 14. 错误码约定

| 错误码 | 含义 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 400 / `PROJECT_MEMBER_VALIDATE_FAILED` | 参数错误 | 表单错误 |
| 401 / `AUTH_TOKEN_EXPIRED` | 未登录 | 跳转登录 |
| 403 / `PROJECT_MEMBER_FORBIDDEN` | 无成员页权限 | 无权限提示 |
| 404 / `PROJECT_NOT_FOUND` | 项目不存在 | 返回列表 |
| 404 / `USER_NOT_FOUND` | 用户不存在 | 表单错误 |
| 409 / `PROJECT_MEMBER_EXISTS` | 成员已存在 | 提示已加入 |
| 409 / `PROJECT_OWNER_REMOVE_DENIED` | 不能移除唯一负责人 | Toast |
| 429 / `AI_RATE_LIMITED` | AI 请求频繁 | 稍后重试 |
| 500 / `COMMON_SERVER_ERROR` | 服务异常 | Toast |

## 15. 验收标准

- 成员页统计、列表、邀请流程和负载热力图均由接口返回。
- 成员列表字段完整支持头像、部门、角色、加入状态、任务数、预估工时、负载率。
- 邀请成员、调整角色、移除成员有明确接口和权限控制。
- AI 分配建议能返回建议、置信度和可采纳动作，采纳后刷新任务和负载。
- 待接受、超载、无权限、重复邀请等异常有明确错误码。

## 16. 待确认问题

| 编号 | 问题 | 负责人 | 状态 |
| --- | --- | --- | --- |
| Q1 | 成员数是否包含待接受成员？ | 产品/后端 | 待确认 |
| Q2 | 成员负载的计算口径是任务工时、日历排班还是综合权重？ | 产品/后端 | 待确认 |
| Q3 | 邀请通知渠道是否包含企微/钉钉/邮件？ | 产品/后端 | 待确认 |
| Q4 | 项目角色枚举是否固定为 PM/研发/QA，还是支持模板自定义？ | 产品/后端 | 待确认 |

## 17. 前端备注

- 当前主承载数据在 `ProjectDetail.vue` 的 `memberList`、`inviteSteps`、`heatmap`、`loads`。
- `ProjectMembers.vue` 当前是固定 `currentTab = 'members'` 的独立占位页，未在路由中单独挂载。
- 当前成员行更多菜单、邀请流程、AI 一键采纳均未接真实接口。
- 当前通知角标静态为 `5`。
