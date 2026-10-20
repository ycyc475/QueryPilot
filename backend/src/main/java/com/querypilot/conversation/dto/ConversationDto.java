package com.querypilot.conversation.dto;

import java.time.Instant;
import java.util.List;

public record ConversationDto(Long id, Long datasetId, List<MessageDto> messages, Instant createdAt) {
}
