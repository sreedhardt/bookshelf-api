from datetime import timedelta

from app.config import DAILY_LATE_FEE_CENTS, LOAN_PERIOD_DAYS, MAX_ACTIVE_LOANS
from app.loans import is_overdue
from app.models import Loan
from tests.conftest import TODAY


def checkout(client, book_id=1, member_id=1):
    return client.post("/loans", json={"book_id": book_id, "member_id": member_id})


def test_checkout_sets_due_date(client):
    response = checkout(client)
    assert response.status_code == 201
    loan = response.json()
    assert loan["checked_out"] == TODAY.isoformat()
    assert loan["due"] == (TODAY + timedelta(days=LOAN_PERIOD_DAYS)).isoformat()
    assert loan["returned"] is None


def test_checkout_unknown_book_or_member(client):
    assert checkout(client, book_id=999).status_code == 404
    assert checkout(client, member_id=999).status_code == 404


def test_no_copies_available(client):
    assert checkout(client, book_id=3, member_id=1).status_code == 201
    response = checkout(client, book_id=3, member_id=2)
    assert response.status_code == 409
    assert response.json()["detail"] == "No copies available"


def test_active_loan_limit(client):
    for book_id in range(1, MAX_ACTIVE_LOANS + 1):
        assert checkout(client, book_id=book_id).status_code == 201
    response = checkout(client, book_id=MAX_ACTIVE_LOANS + 1)
    assert response.status_code == 409


def test_member_with_overdue_loan_cannot_borrow(client, today):
    checkout(client, book_id=1)
    today.value = TODAY + timedelta(days=LOAN_PERIOD_DAYS + 5)
    response = checkout(client, book_id=2)
    assert response.status_code == 409
    assert response.json()["detail"] == "Member has overdue loans"


def test_member_can_borrow_on_due_date(client, today):
    checkout(client, book_id=1)
    today.value = TODAY + timedelta(days=LOAN_PERIOD_DAYS)
    response = checkout(client, book_id=2)
    assert response.status_code == 201


def test_member_loans_not_flagged_overdue_on_due_date(client, today):
    checkout(client, book_id=1)
    today.value = TODAY + timedelta(days=LOAN_PERIOD_DAYS)
    loans = client.get("/members/1/loans").json()
    assert len(loans) == 1
    assert loans[0]["overdue"] is False


def test_return_on_time_has_no_fee(client, today):
    loan = checkout(client).json()
    today.value = TODAY + timedelta(days=3)
    returned = client.post(f"/loans/{loan['id']}/return").json()
    assert returned["returned"] == today.value.isoformat()
    assert returned["fee_cents"] == 0


def test_late_return_charges_fee(client, today):
    loan = checkout(client).json()
    today.value = TODAY + timedelta(days=LOAN_PERIOD_DAYS + 4)
    returned = client.post(f"/loans/{loan['id']}/return").json()
    assert returned["fee_cents"] == 4 * DAILY_LATE_FEE_CENTS


def test_cannot_return_twice(client):
    loan = checkout(client).json()
    client.post(f"/loans/{loan['id']}/return")
    assert client.post(f"/loans/{loan['id']}/return").status_code == 409


def test_member_loans_flag_overdue(client, today):
    checkout(client, book_id=1)
    today.value = TODAY + timedelta(days=LOAN_PERIOD_DAYS + 1)
    loans = client.get("/members/1/loans").json()
    assert len(loans) == 1
    assert loans[0]["overdue"] is True


def test_returned_loan_not_flagged_overdue_even_if_past_due(client, today):
    loan = checkout(client, book_id=1).json()
    today.value = TODAY + timedelta(days=LOAN_PERIOD_DAYS + 1)
    client.post(f"/loans/{loan['id']}/return")
    loans = client.get("/members/1/loans").json()
    assert len(loans) == 1
    assert loans[0]["overdue"] is False


def _make_loan(due):
    return Loan(id=1, book_id=1, member_id=1, checked_out=due - timedelta(days=LOAN_PERIOD_DAYS), due=due)


def test_is_overdue_false_before_due_date():
    due = TODAY
    loan = _make_loan(due)
    assert is_overdue(loan, due - timedelta(days=1)) is False


def test_is_overdue_false_on_due_date():
    due = TODAY
    loan = _make_loan(due)
    assert is_overdue(loan, due) is False


def test_is_overdue_true_day_after_due_date():
    due = TODAY
    loan = _make_loan(due)
    assert is_overdue(loan, due + timedelta(days=1)) is True


def test_is_overdue_false_when_returned_regardless_of_date():
    due = TODAY
    loan = _make_loan(due).copy(update={"returned": due + timedelta(days=10)})
    assert is_overdue(loan, due + timedelta(days=20)) is False
