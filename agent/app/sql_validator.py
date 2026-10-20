"""SQL 安全校验（SQLGlot AST 层防线之一，不替代数据库只读权限）。

规则（PRD §9 / F04）：
- 仅允许单条语句；
- 仅允许 SELECT（含 UNION / CTE），拒绝 DDL/DML/DCL；
- 表名必须在白名单内（FROM/JOIN/子查询都会遍历）；
- 列名必须在白名单并集内（演示库列名基本唯一，暂不解析别名）；
- 拒绝高危函数（pg_sleep / pg_read_file / dblink 等）。
"""

from typing import Mapping, Set

import sqlglot
from sqlglot import exp

DANGEROUS_FUNCTIONS = {
    "pg_sleep", "pg_read_file", "pg_read_binary_file", "pg_ls_dir", "pg_stat_file",
    "lo_import", "lo_export", "dblink", "dblink_exec", "dblink_connect",
    "current_setting", "set_config", "pg_terminate_backend", "pg_cancel_backend",
}


class ValidationError(Exception):
    """SQL 校验失败。"""


class SqlValidator:
    def __init__(self, allowed_tables: Mapping[str, Set[str]]):
        self.allowed_tables = allowed_tables
        self.all_columns = {c for cols in allowed_tables.values() for c in cols}

    def validate(self, sql: str) -> None:
        statements = sqlglot.parse(sql, read="postgres")
        if not statements:
            raise ValidationError("空 SQL")
        if len(statements) > 1:
            raise ValidationError("禁止多语句")
        statement = statements[0]

        if not self._is_select(statement):
            raise ValidationError("只允许 SELECT 查询")

        self._check_tables(statement)
        self._check_columns(statement)
        self._check_functions(statement)

    @staticmethod
    def _is_select(statement: exp.Expression) -> bool:
        return isinstance(statement, (exp.Select, exp.Union))

    def _check_tables(self, statement: exp.Expression) -> None:
        for table in statement.find_all(exp.Table):
            if table.name not in self.allowed_tables:
                raise ValidationError(f"未授权的表: {table.name}")

    def _check_columns(self, statement: exp.Expression) -> None:
        for column in statement.find_all(exp.Column):
            if column.name not in self.all_columns:
                raise ValidationError(f"未授权的字段: {column.name}")

    def _check_functions(self, statement: exp.Expression) -> None:
        for func in statement.find_all(exp.Func):
            name = (func.name or "").lower()
            if name in DANGEROUS_FUNCTIONS:
                raise ValidationError(f"禁止的函数: {name}")
