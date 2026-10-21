package com.querypilot.conversation.dto;

import com.querypilot.conversation.QueryRun;

import java.time.Instant;

public record QueryRunDto(Long id, Long conversationId, String question, String status,
                          String validationStatus, String sqlText, Long durationMs,
                          Integer rowCount, String errorCode, Instant createdAt) {

    public static QueryRunDto from(QueryRun run) {
        return new QueryRunDto(run.getId(), run.getConversationId(), run.getQuestion(), run.getStatus(),
                run.getValidationStatus(), run.getSqlText(), run.getDurationMs(), run.getRowCount(),
                run.getErrorCode(), run.getCreatedAt());
    }
}
