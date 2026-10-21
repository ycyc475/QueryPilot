# QueryPilot — 面向业务人员的对话式数据分析平台

> 全栈 + AI Agent 作品集项目。用户以自然语言提问，系统检索获授权的数据表结构及业务口径，生成并校验只读 SQL，执行后返回图表、明细与可追溯的结论。

需求基线：根目录 `QueryPilot_对话式数据分析平台_PRD_v0.1.md`。进度与验收：`docs/PROGRESS.md`。**项目总结与上手指南（面向新人，强烈推荐先读）：`docs/PROJECT_GUIDE.md`**。

## 当前进度

已完成阶段 1–4：基础工程、语义元数据、Text-to-SQL、Agent 与图表。现在可以登录 → 选数据集 → 自然语言提问 → 得到图表 + SQL + 明细 + 结论。剩余：多轮追问、评测与交付。

## 架构

```
Vue 3 + TS + Vite + Element Plus + ECharts（对话页 / 图表）
        │ REST（/api 代理）
Java 21 + Spring Boot 3（认证 / 数据集与元数据 / 会话 / query_run / 审计）
        │ HTTP（/ask，内部，禁用系统代理）
Python + FastAPI + SQLGlot（意图解析 → 生成 SQL → 校验 → 只读执行 → 图表/结论）
        ├── PostgreSQL 元数据库 querypilot_meta（Java 读写）
        └── PostgreSQL 演示分析库 querypilot_analysis（只读账号 qp_analysis_ro）
```

## 快速开始

前置：Docker、Java 21、Node.js、Python 3。

```bash
# 1. 数据库（PostgreSQL，单实例双库；首次初始化角色/库/分析库表）
docker compose -f docker/docker-compose.yml up -d db

# 2. 生成模拟电商数据（一次性；固定随机种子，可重复运行）
pip install -r scripts/requirements.txt
python scripts/seed_ecommerce.py

# 3. 启动 Agent 服务（端口 8000，需先建 venv）
cd agent
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt      # Windows
./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000

# 4. 启动后端（端口 8080，自动执行 Flyway 迁移 + 种子账号）
cd ../backend
./mvnw spring-boot:run

# 5. 启动前端（端口 5173，/api 代理到 8080）
cd ../frontend
npm install
npm run dev
```

浏览器访问 **http://localhost:5173**。

演示账号：`admin@querypilot.dev / Admin123!`（ADMIN）、`demo@querypilot.dev / Demo123!`（ANALYST）。

示例提问：`过去30天每天的实付销售额趋势`、`上个月各省销售额前10名`、`华东地区按省份的实付销售额`。

## 测试

```bash
cd backend && ./mvnw test                              # 后端单测（15）
cd agent && ./.venv/Scripts/python.exe -m pytest       # agent 单测（33）
cd frontend && npm run build                           # 前端类型检查 + 构建
```

## 本机开发注意（Windows）

- 跑 Maven Wrapper 需加前缀（Anaconda `cygpath` 覆盖问题）：`PATH=/usr/bin:$PATH JAVA_HOME=/d/JavaJdk ./mvnw ...`；CMD/PowerShell 下全局 `mvn` 无需前缀。
- 本机系统代理（Clash 127.0.0.1:7890）会把 Java→localhost 的 HTTP 请求转坏；后端调 agent 已禁用代理（`AgentClient`），无需额外处理。
- Maven 本地仓库在 `D:\Apache\apache-maven-3.10.0\repository`（`~/.m2/settings.xml` 已配阿里云镜像）。

详见 `docs/PROGRESS.md` 与记忆 `dev-environment-quirks`。

## 已知限制（阶段 1–4）

- 意图解析与 SQL 生成当前是**确定性模板**（无 LLM，PRD §12#7 允许）；真实 LLM 接入留后续。
- 维度暂覆盖日期/月份/渠道/状态/省份/地区；商品品类等需 join 明细表的维度留后续（避免聚合重复计数）。
- 多轮上下文继承（「只看华东」）、SSE 流式、管理员审计页属第五阶段。
