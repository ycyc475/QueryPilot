# 第一阶段实施方案（归档）

> 对应 PRD §11「阶段 1. 基础工程」。目标：前后端脚手架、登录、数据库、模拟电商数据；交付标志「页面可登录、可查询数据集」。

## 范围

- 做：工程脚手架、Docker Compose、元数据库 11 表（Flyway）、用户认证 + 种子账号、`/api/datasets`、模拟电商分析库 + 只读账号 + 确定性种子数据。
- 不做：Agent/LangGraph/Text-to-SQL/图表/SSE/会话与审计接口（表先建，接口后续阶段）。

## 目录结构

```
backend/    Java 21 + Spring Boot 3（Maven Wrapper，com.querypilot）
frontend/   Vue3+TS+Vite+Element Plus+Pinia+Router+Axios
agent/      Python FastAPI+LangGraph（Phase 3-4，占位）
scripts/    seed_ecommerce.py（固定随机种子）
docker/     docker-compose.yml + init/（角色/库 + 分析库 DDL）
docs/       PROGRESS.md / phase-1-plan.md
```

## 数据库

- 元库 `querypilot_meta`（owner `qp_meta`，Flyway V1–V3）：
  - V1 `auth_catalog`：users、data_sources、datasets、schema_tables、schema_columns、schema_relations、business_metrics
  - V2 `conversations_runs`：conversations、messages、query_runs、audit_logs
  - V3 目录元数据 + 指标口径种子
- 分析库 `querypilot_analysis`（owner `qp_analysis`，只读账号 `qp_analysis_ro`）：categories、products、customers、orders、order_items。
- 只读账号：`qp_analysis_ro` 仅 `SELECT` 白名单表 + `statement_timeout=30s` + `default_transaction_read_only=on`。

## 接口

- `POST /api/auth/login`、`GET /api/auth/me`、`GET /api/datasets`、`GET /api/health`。

## 默认决策

- 后端 Maven Wrapper；前端 npm；JWT HS256（`JWT_SECRET`，12h）；BCrypt 密码哈希。
- 演示账号：`admin@querypilot.dev / Admin123!`、`demo@querypilot.dev / Demo123!`。
- 模拟数据规模：8 类 / 40 商品 / 5000 客户 / 60000 订单（2 年）/ 150000 明细，固定随机种子。
