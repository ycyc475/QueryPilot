#!/usr/bin/env python3
"""核对/同步「分析库实际表结构」与「元数据库白名单（schema_tables/schema_columns）」。

- 分析库用只读账号（qp_analysis_ro）读 information_schema。
- 元库用 qp_meta 读 schema_tables/schema_columns。
- 输出差异报告：缺失表 / 多余表 / 缺失列 / 多余列（按表名+列名比对，忽略类型名差异）。
- 加 --sync 时把缺失的表/列写入元库（is_accessible=true，保留已有人工描述）。

用法：
    python scripts/schema_scan.py          # 只报告差异
    python scripts/schema_scan.py --sync   # 报告并同步缺失项
"""

import argparse

import psycopg2

SYSTEM_TABLES = {"flyway_schema_history"}


def parse_args():
    p = argparse.ArgumentParser(description="核对分析库与元数据库的表结构")
    p.add_argument("--analysis-db", default="querypilot_analysis")
    p.add_argument("--analysis-user", default="qp_analysis_ro")
    p.add_argument("--analysis-password", default="qp_analysis_ro_pw")
    p.add_argument("--meta-db", default="querypilot_meta")
    p.add_argument("--meta-user", default="qp_meta")
    p.add_argument("--meta-password", default="qp_meta_pw")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", default=5432, type=int)
    p.add_argument("--dataset-name", default="电商分析")
    p.add_argument("--sync", action="store_true", help="把缺失的表/列插入元库")
    return p.parse_args()


def actual_schema(cur):
    cur.execute(
        "SELECT table_name, column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' ORDER BY table_name, ordinal_position"
    )
    tables = {}
    for table, column in cur.fetchall():
        if table in SYSTEM_TABLES:
            continue
        tables.setdefault(table, []).append(column)
    return tables


def meta_schema(cur, dataset_name):
    cur.execute(
        "SELECT id, table_name, is_accessible FROM schema_tables "
        "WHERE dataset_id = (SELECT id FROM datasets WHERE name = %s) ORDER BY id",
        (dataset_name,),
    )
    tables = {row[1]: (row[0], row[2]) for row in cur.fetchall()}
    columns = {}
    for table_name, (table_id, _accessible) in tables.items():
        cur.execute("SELECT column_name FROM schema_columns WHERE table_id = %s ORDER BY id", (table_id,))
        columns[table_name] = [row[0] for row in cur.fetchall()]
    return tables, columns


def main():
    args = parse_args()
    aconn = psycopg2.connect(host=args.host, port=args.port, dbname=args.analysis_db,
                             user=args.analysis_user, password=args.analysis_password)
    mconn = psycopg2.connect(host=args.host, port=args.port, dbname=args.meta_db,
                             user=args.meta_user, password=args.meta_password)
    acur, mcur = aconn.cursor(), mconn.cursor()

    actual = actual_schema(acur)
    meta_tables, meta_columns = meta_schema(mcur, args.dataset_name)

    missing_tables = [t for t in actual if t not in meta_tables]
    extra_tables = [t for t in meta_tables if t not in actual]
    missing_columns = {}
    extra_columns = {}
    for table in sorted(set(actual) & set(meta_tables)):
        a = set(actual[table])
        m = set(meta_columns.get(table, []))
        if a - m:
            missing_columns[table] = sorted(a - m)
        if m - a:
            extra_columns[table] = sorted(m - a)

    print("实际分析库表数：%d，元库表数：%d" % (len(actual), len(meta_tables)))
    print("缺失表（分析库有、元库无）：%s" % (missing_tables or "无"))
    print("多余表（元库有、分析库无）：%s" % (extra_tables or "无"))
    print("缺失列：%s" % (missing_columns or "无"))
    print("多余列：%s" % (extra_columns or "无"))

    if args.sync and (missing_tables or missing_columns):
        mcur.execute("SELECT id FROM datasets WHERE name = %s", (args.dataset_name,))
        dataset_id = mcur.fetchone()[0]
        for table in missing_tables:
            mcur.execute(
                "INSERT INTO schema_tables (dataset_id, table_name, description, is_accessible) "
                "VALUES (%s, %s, %s, TRUE) RETURNING id",
                (dataset_id, table, "自动扫描发现"),
            )
            table_id = mcur.fetchone()[0]
            for column in actual[table]:
                mcur.execute(
                    "INSERT INTO schema_columns (table_id, column_name, description, is_sensitive) "
                    "VALUES (%s, %s, NULL, FALSE)",
                    (table_id, column),
                )
        for table, columns in missing_columns.items():
            mcur.execute(
                "SELECT id FROM schema_tables WHERE dataset_id = %s AND table_name = %s",
                (dataset_id, table),
            )
            table_id = mcur.fetchone()[0]
            for column in columns:
                mcur.execute(
                    "INSERT INTO schema_columns (table_id, column_name, description, is_sensitive) "
                    "VALUES (%s, %s, NULL, FALSE)",
                    (table_id, column),
                )
        mconn.commit()
        print("已同步缺失的表/列到元库。")

    acur.close(); mcur.close(); aconn.close(); mconn.close()


if __name__ == "__main__":
    main()
