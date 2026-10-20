"""QueryPilot Agent 服务（阶段 3：Text-to-SQL）。

- /health：存活检查
- /validate-sql：SQL 安全校验
- /query：查询计划 → 生成 SQL → 校验 → 只读执行（单轮查询）
"""

from fastapi import FastAPI
from pydantic import BaseModel

from .config import ALLOWED_SCHEMA, ANALYSIS_DB
from .executor import ExecutionError, Executor
from .query_plan import QueryPlan
from .sql_generator import PlanError, generate_sql
from .sql_validator import SqlValidator, ValidationError

app = FastAPI(title="QueryPilot Agent")

executor = Executor(ANALYSIS_DB)


class ValidateSqlRequest(BaseModel):
    sql: str


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

    return {"code": 0, "sql": sql, "data": result}
