package com.querypilot.metadata.dto;

import com.querypilot.metadata.SchemaTable;

import java.util.List;

public record TableDto(Long id, String name, String description, String synonyms, List<ColumnDto> columns) {

    public static TableDto from(SchemaTable table, List<ColumnDto> columns) {
        return new TableDto(table.getId(), table.getTableName(), table.getDescription(),
                table.getSynonyms(), columns);
    }
}
