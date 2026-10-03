"""In-memory storage. Process-local; resets on restart."""

from app.models import Book, Loan, Member

SEED_BOOKS = [
    Book(id=1, title="Dune", author="Frank Herbert", year=1965, copies=2),
    Book(id=2, title="The Left Hand of Darkness", author="Ursula K. Le Guin", year=1969, copies=1),
    Book(id=3, title="Neuromancer", author="William Gibson", year=1984, copies=1),
    Book(id=4, title="Kindred", author="Octavia E. Butler", year=1979, copies=3),
    Book(id=5, title="The Dispossessed", author="Ursula K. Le Guin", year=1974, copies=1),
    Book(id=6, title="Snow Crash", author="Neal Stephenson", year=1992, copies=2),
]

SEED_MEMBERS = [
    Member(id=1, name="Ada Park", email="ada@example.com"),
    Member(id=2, name="Ravi Menon", email="ravi@example.com"),
    Member(id=3, name="Lena Ortiz", email="lena@example.com"),
]


class Store:
    def __init__(self) -> None:
        self.books: dict[int, Book] = {}
        self.members: dict[int, Member] = {}
        self.loans: dict[int, Loan] = {}
        self._next_loan_id = 1

    def seed(self) -> None:
        self.books = {b.id: b for b in SEED_BOOKS}
        self.members = {m.id: m for m in SEED_MEMBERS}
        self.loans = {}
        self._next_loan_id = 1

    def next_loan_id(self) -> int:
        loan_id = self._next_loan_id
        self._next_loan_id += 1
        return loan_id

    def active_loans(self, *, member_id: int | None = None, book_id: int | None = None) -> list[Loan]:
        return [
            loan
            for loan in self.loans.values()
            if loan.returned is None
            and (member_id is None or loan.member_id == member_id)
            and (book_id is None or loan.book_id == book_id)
        ]


store = Store()
