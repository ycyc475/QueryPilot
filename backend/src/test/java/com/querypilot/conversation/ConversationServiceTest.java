package com.querypilot.conversation;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.querypilot.conversation.dto.QueryRunResultDto;
import com.querypilot.user.User;
import com.querypilot.user.UserRepository;
import org.junit.jupiter.api.Test;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class ConversationServiceTest {

    private final ConversationRepository conversationRepository = mock(ConversationRepository.class);
    private final MessageRepository messageRepository = mock(MessageRepository.class);
    private final QueryRunRepository queryRunRepository = mock(QueryRunRepository.class);
    private final UserRepository userRepository = mock(UserRepository.class);
    private final AgentClient agentClient = mock(AgentClient.class);
    private final ObjectMapper objectMapper = new ObjectMapper();

    private final ConversationService service = new ConversationService(
            conversationRepository, messageRepository, queryRunRepository,
            userRepository, agentClient, objectMapper);

    @Test
    void askParsesAgentResponseAndReturnsResult() {
        User user = new User();
        user.setId(1L);
        user.setEmail("demo@querypilot.dev");
        when(userRepository.findByEmail("demo@querypilot.dev")).thenReturn(Optional.of(user));

        Conversation conversation = new Conversation();
        conversation.setId(10L);
        conversation.setUserId(1L);
        conversation.setDatasetId(1L);
        when(conversationRepository.findById(10L)).thenReturn(Optional.of(conversation));

        String agentJson = """
                {"code":0,"query_plan":{"metric":"paid_sales","dimensions":["date"]},
                 "sql":"SELECT 1","columns":[{"name":"date","type":"date"}],
                 "rows":[["2026-10-19",100.0]],"row_count":1,
                 "chart":{"type":"line","x_field":"date","y_field":"metric_value"},
                 "summary":"共 1 条结果","duration_ms":12}""";
        when(agentClient.ask("最近30天销售额", 1L)).thenReturn(agentJson);

        when(queryRunRepository.save(any(QueryRun.class))).thenAnswer(inv -> {
            QueryRun run = inv.getArgument(0);
            if (run.getId() == null) {
                run.setId(99L);
            }
            return run;
        });

        QueryRunResultDto result = service.ask(10L, "最近30天销售额", "demo@querypilot.dev");

        assertThat(result.runId()).isEqualTo(99L);
        assertThat(result.sql()).isEqualTo("SELECT 1");
        assertThat(result.summary()).isEqualTo("共 1 条结果");
        assertThat(result.rowCount()).isEqualTo(1);
    }
}
