package com.querypilot.metadata.dto;

import com.querypilot.metadata.SchemaColumn;

public record ColumnDto(Long id, String name, String dataType, String description, String synonyms,
                        boolean sensitive) {

    public static ColumnDto from(SchemaColumn column) {
        return new ColumnDto(column.getId(), column.getColumnName(), column.getDataType(),
                column.getDescription(), column.getSynonyms(), column.isSensitive());
    }
}
