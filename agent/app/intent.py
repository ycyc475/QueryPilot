"""确定性意图解析：自然语言 → QueryPlan（关键词/词典，无 LLM，PRD §12#7）。

覆盖演示问题所需口径；多轮上下文继承（"只看华东"）留阶段 5。
"""

import re

from .query_plan import Filter, QueryPlan


class IntentError(Exception):
    """意图无法解析。"""


METRIC_KEYWORDS = {
    "paid_sales": ["实付销售额", "销售额", "营收", "收入", "GMV"],
    "order_count": ["订单量", "订单数", "单量", "订单数量"],
    "avg_order_value": ["客单价", "客单", "人均消费", "ARPU"],
}

DIMENSION_KEYWORDS = {
    "date": ["每天", "按天", "按日", "趋势", "逐日", "每日"],
    "month": ["每月", "按月", "逐月"],
    "province": ["各省", "省份", "按省", "分省", "哪个省"],
    "region": ["各地区", "按地区", "分地区", "区域", "大区", "各区"],
    "channel": ["渠道", "各渠道"],
}

TIME_KEYWORDS = {
    "last_7_days": ["过去7天", "最近7天", "近7天", "本周", "近一周"],
    "last_30_days": ["过去30天", "最近30天", "近30天", "上个月", "上月", "近一个月"],
    "last_90_days": ["过去90天", "最近90天", "近90天", "近三个月"],
}

REGIONS = ["华东", "华北", "华南", "西南", "华中", "东北", "西北"]

# 类别对比维度 → 排序用 metric_desc（排行）；时间趋势 → dimension_asc
RANKING_DIMENSIONS = {"province", "region", "channel", "status", "month"}


def parse_question(question: str) -> QueryPlan:
    q = question or ""

    metric = _first_match(q, METRIC_KEYWORDS)
    if metric is None:
        raise IntentError("无法识别指标，请使用「实付销售额 / 订单量 / 客单价」等")

    dimensions = [name for name, kws in DIMENSION_KEYWORDS.items() if any(k in q for k in kws)]
    # 去重且保留顺序
    dimensions = list(dict.fromkeys(dimensions))

    time_range = _first_match(q, TIME_KEYWORDS)

    filters = []
    for region in REGIONS:
        if region in q:
            filters.append(Filter(field="region", op="=", value=region))
            break

    if not dimensions:
        dimensions = ["date"]

    sort = "metric_desc" if any(d in RANKING_DIMENSIONS for d in dimensions) else "dimension_asc"

    limit = 1000
    m = re.search(r"前\s*(\d+)", q)
    if m:
        limit = int(m.group(1))
    elif sort == "metric_desc":
        limit = 10

    return QueryPlan(
        metric=metric, dimensions=dimensions, filters=filters,
        time_range=time_range, sort=sort, limit=limit,
    )


def _first_match(text: str, keyword_map: dict) -> str | None:
    for name, kws in keyword_map.items():
        if any(k in text for k in kws):
            return name
    return None
