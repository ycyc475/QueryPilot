"""指标、维度/字段、时间范围的口径定义（确定性，对应元库 business_metrics/schema_columns）。

第一版只覆盖演示问题所需口径；更多维度（如商品品类，需 join order_items）留后续阶段，
避免 join 明细表导致聚合重复计数。
"""

# 指标口径（与 business_metrics 种子一致）
METRICS = {
    "paid_sales": {
        "name": "实付销售额",
        "expression": "SUM(orders.paid_amount)",
        "where": "orders.status = 'paid'",
        "time_column": "orders.ordered_at",
    },
    "order_count": {
        "name": "订单量",
        "expression": "COUNT(orders.id)",
        "where": "orders.status = 'paid'",
        "time_column": "orders.ordered_at",
    },
    "avg_order_value": {
        "name": "客单价",
        "expression": "SUM(orders.paid_amount) / NULLIF(COUNT(orders.id), 0)",
        "where": "orders.status = 'paid'",
        "time_column": "orders.ordered_at",
    },
}

# 维度/过滤字段：语义名 → 表达式 + 需要的 JOIN
FIELDS = {
    "date": {"expr": "orders.ordered_at::date", "join": None},
    "month": {"expr": "to_char(orders.ordered_at, 'YYYY-MM')", "join": None},
    "channel": {"expr": "orders.channel", "join": None},
    "status": {"expr": "orders.status", "join": None},
    "province": {"expr": "c.province", "join": "JOIN customers c ON c.id = orders.customer_id"},
    "region": {"expr": "c.region", "join": "JOIN customers c ON c.id = orders.customer_id"},
}

TIME_RANGES = {
    "last_7_days": "orders.ordered_at >= now() - interval '7 days'",
    "last_30_days": "orders.ordered_at >= now() - interval '30 days'",
    "last_90_days": "orders.ordered_at >= now() - interval '90 days'",
}
