import pytest

from app.config import ALLOWED_SCHEMA
from app.sql_validator import SqlValidator, ValidationError

validator = SqlValidator(ALLOWED_SCHEMA)


def test_accepts_simple_select():
    validator.validate("SELECT ordered_at, paid_amount FROM orders WHERE status = 'paid'")


def test_accepts_join_and_aggregation():
    sql = (
        "SELECT c.province, SUM(o.paid_amount) AS sales "
        "FROM orders o JOIN customers c ON c.id = o.customer_id "
        "WHERE o.status = 'paid' GROUP BY c.province ORDER BY 2 DESC LIMIT 10"
    )
    validator.validate(sql)


def test_accepts_time_trend():
    sql = (
        "SELECT ordered_at::date AS day, SUM(paid_amount) AS sales FROM orders "
        "WHERE status = 'paid' AND ordered_at >= now() - interval '30 days' "
        "GROUP BY 1 ORDER BY 1"
    )
    validator.validate(sql)


def test_rejects_drop_table():
    with pytest.raises(ValidationError):
        validator.validate("DROP TABLE orders")


def test_rejects_update():
    with pytest.raises(ValidationError):
        validator.validate("UPDATE orders SET status = 'x'")


def test_rejects_delete():
    with pytest.raises(ValidationError):
        validator.validate("DELETE FROM orders WHERE id = 1")


def test_rejects_multi_statement():
    with pytest.raises(ValidationError):
        validator.validate("SELECT 1; DROP TABLE orders")


def test_rejects_unknown_table():
    with pytest.raises(ValidationError):
        validator.validate("SELECT * FROM secrets")


def test_rejects_unknown_column():
    with pytest.raises(ValidationError):
        validator.validate("SELECT secret_col FROM orders")


def test_rejects_subquery_with_unknown_table():
    with pytest.raises(ValidationError):
        validator.validate("SELECT * FROM orders WHERE id IN (SELECT id FROM secrets)")


def test_rejects_dangerous_function():
    with pytest.raises(ValidationError):
        validator.validate("SELECT pg_sleep(10)")


def test_rejects_insert():
    with pytest.raises(ValidationError):
        validator.validate("INSERT INTO orders (id) VALUES (1)")
