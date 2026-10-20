package com.querypilot.conversation;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.querypilot.common.BusinessException;
import com.querypilot.conversation.dto.ConversationDto;
import com.querypilot.conversation.dto.MessageDto;
import com.querypilot.conversation.dto.QueryRunResultDto;
import com.querypilot.user.User;
import com.querypilot.user.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class ConversationService {

    private static final Logger log = LoggerFactory.getLogger(ConversationService.class);

    private final ConversationRepository conversationRepository;
    private final MessageRepository messageRepository;
    private final QueryRunRepository queryRunRepository;
    private final UserRepository userRepository;
    private final AgentClient agentClient;
    private final ObjectMapper objectMapper;

    public ConversationService(ConversationRepository conversationRepository,
                               MessageRepository messageRepository,
                               QueryRunRepository queryRunRepository,
                               UserRepository userRepository,
                               AgentClient agentClient,
                               ObjectMapper objectMapper) {
        this.conversationRepository = conversationRepository;
        this.messageRepository = messageRepository;
        this.queryRunRepository = queryRunRepository;
        this.userRepository = userRepository;
        this.agentClient = agentClient;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public ConversationDto createConversation(String email, Long datasetId) {
        User user = requireUser(email);
        Conversation conversation = new Conversation();
        conversation.setUserId(user.getId());
        conversation.setDatasetId(datasetId);
        conversation = conversationRepository.save(conversation);
        return toDto(conversation, List.of());
    }

    @Transactional(readOnly = true)
    public ConversationDto getConversation(Long id, String email) {
        Conversation conversation = ownedConversation(id, email);
        List<MessageDto> messages = messageRepository.findByConversationIdOrderByIdAsc(id).stream()
                .map(MessageDto::from).toList();
        return toDto(conversation, messages);
    }

    @Transactional
    public QueryRunResultDto ask(Long conversationId, String question, String email) {
        Conversation conversation = ownedConversation(conversationId, email);

        saveMessage(conversationId, "user", question);

        QueryRun run = new QueryRun();
        run.setConversationId(conversationId);
        run.setQuestion(question);
        run.setStatus("RUNNING");
        run = queryRunRepository.save(run);

        String agentJson;
        try {
            agentJson = agentClient.ask(question, conversation.getDatasetId());
        } catch (Exception e) {
            fail(run, "AGENT_UNAVAILABLE");
            throw new BusinessException(HttpStatus.BAD_GATEWAY, "查询服务不可用");
        }

        JsonNode node;
        try {
            node = objectMapper.readTree(agentJson);
        } catch (JsonProcessingException e) {
            fail(run, "AGENT_ERROR");
            throw new BusinessException(HttpStatus.BAD_GATEWAY, "查询服务返回异常");
        }

        if (node.path("code").asInt(-1) != 0) {
            String error = node.path("error").asText("查询失败");
            log.warn("agent 返回错误，原始响应: {}", agentJson);
            fail(run, error);
            throw new BusinessException(HttpStatus.BAD_REQUEST, error);
        }

        String sql = node.path("sql").asText();
        String summary = node.path("summary").asText();
        long durationMs = node.path("duration_ms").asLong();
        int rowCount = node.path("row_count").asInt();

        run.setStatus("SUCCEEDED");
        run.setValidationStatus("PASSED");
        run.setSqlText(sql);
        run.setQueryPlanJson(node.path("query_plan").toString());
        run.setChartSpecJson(node.path("chart").toString());
        run.setDurationMs(durationMs);
        run.setRowCount(rowCount);
        queryRunRepository.save(run);

        saveMessage(conversationId, "assistant", summary);

        return new QueryRunResultDto(run.getId(), sql, node.path("columns"), node.path("rows"),
                rowCount, node.path("chart"), summary, durationMs);
    }

    private void fail(QueryRun run, String errorCode) {
        run.setStatus("FAILED");
        run.setErrorCode(errorCode);
        queryRunRepository.save(run);
    }

    private void saveMessage(Long conversationId, String role, String content) {
        Message message = new Message();
        message.setConversationId(conversationId);
        message.setRole(role);
        message.setContent(content);
        messageRepository.save(message);
    }

    private Conversation ownedConversation(Long id, String email) {
        User user = requireUser(email);
        Conversation conversation = conversationRepository.findById(id)
                .orElseThrow(() -> new BusinessException(HttpStatus.NOT_FOUND, "会话不存在: " + id));
        if (!conversation.getUserId().equals(user.getId())) {
            throw new BusinessException(HttpStatus.FORBIDDEN, "无权访问该会话");
        }
        return conversation;
    }

    private User requireUser(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException(HttpStatus.UNAUTHORIZED, "用户不存在"));
    }

    private ConversationDto toDto(Conversation conversation, List<MessageDto> messages) {
        return new ConversationDto(conversation.getId(), conversation.getDatasetId(), messages,
                conversation.getCreatedAt());
    }
}
