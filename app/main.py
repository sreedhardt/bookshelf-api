from fastapi import FastAPI

from app.routes import books, loans
from app.store import store

app = FastAPI(title="Bookshelf API", version="0.1.0")
app.include_router(books.router)
app.include_router(loans.router)


@app.on_event("startup")
def seed_store() -> None:
    store.seed()


@app.get("/health")
def health():
    return {"status": "ok"}
