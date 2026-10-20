"""图表规格推荐（确定性，PRD §5：时间趋势→折线，类别对比→柱状，明细→表格）。"""

from .query_plan import QueryPlan

TIME_DIMENSIONS = {"date", "month"}
CATEGORY_DIMENSIONS = {"province", "region", "channel", "status"}


def recommend_chart(plan: QueryPlan) -> dict:
    dims = plan.dimensions
    if any(d in TIME_DIMENSIONS for d in dims):
        chart_type = "line"
    elif any(d in CATEGORY_DIMENSIONS for d in dims):
        chart_type = "bar"
    else:
        chart_type = "table"

    if chart_type == "table":
        return {"type": "table"}

    return {"type": chart_type, "x_field": dims[0], "y_field": "metric_value"}
