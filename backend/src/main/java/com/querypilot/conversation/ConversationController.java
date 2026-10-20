package com.querypilot.conversation;

import com.querypilot.common.ApiResponse;
import com.querypilot.conversation.dto.AskRequest;
import com.querypilot.conversation.dto.ConversationDto;
import com.querypilot.conversation.dto.CreateConversationRequest;
import com.querypilot.conversation.dto.QueryRunResultDto;
import jakarta.validation.Valid;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/conversations")
public class ConversationController {

    private final ConversationService conversationService;

    public ConversationController(ConversationService conversationService) {
        this.conversationService = conversationService;
    }

    @PostMapping
    public ApiResponse<ConversationDto> create(@Valid @RequestBody CreateConversationRequest request,
                                               Authentication authentication) {
        return ApiResponse.ok(conversationService.createConversation(authentication.getName(), request.datasetId()));
    }

    @GetMapping("/{id}")
    public ApiResponse<ConversationDto> get(@PathVariable Long id, Authentication authentication) {
        return ApiResponse.ok(conversationService.getConversation(id, authentication.getName()));
    }

    @PostMapping("/{id}/messages")
    public ApiResponse<QueryRunResultDto> ask(@PathVariable Long id,
                                              @Valid @RequestBody AskRequest request,
                                              Authentication authentication) {
        return ApiResponse.ok(conversationService.ask(id, request.content(), authentication.getName()));
    }
}
