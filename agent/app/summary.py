"""基于真实结果生成文字结论（不虚构数据，PRD §12#4）。"""

from .query_plan import QueryPlan

TIME_DIMENSIONS = {"date", "month"}


def summarize(plan: QueryPlan, rows: list, columns: list, metric_name: str) -> str:
    if not rows:
        return "查询无结果，请调整条件。"

    metric_idx = next((i for i, c in enumerate(columns) if c["name"] == "metric_value"), -1)
    dim_idx = next((i for i, c in enumerate(columns) if c["name"] != "metric_value"), 0)

    n = len(rows)
    parts = [f"共 {n} 条结果"]

    if metric_idx >= 0:
        total = sum(float(r[metric_idx]) for r in rows)
        parts.append(f"{metric_name}合计 {total:,.2f}")

        if plan.dimensions and plan.dimensions[0] in TIME_DIMENSIONS:
            values = [float(r[metric_idx]) for r in rows]
            parts.append(f"最高 {max(values):,.2f}，最低 {min(values):,.2f}")
        elif plan.sort == "metric_desc" and rows:
            top = rows[0]
            parts.append(f"最高为 {top[dim_idx]}（{float(top[metric_idx]):,.2f}）")

    return "；".join(parts)
