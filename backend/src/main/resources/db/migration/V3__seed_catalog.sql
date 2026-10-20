-- V3: 数据目录元数据与指标口径种子（演示数据）
-- 用户账号不在此处种子（需 bcrypt 哈希，由 Java DataSeeder 写入）

INSERT INTO data_sources (name, db_type, secret_ref, status)
VALUES ('演示电商分析库', 'postgresql', 'ANALYSIS_DB_RO', 'active');

INSERT INTO datasets (source_id, name, description)
SELECT id, '电商分析', '模拟电商订单/客户/商品/品类/区域数据，用于对话式数据分析演示'
FROM data_sources
WHERE name = '演示电商分析库';

INSERT INTO schema_tables (dataset_id, table_name, description)
SELECT d.id, v.tbl, v.descr
FROM datasets d
CROSS JOIN (VALUES
    ('orders',      '订单主表：下单时间、状态、实付/应付/退款金额、渠道'),
    ('order_items', '订单明细：商品、数量、单价、明细金额'),
    ('customers',   '客户：地区/省份/城市、客户分层（假名）'),
    ('products',    '商品：品类、SKU、单价'),
    ('categories',  '品类目录')
) AS v(tbl, descr)
WHERE d.name = '电商分析';

INSERT INTO schema_columns (table_id, column_name, data_type, description, is_sensitive)
SELECT t.id, v.col, v.dtype, v.descr, FALSE
FROM schema_tables t
JOIN datasets d ON d.id = t.dataset_id
CROSS JOIN (VALUES
    ('orders',      'id',             'bigint',     '订单主键'),
    ('orders',      'customer_id',    'bigint',     '客户ID，关联 customers.id'),
    ('orders',      'order_no',       'varchar',    '订单号'),
    ('orders',      'ordered_at',     'timestamptz','下单时间（指标时间口径）'),
    ('orders',      'status',         'varchar',    '订单状态：paid/refunded/cancelled/pending'),
    ('orders',      'payable_amount', 'numeric',    '应付金额'),
    ('orders',      'paid_amount',    'numeric',    '实付金额'),
    ('orders',      'refund_amount',  'numeric',    '退款金额'),
    ('orders',      'channel',        'varchar',    '渠道：app/web/h5'),
    ('order_items', 'id',             'bigint',     '明细主键'),
    ('order_items', 'order_id',       'bigint',     '订单ID，关联 orders.id'),
    ('order_items', 'product_id',     'bigint',     '商品ID，关联 products.id'),
    ('order_items', 'quantity',       'int',        '数量'),
    ('order_items', 'unit_price',     'numeric',    '成交单价'),
    ('order_items', 'item_amount',    'numeric',    '明细金额'),
    ('customers',   'id',             'bigint',     '客户主键'),
    ('customers',   'name',           'varchar',    '客户姓名（假名，非真实个人信息）'),
    ('customers',   'region',         'varchar',    '大区：华东/华北/华南/西南/华中/东北/西北'),
    ('customers',   'province',       'varchar',    '省份'),
    ('customers',   'city',           'varchar',    '城市'),
    ('customers',   'segment',        'varchar',    '客户分层：new/regular/vip'),
    ('customers',   'created_at',     'timestamptz','注册时间'),
    ('products',    'id',             'bigint',     '商品主键'),
    ('products',    'category_id',    'bigint',     '品类ID，关联 categories.id'),
    ('products',    'name',           'varchar',    '商品名称'),
    ('products',    'sku',            'varchar',    'SKU 编码'),
    ('products',    'unit_price',     'numeric',    '标准单价'),
    ('products',    'status',         'varchar',    '商品状态：active/inactive'),
    ('categories',  'id',             'bigint',     '品类主键'),
    ('categories',  'name',           'varchar',    '品类名称'),
    ('categories',  'description',    'text',       '品类描述')
) AS v(tbl, col, dtype, descr)
WHERE d.name = '电商分析' AND t.table_name = v.tbl;

INSERT INTO schema_relations (dataset_id, from_table, from_column, to_table, to_column, relation_type)
SELECT d.id, v.f, v.fc, v.t, v.tc, 'many_to_one'
FROM datasets d
CROSS JOIN (VALUES
    ('orders',      'customer_id', 'customers', 'id'),
    ('order_items', 'order_id',    'orders',    'id'),
    ('order_items', 'product_id',  'products',  'id'),
    ('products',    'category_id', 'categories','id')
) AS v(f, fc, t, tc)
WHERE d.name = '电商分析';

INSERT INTO business_metrics (dataset_id, name, definition, expression, time_column)
SELECT d.id, v.name, v.def, v.expr, v.tc
FROM datasets d
CROSS JOIN (VALUES
    ('实付销售额', '已支付订单（orders.status=''paid''）的实付金额（orders.paid_amount）之和；退款（refunded）与取消（cancelled）订单不计入。时间口径按 ordered_at 计算。',
     'SUM(orders.paid_amount)', 'ordered_at'),
    ('订单量', '已支付订单（orders.status=''paid''）的订单数。',
     'COUNT(orders.id)', 'ordered_at'),
    ('客单价', '实付销售额除以已支付订单数。',
     'SUM(orders.paid_amount) / COUNT(orders.id)', 'ordered_at')
) AS v(name, def, expr, tc)
WHERE d.name = '电商分析';
