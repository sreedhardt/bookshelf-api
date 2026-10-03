def test_list_books(client):
    body = client.get("/books").json()
    assert body["total"] == 6
    assert [b["id"] for b in body["items"]] == [1, 2, 3, 4, 5, 6]


def test_pagination(client):
    body = client.get("/books", params={"limit": 2, "offset": 2}).json()
    assert body["total"] == 6
    assert [b["id"] for b in body["items"]] == [3, 4]


def test_search_by_title(client):
    body = client.get("/books", params={"q": "Dune"}).json()
    assert [b["title"] for b in body["items"]] == ["Dune"]


def test_search_by_author(client):
    body = client.get("/books", params={"q": "Le Guin"}).json()
    assert body["total"] == 2


def test_get_book_reports_availability(client):
    client.post("/loans", json={"book_id": 1, "member_id": 1})
    body = client.get("/books/1").json()
    assert body["copies"] == 2
    assert body["available"] == 1


def test_unknown_book_is_404(client):
    assert client.get("/books/999").status_code == 404


def test_limit_is_validated(client):
    assert client.get("/books", params={"limit": 0}).status_code == 422
