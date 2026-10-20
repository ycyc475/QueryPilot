"""从查询计划确定性生成 SQL（无 LLM，PRD §12#7 允许先用确定性实现联调）。

生成的 SQL 只包含白名单表/列，仍必须经 SqlValidator 校验后才执行。
"""

from typing import Any

from .definitions import FIELDS, METRICS, TIME_RANGES
from .query_plan import QueryPlan

ALLOWED_OPS = {"=", "!=", "<", "<=", ">", ">=", "in", "not in", "like"}


class PlanError(Exception):
    """查询计划不合法。"""


def generate_sql(plan: QueryPlan) -> str:
    if plan.metric not in METRICS:
        raise PlanError(f"未知指标: {plan.metric}")
    metric = METRICS[plan.metric]

    joins: list[str] = []
    select_exprs: list[str] = []
    group_by: list[str] = []

    for dim in plan.dimensions:
        field = _field(dim)
        _add_join(joins, field)
        select_exprs.append(f"{field['expr']} AS {dim}")
        group_by.append(field["expr"])

    select_exprs.append(f"{metric['expression']} AS metric_value")

    where: list[str] = [metric["where"]]
    if plan.time_range:
        if plan.time_range not in TIME_RANGES:
            raise PlanError(f"未知时间范围: {plan.time_range}")
        where.append(TIME_RANGES[plan.time_range])

    for flt in plan.filters:
        if flt.op.lower() not in ALLOWED_OPS:
            raise PlanError(f"不支持的比较符: {flt.op}")
        field = _field(flt.field)
        _add_join(joins, field)
        where.append(f"{field['expr']} {flt.op} {_literal(flt.value)}")

    sql = f"SELECT {', '.join(select_exprs)} FROM orders"
    for join in joins:
        sql += f" {join}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    if group_by:
        sql += " GROUP BY " + ", ".join(group_by)
    sql += _order_by(plan, group_by, metric["expression"])
    sql += f" LIMIT {plan.limit}"
    return sql


def _field(name: str):
    if name not in FIELDS:
        raise PlanError(f"未知字段/维度: {name}")
    return FIELDS[name]


def _add_join(joins: list[str], field: dict) -> None:
    if field["join"] and field["join"] not in joins:
        joins.append(field["join"])


def _order_by(plan: QueryPlan, group_by: list[str], metric_expression: str) -> str:
    if plan.sort == "metric_desc":
        return f" ORDER BY {metric_expression} DESC"
    if plan.sort == "metric_asc":
        return f" ORDER BY {metric_expression} ASC"
    if plan.sort == "dimension_asc" and group_by:
        return f" ORDER BY {group_by[0]} ASC"
    return ""


def _literal(value: Any) -> str:
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "(" + ", ".join(_literal(v) for v in value) + ")"
    raise PlanError(f"不支持的过滤值: {value!r}")
