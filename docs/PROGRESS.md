# QueryPilot 开发进度

> 需求基线：根目录 `QueryPilot_对话式数据分析平台_PRD_v0.1.md`。本文件每批编码后更新。

## 当前阶段：第二阶段（语义元数据）— ✅ 已完成

阶段目标（PRD §11 阶段2）：Schema 扫描、指标口径、权限白名单、召回接口 → 「能找到与业务问题关联的表字段」。

| 批次 | 内容 | 状态 | 验证 |
|---|---|---|---|
| B6 | 元数据实体/仓库 + Flyway V4（synonyms）+ `/api/datasets/{id}/schema` | ✅ | 7 测试通过；e2e 返回 5 表/31 字段/4 关系/3 指标（含同义词） |
| B7 | 召回接口 `/api/datasets/{id}/semantic-search` | ✅ | 「实付销售额」→paid_amount+指标；「省份」→province；「华东地区」→region |
| B8 | Schema 扫描（`scripts/schema_scan.py` 核对/同步） | ✅ | 5 表一致，无缺失/多余 |
| B9 | 管理员语义编辑（PUT /api/admin/*）+ ADMIN 权限 | ✅ | demo(ANALYST)→403，admin→200 |

## 第一阶段（基础工程）— ✅ 已完成

阶段目标（PRD §11 阶段1）：前后端脚手架、登录、数据库、模拟电商数据 → 「页面可登录、可查询数据集」。

| 批次 | 内容 | 状态 | 验证结果 |
|---|---|---|---|
| B0 | 仓库/目录/Docker Compose/分析库 DDL/只读账号 | ✅ | 两库就绪；5 表归属 qp_analysis；只读账号 SELECT 通过、INSERT 被拒 |
| B1 | 后端脚手架 + Flyway 迁移 + 目录元数据种子 | ✅ | 元库 11 表 + 种子（1 源/1 数据集/5 表/31 列/4 关系/3 指标） |
| B2 | 用户认证（JWT/BCrypt/login/me）+ 种子账号 | ✅ | 5 单测；e2e：login→token、me→用户、错误密码/无 token→401 |
| B3 | 数据集接口 `/api/datasets` | ✅ | 6 单测；e2e 带 token 返回电商数据集、无 token→401 |
| B4 | 模拟电商数据种子脚本（固定随机种子，幂等） | ✅ | 8 类/40 商品/5000 客户/60000 订单/121627 明细；30 天趋势、省份 TOP10 查询正常 |
| B5 | 前端脚手架 + 登录页 + 数据集列表 | ✅ | `npm run build` 通过；dev 代理全栈联通（登录→数据集） |

## 第一阶段验收（PRD §11 阶段1「页面可登录、可查询数据集」）

- ✅ 登录：`POST /api/auth/login` + 前端登录页；错误密码 / 无 token 均返回 401（JSON envelope）。
- ✅ 查询数据集：`GET /api/datasets` + 前端数据集卡片（含数据源信息）。
- ✅ 数据库：元库 11 张表（Flyway V1–V3）+ 分析库 5 张业务表 + 只读账号 `qp_analysis_ro`（`statement_timeout=30s`、`default_transaction_read_only=on`）。
- ✅ 模拟电商数据：确定性（固定种子）、可复现、口径一致（实付销售额 = `status='paid'` 的 `SUM(paid_amount)`）。

## 测试通过

- **后端** `./mvnw test`：6 个测试全绿（上下文加载、AuthController、JwtService、DatasetController）。
- **后端 e2e**：login→token、me→用户、错误密码 401、无 token 401、datasets 返回数据。
- **前端** `npm run build`：`vue-tsc --noEmit` 类型检查 + `vite build` 均通过。
- **数据**：只读账号可查询、写入被拒；30 天每日趋势、省份 TOP10 等 PRD 典型查询可执行。

## 未解决 / 风险

- **版本偏差**：PRD 写「Spring Boot 3」，采用 **Spring Boot 3.5.16**（满足 PRD；Initializr 默认已 4.x，Maven Central 仍提供 3.5.16）。
- **本机环境坑**：Anaconda `cygpath` 覆盖 MSYS2 的 → Maven 需 `PATH=/usr/bin:$PATH JAVA_HOME=/d/JavaJdk` 前缀；Docker Hub 直连超时已配镜像加速。详见记忆 `dev-environment-quirks`。
- **前端 TS 固定 5.x**：最新 TypeScript 7 与 `vue-tsc` 3.3 不兼容（`./lib/tsc` 导出移除），已固定 `typescript@5`。
- **前端 bundle 偏大**：element-plus 全量引入约 866KB；后续可改按需引入或 auto-import。
- `docker/init` 脚本仅首次初始化数据卷时执行，改动需 `docker compose down -v` 重建。
- 本机无全局 Maven/psql：后端用 Maven Wrapper，DB 校验用容器内 psql。

## 第二阶段验收（PRD §11 阶段2「能找到与业务问题关联的表字段」）

- ✅ 元数据读取：`GET /api/datasets/{id}/schema` 返回授权可见的 5 表/31 字段/4 关系/3 指标（含同义词）。
- ✅ 召回：`GET /api/datasets/{id}/semantic-search?q=实付销售额` → 命中「实付销售额」指标 + `orders.paid_amount`；「省份」→ `customers.province`；「华东地区」→ `customers.region`。
- ✅ Schema 扫描：`python scripts/schema_scan.py` 核对分析库↔元库，5 表一致无差异；`--sync` 可补种缺失项。
- ✅ 管理员编辑：`PUT /api/admin/metrics/{id}`、`PUT /api/admin/columns/{id}`；ADMIN 角色才可访问（demo/ANALYST 返回 403）。
- ✅ 白名单：召回与 schema 只返回 `is_accessible=true` 的表。

## 下一步（第三阶段：Text-to-SQL，PRD §11 阶段3）

1. 查询计划（Query Plan）：意图/指标/维度/过滤/时间范围的结构化建模。
2. SQL 生成（SQLGlot）+ 安全校验（AST、表白名单、只读、多语句/危险函数拒绝、行数/超时限制）。
3. 只读执行（复用 `qp_analysis_ro` 账号）+ 错误分类与受限修复。
