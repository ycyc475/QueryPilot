package com.querypilot.metadata.dto;

import java.util.List;

public record TableMatchDto(TableDto table, String matchedTerm, List<ColumnMatchDto> columns) {
}
