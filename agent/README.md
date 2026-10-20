# agent — QueryPilot 的 Text-to-SQL 服务

Python + FastAPI + SQLGlot。负责：查询计划 → SQL 生成 → 安全校验 → 只读执行（阶段 3）。

## 快速开始

```bash
cd agent
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt   # Windows
./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
```

## 测试

```bash
./.venv/Scripts/python.exe -m pytest
```

## 端点

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/health` | 存活检查 |
| `POST` | `/validate-sql` | SQL 安全校验（AST + 白名单） |
| `POST` | `/query` | 查询计划 → 生成 SQL → 校验 → 只读执行 |

`/query` 请求体（QueryPlan）示例：

```json
{"metric":"paid_sales","dimensions":["date"],"time_range":"last_7_days","sort":"dimension_asc"}
```

## 安全红线（PRD §9 / §3）

- 生成的 SQL 必须先经 `SqlValidator` 校验（单语句、仅 SELECT、表/列白名单、危险函数拒绝）才执行。
- 执行用只读账号 `qp_analysis_ro`（`statement_timeout=30s`、`default_transaction_read_only=on`），禁止直连未校验 SQL。

## 已知限制（阶段 3）

- SQL 生成是**确定性模板**（指标/维度口径见 `app/definitions.py`），LLM 生成在阶段 4 接入。
- 维度暂覆盖 date/month/channel/status/province/region；商品品类等需 join 明细表的维度留后续（避免聚合重复计数）。
- 表/列白名单暂为本地配置 `app/config.py`，阶段 4 改为从 Java `/api/datasets/{id}/schema` 拉取。
