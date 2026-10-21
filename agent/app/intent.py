"""确定性意图解析：自然语言 → QueryPlan（关键词/词典，无 LLM，PRD §12#7）。

支持多轮上下文合并（PRD §5 / F08）：新问题未指定的 metric/time_range/dimensions 继承上一轮，
filters 按字段覆盖合并（追问「只看华东」加 region 过滤、保留原指标与时间范围）。
"""

import re
from typing import Optional

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

RANKING_DIMENSIONS = {"province", "region", "channel", "status", "month"}


def parse_question(question: str, context: Optional[dict] = None) -> QueryPlan:
    q = question or ""
    ctx = context or {}

    metric = _first_match(q, METRIC_KEYWORDS)
    dimensions = _detect_dimensions(q)
    time_range = _first_match(q, TIME_KEYWORDS)
    filters = [Filter(field="region", op="=", value=r) for r in REGIONS if r in q]

    # 多轮合并：缺失项继承上一轮
    if metric is None:
        metric = ctx.get("metric")
    if not time_range:
        time_range = ctx.get("time_range")
    if not dimensions:
        dimensions = ctx.get("dimensions") or []
    filters = _merge_filters(ctx.get("filters") or [], filters)

    if metric is None:
        raise IntentError("无法识别指标，请使用「实付销售额 / 订单量 / 客单价」等")
    if not dimensions:
        dimensions = ["date"]

    sort = "metric_desc" if any(d in RANKING_DIMENSIONS for d in dimensions) else "dimension_asc"
    limit = _detect_limit(q, sort)

    return QueryPlan(
        metric=metric, dimensions=dimensions, filters=filters,
        time_range=time_range, sort=sort, limit=limit,
    )


def _detect_dimensions(text: str) -> list:
    dims = []
    for name, kws in DIMENSION_KEYWORDS.items():
        if any(k in text for k in kws):
            dims.append(name)
    return list(dict.fromkeys(dims))


def _merge_filters(prev: list, new: list) -> list:
    merged = [Filter(field=f["field"], op=f.get("op", "="), value=f.get("value")) for f in prev]
    for nf in new:
        merged = [f for f in merged if f.field != nf.field]
        merged.append(nf)
    return merged


def _detect_limit(text: str, sort: str) -> int:
    m = re.search(r"前\s*(\d+)", text)
    if m:
        return int(m.group(1))
    return 10 if sort == "metric_desc" else 1000


def _first_match(text: str, keyword_map: dict) -> str | None:
    for name, kws in keyword_map.items():
        if any(k in text for k in kws):
            return name
    return None
