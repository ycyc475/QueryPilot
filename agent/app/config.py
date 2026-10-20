"""演示数据集的表/列白名单与只读数据库连接配置。"""

import os

# 与元数据库 schema_tables/schema_columns 一致（后续阶段可由 Java /schema 拉取）
ALLOWED_SCHEMA = {
    "orders": {
        "id", "customer_id", "order_no", "ordered_at", "status",
        "payable_amount", "paid_amount", "refund_amount", "channel",
    },
    "order_items": {"id", "order_id", "product_id", "quantity", "unit_price", "item_amount"},
    "customers": {"id", "name", "region", "province", "city", "segment", "created_at"},
    "products": {"id", "category_id", "name", "sku", "unit_price", "status"},
    "categories": {"id", "name", "description"},
}

# 分析库只读账号（独立只读，PRD §9）
ANALYSIS_DB = {
    "host": os.getenv("QP_ANALYSIS_DB_HOST", "localhost"),
    "port": int(os.getenv("QP_ANALYSIS_DB_PORT", "5432")),
    "dbname": os.getenv("QP_ANALYSIS_DB_NAME", "querypilot_analysis"),
    "user": os.getenv("QP_ANALYSIS_DB_USER", "qp_analysis_ro"),
    "password": os.getenv("QP_ANALYSIS_DB_PASSWORD", "qp_analysis_ro_pw"),
}
