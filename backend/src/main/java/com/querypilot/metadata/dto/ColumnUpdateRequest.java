package com.querypilot.metadata.dto;

/**
 * 字段语义编辑请求；字段为 null 表示不修改（部分更新）。
 */
public record ColumnUpdateRequest(String description, String synonyms) {
}
