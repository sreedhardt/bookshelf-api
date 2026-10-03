# Bookshelf API

A small lending service for a community library: browse the catalog, check
books out, return them, and track late fees. FastAPI with in-memory storage.

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest
.venv/bin/python -m uvicorn app.main:app --reload   # http://127.0.0.1:8000/docs
```

## Lending rules

- Loans last 14 days.
- Returns after the due date cost 25 cents per day, capped at $20.
- A member can hold at most 3 books at once.
- A member with an overdue loan cannot borrow until it is returned.

## Layout

| Path | What it holds |
| --- | --- |
| `app/loans.py` | Checkout, return, overdue status, late fees |
| `app/catalog.py` | Search, pagination, availability |
| `app/store.py` | In-memory storage and seed data |
| `app/routes/` | HTTP endpoints |
