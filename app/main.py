from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import books, loans
from app.store import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.seed()
    yield


app = FastAPI(title="Bookshelf API", version="0.1.0", lifespan=lifespan)
app.include_router(books.router)
app.include_router(loans.router)


@app.get("/health")
def health():
    return {"status": "ok"}
