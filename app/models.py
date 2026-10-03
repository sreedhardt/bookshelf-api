from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    copies: int = Field(ge=0)

    class Config:
        schema_extra = {
            "example": {"id": 1, "title": "Dune", "author": "Frank Herbert", "year": 1965, "copies": 2}
        }


class Member(BaseModel):
    id: int
    name: str
    email: str


class Loan(BaseModel):
    id: int
    book_id: int
    member_id: int
    checked_out: date
    due: date
    returned: Optional[date] = None
    fee_cents: int = 0


class CheckoutRequest(BaseModel):
    book_id: int
    member_id: int


class BookPage(BaseModel):
    total: int
    items: list[Book]
