package com.querypilot.metadata.dto;

/**
 * 指标编辑请求；字段为 null 表示不修改（部分更新）。
 */
public record MetricUpdateRequest(String name, String definition, String expression, String timeColumn,
                                  String synonyms) {
}
