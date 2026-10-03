from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.catalog import available_copies, paginate, search_books
from app.deps import get_store
from app.models import BookPage
from app.store import Store

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=BookPage)
def list_books(
    q: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    store: Store = Depends(get_store),
):
    books = sorted(store.books.values(), key=lambda b: b.id)
    if q:
        books = search_books(books, q)
    return BookPage(total=len(books), items=paginate(books, limit, offset))


@router.get("/{book_id}")
def get_book(book_id: int, store: Store = Depends(get_store)):
    book = store.books.get(book_id)
    if book is None:
        raise HTTPException(404, f"Book {book_id} not found")
    return {**book.dict(), "available": available_copies(store, book_id)}
