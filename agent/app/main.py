"""QueryPilot Agent 服务（阶段 3-5：Text-to-SQL + 意图解析 + 图表/结论 + 多轮上下文）。

- /health：存活检查
- /validate-sql：SQL 安全校验
- /query：查询计划 → 生成 SQL → 校验 → 只读执行
- /ask：自然语言 → 意图解析（含多轮上下文合并）→ SQL → 执行 → 图表 + 结论
"""

from typing import Optional

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
    context: Optional[dict] = None


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
        plan = parse_question(request.question, request.context)
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
        # 有限修复（F11）：超时则降级 limit 重试一次，不无限循环
        if exc.kind == "timeout" and plan.limit > 100:
            retry_plan = plan.model_copy(update={"limit": 100})
            retry_sql = generate_sql(retry_plan)
            try:
                SqlValidator(ALLOWED_SCHEMA).validate(retry_sql)
                result = executor.execute(retry_sql)
                sql = retry_sql
            except (ExecutionError, ValidationError) as retry_exc:
                msg = getattr(retry_exc, "message", str(retry_exc))
                return {"code": 500, "error": f"timeout 重试后仍失败: {msg}"}
        else:
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
