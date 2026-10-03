from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from app import loans
from app.deps import get_store, get_today
from app.models import CheckoutRequest, Loan
from app.store import Store

router = APIRouter(tags=["loans"])


@router.post("/loans", response_model=Loan, status_code=201)
def create_loan(body: CheckoutRequest, store: Store = Depends(get_store), today: date = Depends(get_today)):
    try:
        return loans.checkout(store, body.book_id, body.member_id, today)
    except loans.LoanError as e:
        raise HTTPException(e.status_code, e.detail)


@router.post("/loans/{loan_id}/return", response_model=Loan)
def return_loan(loan_id: int, store: Store = Depends(get_store), today: date = Depends(get_today)):
    try:
        return loans.return_loan(store, loan_id, today)
    except loans.LoanError as e:
        raise HTTPException(e.status_code, e.detail)


@router.get("/loans/{loan_id}", response_model=Loan)
def get_loan(loan_id: int, store: Store = Depends(get_store)):
    loan = store.loans.get(loan_id)
    if loan is None:
        raise HTTPException(404, f"Loan {loan_id} not found")
    return loan


@router.get("/members/{member_id}/loans")
def member_loans(member_id: int, store: Store = Depends(get_store), today: date = Depends(get_today)):
    if member_id not in store.members:
        raise HTTPException(404, f"Member {member_id} not found")
    return [
        {**loan.dict(), "overdue": loans.is_overdue(loan, today)}
        for loan in store.loans.values()
        if loan.member_id == member_id
    ]
