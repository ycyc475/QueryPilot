# QueryPilot 项目总结与上手指南

> 面向「前后端 + AI Agent」项目不太熟悉的新人。目标是让你读完这份文档后，能理解整个项目的结构、各部分的职责、数据是怎么流动的，以及如何自己跑起来、如何改代码。
> 需求基线见根目录 `QueryPilot_对话式数据分析平台_PRD_v0.1.md`；开发进度见 `docs/PROGRESS.md`。

---

## 1. 这个项目是做什么的

一句话：**用户用自然语言问数据问题，系统把问题转成 SQL 去查数据库，再把结果变成图表 + 文字结论展示出来。**

典型场景：

> 用户输入「过去 30 天每天的实付销售额趋势」
> → 系统识别出「实付销售额」「按天」「过去 30 天」这三个意图
> → 生成一条 SQL：`SELECT ... SUM(paid_amount) ... GROUP BY 日期`
> → 经过安全校验后，用**只读账号**执行
> → 返回一张折线图 + 明细表 + 这条 SQL + 一句文字结论

它的价值在于：**让不懂 SQL 的业务人员也能自助做数据分析**，同时保证安全（不会误删数据）和可追溯（能回看每一步用了什么 SQL、什么口径）。

---

## 2. 整体架构（先建立全局观）

整个项目由 **4 个独立进程 + 2 个数据库** 组成：

```
┌─────────────────────────────────────────────────────────────┐
│  前端  Vue 3 + TypeScript + Vite + Element Plus + ECharts     │
│  职责：登录、对话界面、渲染图表/表格/SQL                        │
│  端口：5173                                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST（/api，前端代理到 8080）
┌──────────────────────────▼──────────────────────────────────┐
│  后端  Java 21 + Spring Boot 3                               │
│  职责：用户认证、数据集/元数据管理、会话管理、审计、API 网关    │
│  端口：8080                                                  │
│  它读写「元数据库」                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP（/ask，内部调用，端口 8000）
┌──────────────────────────▼──────────────────────────────────┐
│  Agent  Python + FastAPI + SQLGlot                           │
│  职责：意图解析、生成 SQL、安全校验、执行查询、图表/结论        │
│  端口：8000                                                  │
│  它用「只读账号」查「分析数据库」                              │
└───────────────┬──────────────────────────────┬───────────────┘
                │ 只读（qp_analysis_ro）        │ 读写（qp_meta）
     ┌──────────▼──────────┐        ┌──────────▼──────────┐
     │ 分析数据库           │        │ 元数据库             │
     │ querypilot_analysis │        │ querypilot_meta     │
     │ （电商模拟数据，只读）│        │ （用户/会话/元数据）  │
     └─────────────────────┘        └─────────────────────┘
```

### 为什么要拆成三个服务？

这是「前后端 + Agent」类项目最常见的分层，核心思想是**各管一摊、互不越界**：

| 服务 | 只负责 | 不负责 |
|---|---|---|
| 前端 | 展示界面、和用户交互 | 不懂数据库、不懂 SQL |
| 后端 Java | 身份认证、数据管理、会话、把结果存起来 | 不直接生成/执行分析 SQL |
| Agent Python | 理解问题、生成 SQL、执行查询 | 不管登录、不管存历史 |

这样拆的好处：**改 SQL 生成逻辑只动 Agent，改界面只动前端，互相不影响**；同时职责清晰，方便单独测试和替换（比如以后把 Agent 里的确定性逻辑换成大模型，前端和 Java 几乎不用改）。

---

## 3. 技术栈一览

| 层 | 技术 | 为什么用 |
|---|---|---|
| 前端 | Vue 3 + TypeScript + Vite | 主流前端框架，类型安全 |
| | Element Plus | UI 组件库（按钮/表格/输入框） |
| | Pinia + Vue Router | 状态管理 + 路由 |
| | Axios | 发 HTTP 请求 |
| | ECharts | 画折线图/柱状图 |
| 后端 | Java 21 + Spring Boot 3 | 企业级后端框架 |
| | Spring Security + JWT | 登录认证、接口鉴权 |
| | Spring Data JPA | 操作数据库（对象映射到表） |
| | Flyway | 数据库结构版本化迁移 |
| Agent | Python + FastAPI | 轻量 API 服务，适合 AI 逻辑 |
| | SQLGlot | 解析/校验 SQL（安全核心） |
| | psycopg2 | Python 连 PostgreSQL |
| 数据库 | PostgreSQL 16 | 元数据 + 分析数据，两个库 |
| 部署 | Docker Compose | 一键起数据库（及后续全部服务） |

---

## 4. 一次完整的数据流（最重要的一节）

以「过去 30 天每天的实付销售额趋势」为例，跟踪一个请求从头到尾经过哪里：

```
① 用户在浏览器输入问题，点发送
② 前端 ChatView.vue 调 POST /api/conversations/{id}/messages，body = {content: "..."}
   （请求头带 JWT token，证明「我是 demo 用户」）
③ 后端 ConversationController 收到请求
   - 校验 token → 知道是 demo 用户
   - 校验这个会话属于 demo
   - 存一条 user 消息（role=user, content=问题）
   - 建一条 query_run 记录（status=RUNNING，表示"开始执行"）
④ ConversationService 调 AgentClient，把问题 + 上一轮的上下文（context_json）
   发给 Agent 的 /ask 接口（HTTP，端口 8000）
⑤ Agent 收到请求，按顺序做：
   a. 意图解析（intent.py）：从问题里识别指标/维度/时间范围/过滤
      - "实付销售额" → metric=paid_sales
      - "每天/趋势" → dimension=date
      - "过去30天" → time_range=last_30_days
      - 同时合并上一轮上下文（如果是追问）
   b. 生成 SQL（sql_generator.py + definitions.py）：按模板拼出
      SELECT ordered_at::date, SUM(paid_amount) FROM orders WHERE status='paid' ... GROUP BY 1
   c. 安全校验（sql_validator.py，SQLGlot）：
      - 只能一条语句、只能是 SELECT
      - 表名必须在白名单里、列名必须在白名单里
      - 拒绝 DROP/UPDATE/多语句/危险函数
   d. 执行（executor.py）：用只读账号 qp_analysis_ro 执行 SQL
      - statement_timeout=30s（超时中断）
      - 行数上限保护
   e. 图表推荐（chart.py）：时间维度→折线图；类别维度→柱状图
   f. 生成结论（summary.py）：根据真实结果算合计/最高/最低
⑥ Agent 返回 JSON：{query_plan, sql, columns, rows, chart, summary, duration_ms}
⑦ 后端收到结果：
   - 更新 query_run：status=SUCCEEDED，存 sql/query_plan/chart_spec/耗时/行数
   - 存一条 assistant 消息（content=结论）
   - 更新会话的 context_json（供下一轮追问继承）
   - 把结果返回给前端
⑧ 前端收到结果：
   - ChartRenderer.vue 用 ECharts 画折线图
   - 渲染明细表格（columns + rows）
   - 显示「查看 SQL」折叠面板 + 文字结论
```

**记住这条主链**：`前端 → Java(认证/会话) → Agent(解析/生成/校验/执行) → 分析库 → 原路返回 → 图表`。

---

## 5. 核心概念（给新手的解释）

### 5.1 什么是 Text-to-SQL
把自然语言（中文问题）转成 SQL 查询。难点在于：SQL 是严格的、结构化的，自然语言是模糊的。本项目用**确定性模板**（词典匹配）做第一版，后续可换大模型。

### 5.2 为什么要「只读 + 白名单 + AST 校验」三重防线
AI 生成的 SQL 可能出错，甚至可能写出 `DROP TABLE` 这种危险语句。所以设了三道关卡：

1. **AST 校验（代码层）**：用 SQLGlot 解析 SQL，检查「只能 SELECT、表/列必须在白名单、拒绝危险函数」。
2. **只读账号（数据库层）**：`qp_analysis_ro` 账号在数据库层面就**没有写权限**（只能 SELECT），就算代码校验漏了，数据库也会拒绝写操作。
3. **资源限制**：超时 30 秒、行数上限，防止慢查询拖垮数据库。

**核心原则：永远不让「未经校验的 SQL」直接执行。**

### 5.3 什么是 JWT 认证
登录成功后，后端发一个「令牌」（token）给前端。之后每次请求都带上这个 token，后端验证 token 就知道你是谁。无状态（后端不用记 session），适合前后端分离。

### 5.4 什么是「多轮上下文」（追问）
用户问完「销售额趋势」后追问「只看华东地区」，系统要「记得」上一轮的指标和时间，只新增一个地区过滤。实现方式是：每次问完，把这次的「查询计划」（指标/维度/时间/过滤）存进 `conversations.context_json`，下一轮追问时读取并合并。

### 5.5 什么是「元数据」
把数据库的表结构（有哪些表、有哪些字段、字段是什么意思、指标口径）存到专门的「元数据库」里。Agent 生成 SQL 时靠它知道「实付销售额 = orders.paid_amount 之和」。对应第 2 阶段的工作。

---

## 6. 目录结构详解

```
QueryPilot/
├── backend/                      # Java 后端（Spring Boot）
│   ├── pom.xml                   # Maven 依赖配置
│   ├── mvnw / mvnw.cmd           # Maven Wrapper（无需装全局 Maven）
│   └── src/main/java/com/querypilot/
│       ├── QueryPilotApplication.java   # 启动入口
│       ├── auth/                 # 登录认证（JWT 生成/校验）
│       ├── user/                 # 用户实体/仓库
│       ├── dataset/              # 数据集（"电商分析"）
│       ├── metadata/             # 语义元数据（表/字段/指标/召回/编辑）
│       ├── conversation/         # 会话/消息/query_run + 调 Agent 的客户端
│       ├── admin/                # 管理员接口（指标编辑、查询审计）
│       ├── config/               # Spring Security、JWT 过滤器
│       ├── common/               # 统一响应/异常处理
│       └── seed/                 # 种子账号写入
│   └── src/main/resources/db/migration/   # Flyway 迁移 V1..V4
├── frontend/                     # 前端（Vue3 + Vite）
│   └── src/
│       ├── api/                  # HTTP 接口封装（http/auth/dataset/conversation）
│       ├── views/                # 页面（登录/工作台/对话/审计）
│       ├── components/           # ChartRenderer（ECharts 图表）
│       ├── router/               # 路由 + 登录守卫
│       ├── stores/               # Pinia（登录态）
│       └── types/                # TypeScript 类型
├── agent/                        # Agent（Python FastAPI + SQLGlot）
│   ├── app/
│   │   ├── main.py               # 服务入口（/health /validate-sql /query /ask）
│   │   ├── intent.py             # 意图解析（自然语言→查询计划，含多轮合并）
│   │   ├── definitions.py        # 指标/维度/时间范围的口径定义
│   │   ├── sql_generator.py      # 查询计划 → SQL
│   │   ├── sql_validator.py      # SQLGlot 安全校验
│   │   ├── executor.py           # 只读执行 + 错误分类
│   │   ├── chart.py              # 图表推荐
│   │   ├── summary.py            # 结论生成
│   │   └── config.py             # 白名单 + 数据库连接配置
│   ├── tests/                    # pytest 单测
│   └── requirements.txt
├── scripts/
│   ├── seed_ecommerce.py         # 生成模拟电商数据（确定性，可复现）
│   ├── schema_scan.py            # 分析库↔元库 结构核对/同步
│   └── requirements.txt
├── docker/
│   ├── docker-compose.yml        # PostgreSQL（单实例双库）
│   └── init/                     # 建库/建账号/建分析库表
├── docs/
│   ├── PROJECT_GUIDE.md          # 本文档
│   ├── PROGRESS.md               # 开发进度（每批更新）
│   └── phase-1-plan.md
├── AGENTS.md                     # 长期编码约束
└── README.md                     # 快速开始
```

---

## 7. 两个数据库的表结构

### 7.1 元数据库 `querypilot_meta`（Java 读写）

| 表 | 用途 |
|---|---|
| `users` | 用户（邮箱、密码哈希、角色 ADMIN/ANALYST） |
| `data_sources` | 数据源（不存明文密码，存 secret_ref） |
| `datasets` | 数据集（如"电商分析"） |
| `schema_tables` | 表级元数据 + 白名单 |
| `schema_columns` | 字段级元数据（描述、同义词、敏感标记） |
| `schema_relations` | 表关联关系（主外键） |
| `business_metrics` | 指标口径（如"实付销售额"的定义/表达式/同义词） |
| `conversations` | 会话（含 context_json 多轮上下文） |
| `messages` | 对话消息（user/assistant） |
| `query_runs` | 每次查询执行记录（问题/SQL/状态/耗时/行数/图表规格） |
| `audit_logs` | 审计日志 |

### 7.2 分析数据库 `querypilot_analysis`（只读账号访问，模拟电商数据）

| 表 | 内容 | 数据量（种子） |
|---|---|---|
| `categories` | 品类（8 个） | 8 |
| `products` | 商品（40 个） | 40 |
| `customers` | 客户（假名 + 地区/省份/分层） | 5000 |
| `orders` | 订单（下单时间/状态/实付金额） | 60000 |
| `order_items` | 订单明细 | 约 12 万 |

指标口径（在 `business_metrics` 和 Agent 的 `definitions.py` 里）：
- **实付销售额** = `status='paid'` 的订单的 `SUM(paid_amount)`
- **订单量** = `status='paid'` 的订单数
- **客单价** = 实付销售额 / 订单量

---

## 8. 关键 API 清单

### 后端（8080，路径都带 `/api` 前缀）

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/api/auth/login` | 登录，返回 JWT |
| GET | `/api/auth/me` | 当前用户信息 |
| GET | `/api/datasets` | 数据集列表 |
| GET | `/api/datasets/{id}/schema` | 授权可见的元数据（表/字段/关系/指标） |
| GET | `/api/datasets/{id}/semantic-search?q=` | 语义召回（关键词匹配表/字段/指标） |
| POST | `/api/conversations` | 新建会话 |
| GET | `/api/conversations/{id}` | 会话 + 历史消息 |
| POST | `/api/conversations/{id}/messages` | 提问（核心入口，返回图表/SQL/结论） |
| PUT | `/api/admin/metrics/{id}` | 管理员编辑指标（ADMIN） |
| PUT | `/api/admin/columns/{id}` | 管理员编辑字段语义（ADMIN） |
| GET | `/api/admin/query-runs` | 查询审计（ADMIN） |
| GET | `/api/health` | 健康检查 |

### Agent（8000，内部调用）

| 方法 | 路径 | 作用 |
|---|---|---|
| GET | `/health` | 存活 |
| POST | `/validate-sql` | 校验 SQL 是否安全 |
| POST | `/query` | 给定查询计划 → 执行 → 返回结果 |
| POST | `/ask` | 自然语言 → 意图解析 → SQL → 执行 → 图表+结论 |

---

## 9. 安全模型（面试常问）

1. **认证**：BCrypt 密码哈希 + JWT（HS256，密钥从环境变量读）。
2. **鉴权**：`/api/admin/**` 需 ADMIN 角色；普通接口需登录。
3. **SQL 安全三道防线**（见 5.2）：AST 校验 + 只读账号 + 资源限制。
4. **权限隔离**：用户只能访问自己的会话；白名单控制能查哪些表/字段。
5. **敏感信息**：分析库只有模拟数据（假名），密码不落明文（secret_ref 指向环境变量）。

---

## 10. 如何启动 / 测试（详见 README）

```bash
# 1. 数据库
docker compose -f docker/docker-compose.yml up -d db

# 2. 模拟数据（一次性）
pip install -r scripts/requirements.txt
python scripts/seed_ecommerce.py

# 3. Agent（8000）
cd agent
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000

# 4. 后端（8080）
cd ../backend && ./mvnw spring-boot:run

# 5. 前端（5173）
cd ../frontend && npm install && npm run dev
```

测试：

```bash
cd backend && ./mvnw test                             # 后端 15 单测
cd agent && ./.venv/Scripts/python.exe -m pytest      # agent 35 单测
cd frontend && npm run build                          # 前端类型检查+构建
```

演示账号：`admin@querypilot.dev / Admin123!`、`demo@querypilot.dev / Demo123!`。

---

## 11. 开发历程（六个阶段）

| 阶段 | 内容 | 状态 |
|---|---|---|
| 1 基础工程 | 脚手架、登录、数据库、模拟数据 | ✅ |
| 2 语义元数据 | 表/字段/指标元数据、召回、管理员编辑 | ✅ |
| 3 Text-to-SQL | SQL 生成、安全校验、只读执行 | ✅ |
| 4 Agent+图表 | 意图解析、会话、ECharts 图表、结论 | ✅ |
| 5 多轮与可靠性 | 多轮追问、查询审计、错误恢复 | ✅ |
| 6 评测与交付 | 回归测试、性能报告、一键部署 | ⏳ |

---

## 12. 已知限制与后续规划

**当前是「确定性」实现**（没有接大模型），所以：
- 只认得固定的指标/维度/时间/地区关键词，超出词典的提问会报「无法识别指标」。
- 多轮只继承「最近一轮」，维度是「覆盖」不是「累加」。

**后续增强方向**（按优先级）：
1. 接 LLM：真正的自然语言理解、任意追问（需要先定模型服务）。
2. embedding/pgvector：优化元数据召回（可选，PRD 说不阻塞 MVP）。
3. SSE 流式返回：让用户看到逐步执行过程。
4. 第六阶段：评测集、性能报告、Docker 一键起全栈。

---

## 13. 给新人的上手建议

1. **先跑起来**：按第 10 节启动，登录 demo 账号，问几个问题，点「查看 SQL」感受数据流。
2. **再看数据流**：对照第 4 节的 8 步，在代码里找到每一步对应的文件。
3. **改一个东西试试**：
   - 想加一个新指标 → 改 `agent/app/definitions.py`（加 metric 定义）+ `intent.py`（加关键词）。
   - 想加一个维度 → 改 `definitions.py` 的 FIELDS。
   - 想改界面 → 改 `frontend/src/views/`。
4. **看懂安全校验**：读 `agent/app/sql_validator.py`，试着让 Agent 校验一条 `DROP TABLE`，看它怎么拒绝。
5. **看测试**：`agent/tests/` 和 `backend/src/test/` 是最佳的学习样例，测试即文档。
