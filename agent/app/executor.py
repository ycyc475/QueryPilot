"""只读执行：用 qp_analysis_ro 账号执行「已校验」的 SQL，带超时与行数上限。

返回列名+类型、行（转为 JSON 可序列化）与耗时；错误按类别分类（timeout/permission/syntax/other）。
"""

import time
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

import psycopg2
from psycopg2 import errors as pg_errors


class ExecutionError(Exception):
    def __init__(self, kind: str, message: str):
        self.kind = kind
        self.message = message
        super().__init__(f"{kind}: {message}")


class Executor:
    def __init__(self, dsn: dict, timeout_ms: int = 30000, max_rows: int = 10000):
        self.dsn = dsn
        self.timeout_ms = timeout_ms
        self.max_rows = max_rows

    def execute(self, sql: str) -> dict:
        start = time.monotonic()
        try:
            with psycopg2.connect(**self.dsn, connect_timeout=5) as conn:
                conn.set_session(readonly=True, autocommit=True)
                with conn.cursor() as cur:
                    cur.execute("SET statement_timeout = %s", (self.timeout_ms,))
                    cur.execute(sql)
                    desc = cur.description
                    rows = [[_jsonable(v) for v in row] for row in cur.fetchmany(self.max_rows)]
                columns = _type_names(conn, desc)
        except pg_errors.QueryCanceled as exc:
            raise ExecutionError("timeout", str(exc).strip())
        except pg_errors.InsufficientPrivilege as exc:
            raise ExecutionError("permission", str(exc).strip())
        except pg_errors.SyntaxError as exc:
            raise ExecutionError("syntax", str(exc).strip())
        except pg_errors.Error as exc:
            raise ExecutionError("other", str(exc).strip())

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "duration_ms": int((time.monotonic() - start) * 1000),
        }


def _type_names(conn, desc) -> list[dict]:
    if not desc:
        return []
    oids = [d.type_code for d in desc]
    with conn.cursor() as tcur:
        tcur.execute("SELECT oid, typname FROM pg_type WHERE oid = ANY(%s)", (oids,))
        oid_to_name = dict(tcur.fetchall())
    return [{"name": d.name, "type": oid_to_name.get(d.type_code, str(d.type_code))} for d in desc]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return str(value)
    return value
