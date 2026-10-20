package com.querypilot.metadata.dto;

import java.util.List;

public record SearchResultDto(Long datasetId, String query, List<MetricMatchDto> metrics,
                              List<TableMatchDto> tables) {
}
