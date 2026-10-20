from datetime import date, datetime, timedelta
from decimal import Decimal

from app.executor import _jsonable


def test_jsonable_converts_decimal_to_float():
    assert _jsonable(Decimal("123.45")) == 123.45
    assert isinstance(_jsonable(Decimal("0")), float)


def test_jsonable_converts_dates_to_iso():
    assert _jsonable(date(2026, 10, 20)) == "2026-10-20"
    assert _jsonable(datetime(2026, 10, 20, 12, 0, 0)).startswith("2026-10-20T12:00:00")


def test_jsonable_converts_timedelta():
    assert isinstance(_jsonable(timedelta(days=1)), str)


def test_jsonable_passes_scalars_through():
    assert _jsonable(42) == 42
    assert _jsonable("hello") == "hello"
    assert _jsonable(None) is None
