package com.querypilot.conversation.dto;

import jakarta.validation.constraints.NotBlank;

public record AskRequest(@NotBlank(message = "问题不能为空") String content) {
}
