package com.querypilot.conversation.dto;

import com.fasterxml.jackson.databind.JsonNode;

public record QueryRunResultDto(Long runId, String sql, JsonNode columns, JsonNode rows, Integer rowCount,
                                JsonNode chart, String summary, Long durationMs) {
}
