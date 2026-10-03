from datetime import date

from app.config import DAILY_LATE_FEE_CENTS, MAX_LATE_FEE_CENTS
from app.loans import late_fee_cents

DUE = date(2026, 3, 16)


def test_no_fee_when_returned_early():
    assert late_fee_cents(DUE, date(2026, 3, 10)) == 0


def test_no_fee_when_returned_on_due_date():
    assert late_fee_cents(DUE, DUE) == 0


def test_fee_per_day_late():
    assert late_fee_cents(DUE, date(2026, 3, 19)) == 3 * DAILY_LATE_FEE_CENTS


def test_fee_is_capped():
    assert late_fee_cents(DUE, date(2027, 3, 16)) == MAX_LATE_FEE_CENTS
