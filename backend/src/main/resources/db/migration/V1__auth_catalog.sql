-- V1: 认证与数据目录元数据
CREATE TABLE users (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name  VARCHAR(100),
    role          VARCHAR(20)  NOT NULL DEFAULT 'ANALYST',
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE data_sources (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    db_type    VARCHAR(30)  NOT NULL DEFAULT 'postgresql',
    secret_ref VARCHAR(100) NOT NULL,      -- 指向环境变量，不存明文密码
    status     VARCHAR(20)  NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE datasets (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id   BIGINT NOT NULL REFERENCES data_sources(id),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE schema_tables (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id    BIGINT NOT NULL REFERENCES datasets(id),
    table_name    VARCHAR(100) NOT NULL,
    description   TEXT,
    is_accessible BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (dataset_id, table_name)
);

CREATE TABLE schema_columns (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    table_id     BIGINT NOT NULL REFERENCES schema_tables(id),
    column_name  VARCHAR(100) NOT NULL,
    data_type    VARCHAR(50),
    description  TEXT,
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (table_id, column_name)
);

CREATE TABLE schema_relations (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id    BIGINT NOT NULL REFERENCES datasets(id),
    from_table    VARCHAR(100) NOT NULL,
    from_column   VARCHAR(100) NOT NULL,
    to_table      VARCHAR(100) NOT NULL,
    to_column     VARCHAR(100) NOT NULL,
    relation_type VARCHAR(20)  NOT NULL DEFAULT 'many_to_one'
);

CREATE TABLE business_metrics (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id  BIGINT NOT NULL REFERENCES datasets(id),
    name        VARCHAR(100) NOT NULL,
    definition  TEXT NOT NULL,
    expression  TEXT NOT NULL,
    time_column VARCHAR(100),
    UNIQUE (dataset_id, name)
);
