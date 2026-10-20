"""Lending rules: checkout, return, overdue status and late fees."""

from datetime import date, timedelta

from app.catalog import available_copies
from app.config import DAILY_LATE_FEE_CENTS, LOAN_PERIOD_DAYS, MAX_ACTIVE_LOANS, MAX_LATE_FEE_CENTS
from app.models import Loan
from app.store import Store


class LoanError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def is_overdue(loan: Loan, today: date) -> bool:
    return loan.returned is None and today >= loan.due


def late_fee_cents(due: date, returned: date) -> int:
    days_late = (returned - due).days
    if days_late <= 0:
        return 0
    return min(days_late * DAILY_LATE_FEE_CENTS, MAX_LATE_FEE_CENTS)


def checkout(store: Store, book_id: int, member_id: int, today: date) -> Loan:
    if book_id not in store.books:
        raise LoanError(404, f"Book {book_id} not found")
    if member_id not in store.members:
        raise LoanError(404, f"Member {member_id} not found")

    active = store.active_loans(member_id=member_id)
    if any(is_overdue(loan, today) for loan in active):
        raise LoanError(409, "Member has overdue loans")
    if len(active) >= MAX_ACTIVE_LOANS:
        raise LoanError(409, f"Member already has {MAX_ACTIVE_LOANS} active loans")
    if available_copies(store, book_id) <= 0:
        raise LoanError(409, "No copies available")

    loan = Loan(
        id=store.next_loan_id(),
        book_id=book_id,
        member_id=member_id,
        checked_out=today,
        due=today + timedelta(days=LOAN_PERIOD_DAYS),
    )
    store.loans[loan.id] = loan
    return loan


def return_loan(store: Store, loan_id: int, today: date) -> Loan:
    loan = store.loans.get(loan_id)
    if loan is None:
        raise LoanError(404, f"Loan {loan_id} not found")
    if loan.returned is not None:
        raise LoanError(409, "Loan already returned")

    returned = loan.model_copy(update={"returned": today, "fee_cents": late_fee_cents(loan.due, today)})
    store.loans[loan_id] = returned
    return returned
