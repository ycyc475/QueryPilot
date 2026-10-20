-- 02_analysis_schema.sql
-- 演示分析库（querypilot_analysis）业务表 DDL 与只读授权。
-- 由 postgres 超级用户执行，连接切换到分析库后 SET ROLE qp_analysis，使对象归属 qp_analysis。

\connect querypilot_analysis

SET ROLE qp_analysis;

CREATE TABLE categories (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE products (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id BIGINT NOT NULL REFERENCES categories(id),
    name        VARCHAR(200) NOT NULL,
    sku         VARCHAR(64) NOT NULL UNIQUE,
    unit_price  NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    status      VARCHAR(20) NOT NULL DEFAULT 'active'
);

CREATE TABLE customers (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,          -- 假名，不使用真实个人信息
    region     VARCHAR(20) NOT NULL,           -- 华东/华北/华南/西南/华中/东北/西北
    province   VARCHAR(40) NOT NULL,
    city       VARCHAR(40),
    segment    VARCHAR(20) NOT NULL,           -- new/regular/vip
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id    BIGINT NOT NULL REFERENCES customers(id),
    order_no       VARCHAR(32) NOT NULL UNIQUE,
    ordered_at     TIMESTAMPTZ NOT NULL,
    status         VARCHAR(20) NOT NULL,       -- paid / refunded / cancelled / pending
    payable_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    paid_amount    NUMERIC(12,2) NOT NULL DEFAULT 0,
    refund_amount  NUMERIC(12,2) NOT NULL DEFAULT 0,
    channel        VARCHAR(20) NOT NULL        -- app / web / h5
);

CREATE TABLE order_items (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id    BIGINT NOT NULL REFERENCES orders(id),
    product_id  BIGINT NOT NULL REFERENCES products(id),
    quantity    INT NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(12,2) NOT NULL,
    item_amount NUMERIC(12,2) NOT NULL
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_customers_region   ON customers(region);
CREATE INDEX idx_customers_province ON customers(province);
CREATE INDEX idx_orders_customer    ON orders(customer_id);
CREATE INDEX idx_orders_ordered_at  ON orders(ordered_at);
CREATE INDEX idx_orders_status      ON orders(status);
CREATE INDEX idx_order_items_order  ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- 只读账号：仅 SELECT 白名单表；后续新增表由 qp_analysis 创建时自动获得 SELECT 授权
GRANT USAGE ON SCHEMA public TO qp_analysis_ro;
GRANT SELECT ON categories, products, customers, orders, order_items TO qp_analysis_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE qp_analysis IN SCHEMA public
    GRANT SELECT ON TABLES TO qp_analysis_ro;

RESET ROLE;
