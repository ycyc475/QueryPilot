-- V2: 会话、消息、查询执行与审计（本阶段只建表，接口在后续阶段实现）
CREATE TABLE conversations (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id      BIGINT NOT NULL REFERENCES users(id),
    dataset_id   BIGINT NOT NULL REFERENCES datasets(id),
    context_json JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE messages (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id),
    role            VARCHAR(20) NOT NULL,
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE query_runs (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id   BIGINT NOT NULL REFERENCES conversations(id),
    question          TEXT NOT NULL,
    query_plan_json   JSONB,
    sql_text          TEXT,
    validation_status VARCHAR(30),
    status            VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    duration_ms       BIGINT,
    row_count         INTEGER,
    chart_spec_json   JSONB,
    error_code        VARCHAR(50),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT,
    action      VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    status      VARCHAR(20) NOT NULL,
    detail_json JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_conversations_user     ON conversations(user_id);
CREATE INDEX idx_messages_conversation  ON messages(conversation_id);
CREATE INDEX idx_query_runs_conversation ON query_runs(conversation_id);
CREATE INDEX idx_audit_logs_user        ON audit_logs(user_id);
