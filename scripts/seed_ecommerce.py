#!/usr/bin/env python3
"""生成确定性模拟电商数据，写入 querypilot_analysis（写账号 qp_analysis）。

- 固定随机种子 => 重复运行得到完全一致的数据（可复现评测）。
- 默认 TRUNCATE 后重建（演示分析库，非生产数据）；应用侧使用只读账号 qp_analysis_ro 访问。
- 指标口径：实付销售额 = status='paid' 的 SUM(paid_amount)；退款/取消订单不计入。

用法：
    python scripts/seed_ecommerce.py
    python scripts/seed_ecommerce.py --seed 42 --orders 60000 --customers 5000
"""

import argparse
import datetime
import random
import sys

import psycopg2
from psycopg2.extras import execute_values

REGION_PROVINCES = {
    "华东": ["上海", "江苏", "浙江", "安徽", "福建", "江西", "山东"],
    "华北": ["北京", "天津", "河北", "山西", "内蒙古"],
    "华南": ["广东", "广西", "海南"],
    "华中": ["河南", "湖北", "湖南"],
    "西南": ["重庆", "四川", "贵州", "云南", "西藏"],
    "东北": ["辽宁", "吉林", "黑龙江"],
    "西北": ["陕西", "甘肃", "青海", "宁夏", "新疆"],
}
PROVINCE_TO_REGION = {p: r for r, ps in REGION_PROVINCES.items() for p in ps}
PROVINCES = list(PROVINCE_TO_REGION.keys())

# 近似人口权重（用于让客户/订单分布更贴近真实，避免均匀分布导致小省份销量虚高）
PROVINCE_WEIGHTS = {
    "广东": 126, "山东": 101, "河南": 99, "江苏": 85, "四川": 84, "河北": 74,
    "湖南": 66, "浙江": 65, "安徽": 61, "湖北": 58, "广西": 50, "云南": 47,
    "江西": 45, "辽宁": 43, "福建": 42, "陕西": 40, "贵州": 39, "山西": 35,
    "重庆": 32, "黑龙江": 31, "新疆": 26, "甘肃": 25, "上海": 25, "吉林": 24,
    "内蒙古": 24, "北京": 22, "天津": 14, "海南": 10, "宁夏": 7, "青海": 6,
    "西藏": 4,
}

CAPITALS = {
    "上海": ["上海"], "江苏": ["南京", "苏州", "无锡"], "浙江": ["杭州", "宁波", "温州"],
    "安徽": ["合肥", "芜湖"], "福建": ["福州", "厦门", "泉州"], "江西": ["南昌", "赣州"],
    "山东": ["济南", "青岛", "烟台"], "北京": ["北京"], "天津": ["天津"],
    "河北": ["石家庄", "唐山"], "山西": ["太原", "大同"], "内蒙古": ["呼和浩特", "包头"],
    "广东": ["广州", "深圳", "东莞"], "广西": ["南宁", "桂林"], "海南": ["海口", "三亚"],
    "河南": ["郑州", "洛阳"], "湖北": ["武汉", "宜昌"], "湖南": ["长沙", "株洲"],
    "重庆": ["重庆"], "四川": ["成都", "绵阳"], "贵州": ["贵阳", "遵义"],
    "云南": ["昆明", "大理"], "西藏": ["拉萨"], "辽宁": ["沈阳", "大连"],
    "吉林": ["长春", "吉林"], "黑龙江": ["哈尔滨", "大庆"], "陕西": ["西安", "咸阳"],
    "甘肃": ["兰州", "天水"], "青海": ["西宁"], "宁夏": ["银川"], "新疆": ["乌鲁木齐", "喀什"],
}

CATEGORIES = [
    ("数码家电", "手机、电脑、家电等数码产品"),
    ("服饰鞋包", "服装、鞋靴、箱包"),
    ("美妆个护", "护肤、彩妆、洗护"),
    ("食品生鲜", "零食、粮油、生鲜"),
    ("家居日用", "家纺、厨具、清洁"),
    ("母婴玩具", "母婴用品与儿童玩具"),
    ("运动户外", "运动装备与户外用品"),
    ("图书文娱", "图书、文具与影音"),
]

PRODUCTS_BY_CATEGORY = {
    "数码家电": ["智能手机 Pro", "蓝牙耳机", "笔记本电脑", "智能手表", "无线充电器"],
    "服饰鞋包": ["休闲T恤", "牛仔长裤", "运动跑鞋", "双肩背包", "针织毛衣"],
    "美妆个护": ["保湿面霜", "氨基酸洗面奶", "丝绒口红", "防晒霜", "去屑洗发水"],
    "食品生鲜": ["每日坚果礼盒", "有机大米", "新鲜草莓", "纯牛奶", "速溶咖啡"],
    "家居日用": ["全棉四件套", "保温杯", "收纳箱", "洗衣液", "不锈钢锅具"],
    "母婴玩具": ["婴儿纸尿裤", "儿童积木", "婴儿推车", "绘本套装", "儿童水杯"],
    "运动户外": ["瑜伽垫", "登山背包", "羽毛球拍", "跑步腰包", "露营帐篷"],
    "图书文娱": ["畅销小说", "钢笔套装", "手账本", "蓝牙音箱", "拼图"],
}

PRICE_RANGES = {
    "数码家电": (99, 8999),
    "服饰鞋包": (39, 999),
    "美妆个护": (19, 599),
    "食品生鲜": (9, 299),
    "家居日用": (15, 799),
    "母婴玩具": (29, 1999),
    "运动户外": (19, 2999),
    "图书文娱": (9, 299),
}

SURNAMES = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴", "徐", "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "郑"]
GIVEN_NAMES = ["伟", "芳", "娜", "敏", "静", "磊", "军", "洋", "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平", "刚", "桂英", "强", "丽", "俊", "雪"]

CHANNELS = ["app", "web", "h5"]
CHANNEL_WEIGHTS = [45, 35, 20]
SEGMENTS = ["new", "regular", "vip"]
SEGMENT_WEIGHTS = [50, 35, 15]
STATUSES = ["paid", "refunded", "cancelled", "pending"]
STATUS_WEIGHTS = [80, 8, 7, 5]


def parse_args():
    p = argparse.ArgumentParser(description="Seed deterministic mock e-commerce data.")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", default=5432, type=int)
    p.add_argument("--dbname", default="querypilot_analysis")
    p.add_argument("--user", default="qp_analysis")
    p.add_argument("--password", default="qp_analysis_pw")
    p.add_argument("--seed", default=42, type=int, help="随机种子（固定以保证可复现）")
    p.add_argument("--customers", default=5000, type=int)
    p.add_argument("--orders", default=60000, type=int)
    return p.parse_args()


def random_name(rng):
    name = rng.choice(SURNAMES) + rng.choice(GIVEN_NAMES)
    if rng.random() < 0.3:
        name += rng.choice(GIVEN_NAMES)
    return name


def weighted(rng, values, weights):
    return rng.choices(values, weights=weights, k=1)[0]


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    now = datetime.datetime.now(datetime.timezone.utc)

    conn = psycopg2.connect(
        host=args.host, port=args.port, dbname=args.dbname,
        user=args.user, password=args.password,
    )
    conn.autocommit = False
    cur = conn.cursor()

    print("截断并重建模拟数据（固定种子 = %d）..." % args.seed)
    cur.execute("TRUNCATE TABLE order_items, orders, customers, products, categories RESTART IDENTITY CASCADE")

    # 品类（id 1..8）
    category_rows = [(name, desc) for name, desc in CATEGORIES]
    execute_values(cur, "INSERT INTO categories (name, description) VALUES %s", category_rows)

    # 商品（id 1..40，按品类顺序）
    product_rows = []
    products = []  # (id, unit_price)
    pid = 0
    for cat_idx, (cat_name, _) in enumerate(CATEGORIES):
        cat_id = cat_idx + 1
        lo, hi = PRICE_RANGES[cat_name]
        for pname in PRODUCTS_BY_CATEGORY[cat_name]:
            pid += 1
            price = round(rng.uniform(lo, hi), 2)
            sku = "P%04d" % pid
            product_rows.append((cat_id, pname, sku, price, "active"))
            products.append((pid, price))
    execute_values(cur, "INSERT INTO products (category_id, name, sku, unit_price, status) VALUES %s", product_rows)

    # 客户（id 1..N）
    customer_rows = []
    province_pool = PROVINCES
    province_weights = [PROVINCE_WEIGHTS[p] for p in PROVINCES]
    for _ in range(args.customers):
        province = rng.choices(province_pool, weights=province_weights, k=1)[0]
        region = PROVINCE_TO_REGION[province]
        city = rng.choice(CAPITALS[province])
        name = random_name(rng)
        segment = weighted(rng, SEGMENTS, SEGMENT_WEIGHTS)
        created_at = now - datetime.timedelta(seconds=rng.randint(0, 3 * 365 * 86400))
        customer_rows.append((name, region, province, city, segment, created_at))
    execute_values(cur, "INSERT INTO customers (name, region, province, city, segment, created_at) VALUES %s", customer_rows)

    # 订单 + 明细（订单 id 1..N，明细 order_id 与订单序号一致）
    order_rows = []
    item_rows = []
    for i in range(args.orders):
        order_id = i + 1
        customer_id = rng.randint(1, args.customers)
        ordered_at = now - datetime.timedelta(seconds=rng.randint(0, 2 * 365 * 86400))
        status = weighted(rng, STATUSES, STATUS_WEIGHTS)
        channel = weighted(rng, CHANNELS, CHANNEL_WEIGHTS)
        n_items = weighted(rng, [1, 2, 3, 4, 5], [40, 30, 20, 7, 3])
        payable = 0.0
        for _ in range(n_items):
            prod_id, unit_price = rng.choice(products)
            qty = rng.randint(1, 3)
            amt = round(qty * unit_price, 2)
            payable += amt
            item_rows.append((order_id, prod_id, qty, unit_price, amt))
        payable = round(payable, 2)
        if status == "paid":
            paid, refund = payable, 0.0
        elif status == "refunded":
            paid, refund = payable, payable
        else:  # cancelled / pending
            paid, refund = 0.0, 0.0
        order_no = "SO%s%06d" % (ordered_at.strftime("%Y%m%d"), i)
        order_rows.append((customer_id, order_no, ordered_at, status, payable, paid, refund, channel))

    execute_values(
        cur,
        "INSERT INTO orders (customer_id, order_no, ordered_at, status, payable_amount, paid_amount, refund_amount, channel) VALUES %s",
        order_rows,
        page_size=1000,
    )
    execute_values(
        cur,
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price, item_amount) VALUES %s",
        item_rows,
        page_size=1000,
    )

    conn.commit()

    cur.execute("SELECT (SELECT count(*) FROM categories), (SELECT count(*) FROM products), "
                "(SELECT count(*) FROM customers), (SELECT count(*) FROM orders), (SELECT count(*) FROM order_items)")
    cats, prods, custs, orders, items = cur.fetchone()
    print("写入完成：品类 %d，商品 %d，客户 %d，订单 %d，明细 %d" % (cats, prods, custs, orders, items))

    cur.execute("SELECT count(*), coalesce(sum(paid_amount), 0) FROM orders WHERE status = 'paid'")
    paid_cnt, paid_sum = cur.fetchone()
    print("指标校验：已支付订单 %d 笔，实付销售额合计 = %.2f" % (paid_cnt, paid_sum))

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
