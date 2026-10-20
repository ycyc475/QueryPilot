package com.querypilot.metadata.dto;

import java.util.List;

public record SchemaDto(Long datasetId, List<TableDto> tables, List<RelationDto> relations,
                        List<MetricDto> metrics) {
}
