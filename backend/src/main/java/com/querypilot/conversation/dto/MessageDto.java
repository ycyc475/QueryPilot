package com.querypilot.conversation.dto;

import com.querypilot.conversation.Message;

import java.time.Instant;

public record MessageDto(Long id, String role, String content, Instant createdAt) {

    public static MessageDto from(Message message) {
        return new MessageDto(message.getId(), message.getRole(), message.getContent(), message.getCreatedAt());
    }
}
