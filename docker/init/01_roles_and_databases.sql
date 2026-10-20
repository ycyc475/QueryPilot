-- 01_roles_and_databases.sql
-- 创建应用账号与两个数据库。由 postgres 超级用户执行（docker-entrypoint-initdb.d）。
-- 说明：分析库账号 qp_analysis_ro 仅用于只读查询，属于安全基线，后续 Agent 执行 SQL 也只用该账号。

CREATE ROLE qp_meta LOGIN PASSWORD 'qp_meta_pw';
CREATE ROLE qp_analysis LOGIN PASSWORD 'qp_analysis_pw';
CREATE ROLE qp_analysis_ro LOGIN PASSWORD 'qp_analysis_ro_pw'
    NOSUPERUSER NOCREATEDB NOCREATEROLE;

CREATE DATABASE querypilot_meta OWNER qp_meta;
CREATE DATABASE querypilot_analysis OWNER qp_analysis;

-- 只读账号兜底：单语句超时 + 会话级只读（AST 校验之外的数据库层约束）
ALTER ROLE qp_analysis_ro SET statement_timeout = '30s';
ALTER ROLE qp_analysis_ro SET default_transaction_read_only = on;
