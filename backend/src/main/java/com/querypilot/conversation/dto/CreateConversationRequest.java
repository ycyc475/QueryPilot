package com.querypilot.conversation.dto;

import jakarta.validation.constraints.NotNull;

public record CreateConversationRequest(@NotNull(message = "数据集不能为空") Long datasetId) {
}
