package com.querypilot.conversation;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.Proxy;

/**
 * 调用 Python Agent 服务（/ask）的 HTTP 客户端，返回原始 JSON 字符串。
 * 显式用 ObjectMapper 序列化请求体，并禁用代理（本机系统代理会转坏 localhost 请求）。
 */
@Component
public class AgentClient {

    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    public AgentClient(@Value("${app.agent.base-url:http://localhost:8000}") String baseUrl,
                       ObjectMapper objectMapper) {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setProxy(Proxy.NO_PROXY);
        this.restClient = RestClient.builder().baseUrl(baseUrl).requestFactory(factory).build();
        this.objectMapper = objectMapper;
    }

    public String ask(String question, Long datasetId, String contextJson) {
        String json;
        try {
            ObjectNode body = objectMapper.createObjectNode();
            body.put("question", question);
            body.put("dataset_id", datasetId);
            if (contextJson != null && !contextJson.isBlank()) {
                body.set("context", objectMapper.readTree(contextJson));
            }
            json = objectMapper.writeValueAsString(body);
        } catch (JsonProcessingException e) {
            throw new IllegalStateException("序列化请求失败", e);
        }
        return restClient.post()
                .uri("/ask")
                .contentType(MediaType.APPLICATION_JSON)
                .body(json)
                .retrieve()
                .onStatus(HttpStatusCode::isError, (request, response) -> { /* 吞掉错误，交给调用方解析 */ })
                .body(String.class);
    }
}
