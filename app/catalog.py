from app.models import Book
from app.store import Store


def search_books(books: list[Book], query: str) -> list[Book]:
    """Books whose title or author contains the query (case-insensitive)."""
    query = query.casefold()
    return [
        b
        for b in books
        if query in b.title.casefold() or query in b.author.casefold()
    ]


def paginate(books: list[Book], limit: int, offset: int) -> list[Book]:
    return books[offset : offset + limit]


def available_copies(store: Store, book_id: int) -> int:
    return store.books[book_id].copies - len(store.active_loans(book_id=book_id))
