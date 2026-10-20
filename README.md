# QueryPilot — 面向业务人员的对话式数据分析平台

> 全栈 + AI Agent 作品集项目。用户以自然语言提问，系统检索获授权的数据表结构及业务口径，生成并校验只读 SQL，执行后返回图表、明细与可追溯的结论。

需求基线：根目录 `QueryPilot_对话式数据分析平台_PRD_v0.1.md`。进度与验收：`docs/PROGRESS.md`。

## 当前进度

第一阶段（基础工程）已完成：登录、数据库、模拟电商数据、数据集查询。对话式分析（Text-to-SQL / Agent / 图表）属后续阶段。

## 架构

```
Vue 3 + TS + Vite + Element Plus
        │ REST / SSE
Java 21 + Spring Boot 3（认证 / 数据集与元数据 / 会话 / 审计）
        │ 内部 API
Python + FastAPI + LangGraph + SQLGlot（意图 / 检索 / 查询规划 / SQL 生成与校验）—— 后续阶段
        ├── PostgreSQL 元数据库 querypilot_meta
        └── PostgreSQL 演示分析库 querypilot_analysis（独立只读账号）
```

## 快速开始

```bash
# 1. 启动数据库（PostgreSQL 16，单实例双库；首次初始化角色/库/分析库表）
docker compose -f docker/docker-compose.yml up -d db

# 2. 生成模拟电商数据（一次性；固定随机种子，可重复运行）
pip install -r scripts/requirements.txt
python scripts/seed_ecommerce.py

# 3. 启动后端（自动执行 Flyway 迁移 + 种子账号）
cd backend && ./mvnw spring-boot:run

# 4. 启动前端（开发服务器，/api 代理到 8080）
cd frontend && npm install && npm run dev
# 浏览器访问 http://localhost:5173
```

演示账号：`admin@querypilot.dev / Admin123!`（ADMIN）、`demo@querypilot.dev / Demo123!`（ANALYST）。

### 测试

```bash
cd backend && ./mvnw test        # 后端单测 + 上下文加载
cd frontend && npm run build     # 前端类型检查 + 构建
```

## 本机开发注意（Windows）

本机 Anaconda 的 `cygpath` 会覆盖 MSYS2 的，导致 Maven Wrapper 路径错乱；Docker Hub 直连超时已配镜像加速。跑 Maven 需加前缀：

```bash
PATH=/usr/bin:$PATH JAVA_HOME=/d/JavaJdk ./mvnw ...
```

## 已知限制（第一阶段）

- 对话式分析（Text-to-SQL、Agent、图表、结论）尚未实现。
- 前端 element-plus 全量引入，bundle 偏大，后续可改按需引入。
- 数据写入/多租户/多数据源等属 PRD 明确非目标。
