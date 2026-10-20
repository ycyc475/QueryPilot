# AGENTS.md — 长期编码约束

> 本文档是给后续编码助手（包括 Claude Code）的长期约束，优先级高于单次对话偏好。需求基线见仓库根目录 PRD。

## 1. 需求与范围

- `QueryPilot_对话式数据分析平台_PRD_v0.1.md` 是**唯一需求基线**。需求冲突时以 PRD 为准，并在 `docs/PROGRESS.md` 记录偏差。
- MVP 范围：单组织、单 PostgreSQL 只读分析数据源；自然语言查询、受控 Text-to-SQL、图表、结论、多轮追问。
- 不做（MVP）：数据写入/自动修改、通用 ETL、多数据源联邦、BI 拖拽建模、复杂多租户计费、执行用户任意 SQL。

## 2. 技术栈（PRD §6，非必要不新增组件）

- 前端：Vue 3 + TypeScript + Vite + Element Plus + ECharts（图表）。
- 后端：Java 21 + Spring Boot 3（认证、数据集/元数据管理、会话、审计、API 网关）。
- Agent：Python + FastAPI + LangGraph + SQLGlot（意图、Schema 检索、查询规划、SQL 生成/校验、结论）。
- 数据库：PostgreSQL（元数据/会话库 + 独立演示分析库，分析库用独立只读账号）。
- 部署：Docker Compose + Nginx；测试：JUnit、pytest、Vitest/Playwright；CI：GitHub Actions。

## 3. Text-to-SQL 安全红线（PRD §3/§9/§12）

- **任何**自然语言生成的 SQL 必须经过：受限查询计划 → SQLGlot AST 校验 → 字段/表白名单校验 → 只读检查 → 成本/行数/超时约束，**禁止直接运行未经验证的 SQL**。
- 数据库层面必须有只读账号兜底（仅授予白名单表的 `SELECT`），AST 校验只是防线之一，不能替代数据库权限。
- 用户文本、数据库内容、元数据描述均为不可信输入，不能改变工具权限或系统规则。
- 图表通过受约束 JSON 规格生成、前端映射 ECharts，**不执行模型生成的 JavaScript**。

## 4. 数据真实性

- 模型生成的指标、字段、查询条件、图表规格都必须校验；总结只能依据真实查询结果，**禁止虚构数据/图表**。
- 外部模型 API 暂不可用时，用确定性 Mock 模型支撑端到端联调，不阻塞开发。

## 5. 交付纪律

- 每完成一个模块，提供：启动命令、测试命令、示例数据、验收步骤、已知限制。
- 每批编码后运行测试并更新 `docs/PROGRESS.md`（已完成 / 测试通过 / 未解决 / 下一步）。
- 不编造「测试通过 / 性能指标 / 接口已实现」；未验证一律标注为「未验证」。

## 6. 工程约定

- Monorepo：`backend/`（Java）、`frontend/`（Vue）、`agent/`（Python）、`scripts/`、`docker/`、`docs/`。
- 数据库迁移：元数据库用 Flyway（`backend/src/main/resources/db/migration`）；分析库 schema/角色用 `docker/init/`。
- 凭据只存环境变量 / `secret_ref`，不落明文；日志脱敏。
- 提交信息末尾加 `Co-Authored-By: Claude Code <noreply@anthropic.com>`。
