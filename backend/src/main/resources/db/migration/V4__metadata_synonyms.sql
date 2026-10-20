-- V4: 语义元数据 —— 同义词字段与补种（用于词典/关键词召回）

ALTER TABLE schema_tables ADD COLUMN synonyms TEXT;
ALTER TABLE schema_columns ADD COLUMN synonyms TEXT;
ALTER TABLE business_metrics ADD COLUMN synonyms TEXT;

-- 表级同义词
UPDATE schema_tables SET synonyms = CASE table_name
    WHEN 'orders'      THEN '订单'
    WHEN 'order_items' THEN '订单明细,明细,订单行'
    WHEN 'customers'   THEN '客户,用户'
    WHEN 'products'    THEN '商品,SKU'
    WHEN 'categories'  THEN '品类,类目,分类'
END;

-- 字段级同义词（按表+字段精确匹配）
UPDATE schema_columns sc
SET synonyms = v.syn
FROM (VALUES
    ('orders',      'customer_id',    '客户ID,客户'),
    ('orders',      'order_no',       '订单号,单号'),
    ('orders',      'ordered_at',     '下单时间,时间,日期,下单日期'),
    ('orders',      'status',         '订单状态,状态'),
    ('orders',      'payable_amount', '应付金额,应付'),
    ('orders',      'paid_amount',    '实付金额,实付,支付金额,销售额,营收,收入'),
    ('orders',      'refund_amount',  '退款金额,退款'),
    ('orders',      'channel',        '渠道,来源'),
    ('order_items', 'order_id',       '订单ID,订单'),
    ('order_items', 'product_id',     '商品ID,商品'),
    ('order_items', 'quantity',       '数量,件数'),
    ('order_items', 'unit_price',     '单价,价格'),
    ('order_items', 'item_amount',    '明细金额,金额,小计'),
    ('customers',   'name',           '客户姓名,姓名,名称'),
    ('customers',   'region',         '地区,区域,大区'),
    ('customers',   'province',       '省份,省'),
    ('customers',   'city',           '城市,市'),
    ('customers',   'segment',        '客户分层,分层,会员等级'),
    ('customers',   'created_at',     '注册时间,创建时间'),
    ('products',    'category_id',    '品类ID,类目ID'),
    ('products',    'name',           '商品名称,名称'),
    ('products',    'sku',            'SKU,货号'),
    ('products',    'unit_price',     '单价,价格,标准价'),
    ('products',    'status',         '商品状态,状态'),
    ('categories',  'name',           '品类名称,名称'),
    ('categories',  'description',    '品类描述,描述')
) AS v(tbl, col, syn)
JOIN schema_tables st ON st.table_name = v.tbl
WHERE sc.table_id = st.id AND sc.column_name = v.col;

-- 指标级同义词
UPDATE business_metrics SET synonyms = CASE name
    WHEN '实付销售额' THEN '销售额,营收,收入,GMV'
    WHEN '订单量'     THEN '订单数,单量,订单数量'
    WHEN '客单价'     THEN '客单,客单价,ARPU,人均消费'
END;
