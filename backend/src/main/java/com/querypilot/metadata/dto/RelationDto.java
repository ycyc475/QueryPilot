package com.querypilot.metadata.dto;

import com.querypilot.metadata.SchemaRelation;

public record RelationDto(String fromTable, String fromColumn, String toTable, String toColumn,
                          String relationType) {

    public static RelationDto from(SchemaRelation relation) {
        return new RelationDto(relation.getFromTable(), relation.getFromColumn(),
                relation.getToTable(), relation.getToColumn(), relation.getRelationType());
    }
}
