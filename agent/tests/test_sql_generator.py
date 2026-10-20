import pytest

from app.config import ALLOWED_SCHEMA
from app.query_plan import Filter, QueryPlan
from app.sql_generator import PlanError, generate_sql
from app.sql_validator import SqlValidator

validator = SqlValidator(ALLOWED_SCHEMA)


def test_generates_daily_sales_trend():
    sql = generate_sql(QueryPlan(metric="paid_sales", dimensions=["date"], time_range="last_30_days"))
    assert "SUM(orders.paid_amount)" in sql
    assert "orders.ordered_at::date" in sql
    assert "interval '30 days'" in sql
    assert "GROUP BY orders.ordered_at::date" in sql
    validator.validate(sql)  # 生成的 SQL 必须过校验


def test_generates_province_ranking():
    sql = generate_sql(QueryPlan(
        metric="paid_sales", dimensions=["province"], time_range="last_30_days",
        sort="metric_desc", limit=10,
    ))
    assert "JOIN customers c ON c.id = orders.customer_id" in sql
    assert "c.province" in sql
    assert "ORDER BY SUM(orders.paid_amount) DESC" in sql
    assert "LIMIT 10" in sql
    validator.validate(sql)


def test_generates_region_filter():
    sql = generate_sql(QueryPlan(
        metric="paid_sales", dimensions=["province"],
        filters=[Filter(field="region", op="=", value="华东")],
    ))
    assert "c.region = '华东'" in sql
    validator.validate(sql)


def test_generates_order_count():
    sql = generate_sql(QueryPlan(metric="order_count", dimensions=["date"], time_range="last_7_days"))
    assert "COUNT(orders.id)" in sql
    validator.validate(sql)


def test_escapes_single_quote_in_value():
    sql = generate_sql(QueryPlan(metric="paid_sales", filters=[Filter(field="channel", value="a'b")]))
    assert "orders.channel = 'a''b'" in sql
    validator.validate(sql)


def test_rejects_unknown_metric():
    with pytest.raises(PlanError):
        generate_sql(QueryPlan(metric="nope"))


def test_rejects_unknown_dimension():
    with pytest.raises(PlanError):
        generate_sql(QueryPlan(metric="paid_sales", dimensions=["nope"]))


def test_rejects_bad_op():
    with pytest.raises(PlanError):
        generate_sql(QueryPlan(metric="paid_sales", filters=[Filter(field="status", op="; DROP", value="x")]))
