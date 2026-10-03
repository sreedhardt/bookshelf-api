from datetime import date

from app.store import Store, store


def get_store() -> Store:
    return store


def get_today() -> date:
    return date.today()
