
import pytest

from app import app, db, Client


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        test_client = app.test_client()
        yield test_client

        db.session.remove()
        db.drop_all()


def add_client(client, name="Камила", email="kamila@example.com",
               phone="+77011234567"):
    return client.post(
        "/",
        data={
            "name": name,
            "email": email,
            "phone": phone,
        },
        follow_redirects=True,
    )


def test_home_page_opens(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Список клиентов".encode() in response.data


def test_add_client(client):
    response = add_client(client)
    assert response.status_code == 200
    assert "Клиент успешно добавлен.".encode() in response.data

    saved = db.session.execute(db.select(Client)).scalars().all()
    assert len(saved) == 1
    assert saved[0].name == "Камила"


def test_reject_duplicate_email(client):
    add_client(client)
    response = add_client(client, name="Другой клиент")

    assert "уже существует".encode() in response.data
    assert len(db.session.execute(db.select(Client)).scalars().all()) == 1


@pytest.mark.parametrize("email", [
    "kamila",
    "kamila@gmail",
    "kamila@@gmail.com",
])
def test_reject_invalid_email(client, email):
    response = add_client(client, email=email)
    assert "электрон".encode() in response.data.lower()
    assert len(db.session.execute(db.select(Client)).scalars().all()) == 0


@pytest.mark.parametrize("phone", [
    "1",
    "07011234567",
    "123",
])
def test_reject_invalid_phone(client, phone):
    response = add_client(client, phone=phone)
    assert "номер".encode() in response.data.lower()
    assert len(db.session.execute(db.select(Client)).scalars().all()) == 0


def test_search_clients_by_name(client):
    add_client(client, name="Камила")
    add_client(client, name="Мила", email="mila@example.com")

    response = client.get("/")
    assert "Камила".encode() in response.data
    assert "Мила".encode() in response.data


def test_edit_client(client):
    add_client(client)

    saved = db.session.execute(db.select(Client)).scalars().first()
    response = client.post(
        f"/edit/{saved.id}",
        data={
            "name": "Камила Новая",
            "email": "new@example.com",
            "phone": "+77011234567",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Данные клиента обновлены.".encode() in response.data

    updated = db.session.get(Client, saved.id)
    assert updated.name == "Камила Новая"
    assert updated.email == "new@example.com"


def test_delete_client(client):
    add_client(client)

    saved = db.session.execute(db.select(Client)).scalars().first()
    response = client.post(
        f"/delete/{saved.id}",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Клиент удалён.".encode() in response.data
    assert db.session.get(Client, saved.id) is None


def test_edit_unknown_client(client):
    response = client.get("/edit/99999", follow_redirects=True)
    assert response.status_code == 200
    assert "Клиент не найден.".encode() in response.data
