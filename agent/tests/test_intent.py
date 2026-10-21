import pytest

from app.chart import recommend_chart
from app.intent import IntentError, parse_question
from app.summary import summarize


def test_parses_daily_order_count_trend():
    plan = parse_question("过去30天每天的订单量趋势如何")
    assert plan.metric == "order_count"
    assert plan.dimensions == ["date"]
    assert plan.time_range == "last_30_days"
    assert plan.sort == "dimension_asc"


def test_parses_province_sales_ranking():
    plan = parse_question("上个月各省销售额前10名是哪些")
    assert plan.metric == "paid_sales"
    assert plan.dimensions == ["province"]
    assert plan.time_range == "last_30_days"
    assert plan.sort == "metric_desc"
    assert plan.limit == 10


def test_parses_daily_sales_trend():
    plan = parse_question("最近30天每天的实付销售额趋势")
    assert plan.metric == "paid_sales"
    assert plan.dimensions == ["date"]
    assert plan.time_range == "last_30_days"


def test_parses_region_filter():
    plan = parse_question("华东地区按省份的销售额")
    assert plan.metric == "paid_sales"
    assert plan.dimensions == ["province"]
    assert plan.filters[0].value == "华东"


def test_parses_order_count_with_default_dimension():
    plan = parse_question("近7天订单量")
    assert plan.metric == "order_count"
    assert plan.time_range == "last_7_days"
    assert plan.dimensions == ["date"]


def test_parses_avg_order_value():
    plan = parse_question("帮我查一下客单价")
    assert plan.metric == "avg_order_value"


def test_rejects_unknown_metric():
    with pytest.raises(IntentError):
        parse_question("你好")


def test_chart_time_is_line_category_is_bar():
    from app.query_plan import QueryPlan
    assert recommend_chart(QueryPlan(metric="paid_sales", dimensions=["date"]))["type"] == "line"
    assert recommend_chart(QueryPlan(metric="paid_sales", dimensions=["province"]))["type"] == "bar"


def test_inherits_metric_and_time_from_context():
    ctx = {"metric": "paid_sales", "dimensions": ["date"], "filters": [],
           "time_range": "last_30_days", "sort": "dimension_asc", "limit": 1000}
    plan = parse_question("只看华东地区，按省份拆分", ctx)
    assert plan.metric == "paid_sales"
    assert plan.dimensions == ["province"]
    assert plan.time_range == "last_30_days"
    assert plan.filters[0].value == "华东"


def test_inherits_when_only_dimension_changes():
    ctx = {"metric": "order_count", "dimensions": ["date"], "filters": [],
           "time_range": "last_7_days", "sort": "dimension_asc", "limit": 1000}
    plan = parse_question("改按省份", ctx)
    assert plan.metric == "order_count"
    assert plan.dimensions == ["province"]
    assert plan.time_range == "last_7_days"


def test_summary_not_empty_and_mentions_total():
    from app.query_plan import QueryPlan
    columns = [{"name": "date", "type": "date"}, {"name": "metric_value", "type": "numeric"}]
    rows = [["2026-10-18", 100.0], ["2026-10-19", 200.0]]
    text = summarize(QueryPlan(metric="paid_sales", dimensions=["date"]), rows, columns, "实付销售额")
    assert "合计" in text
    assert "300.00" in text
