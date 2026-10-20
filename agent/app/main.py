"""QueryPilot Agent 服务（阶段 3-4：Text-to-SQL + 意图解析 + 图表/结论）。

- /health：存活检查
- /validate-sql：SQL 安全校验
- /query：查询计划 → 生成 SQL → 校验 → 只读执行
- /ask：自然语言 → 意图解析 → SQL → 执行 → 图表 + 结论
"""

from fastapi import FastAPI
from pydantic import BaseModel

from .chart import recommend_chart
from .config import ALLOWED_SCHEMA, ANALYSIS_DB
from .definitions import METRICS
from .executor import ExecutionError, Executor
from .intent import IntentError, parse_question
from .query_plan import QueryPlan
from .sql_generator import PlanError, generate_sql
from .sql_validator import SqlValidator, ValidationError
from .summary import summarize

app = FastAPI(title="QueryPilot Agent")

executor = Executor(ANALYSIS_DB)


class ValidateSqlRequest(BaseModel):
    sql: str


class AskRequest(BaseModel):
    question: str
    dataset_id: int = 1


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/validate-sql")
def validate_sql(request: ValidateSqlRequest):
    validator = SqlValidator(ALLOWED_SCHEMA)
    try:
        validator.validate(request.sql)
        return {"valid": True}
    except ValidationError as exc:
        return {"valid": False, "error": str(exc)}


@app.post("/query")
def query(plan: QueryPlan):
    return _run_plan(plan)


@app.post("/ask")
def ask(request: AskRequest):
    try:
        plan = parse_question(request.question)
    except IntentError as exc:
        return {"code": 400, "error": str(exc)}
    return _run_plan(plan)


def _run_plan(plan: QueryPlan):
    try:
        sql = generate_sql(plan)
    except PlanError as exc:
        return {"code": 400, "error": str(exc)}

    try:
        SqlValidator(ALLOWED_SCHEMA).validate(sql)
    except ValidationError as exc:
        return {"code": 400, "error": f"SQL 校验失败: {exc}"}

    try:
        result = executor.execute(sql)
    except ExecutionError as exc:
        return {"code": 500, "error": f"{exc.kind}: {exc.message}"}

    chart = recommend_chart(plan)
    metric_name = METRICS[plan.metric]["name"]
    summary = summarize(plan, result["rows"], result["columns"], metric_name)

    return {
        "code": 0,
        "query_plan": plan.model_dump(),
        "sql": sql,
        "columns": result["columns"],
        "rows": result["rows"],
        "row_count": result["row_count"],
        "chart": chart,
        "summary": summary,
        "duration_ms": result["duration_ms"],
    }
