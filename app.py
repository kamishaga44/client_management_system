
import os
import re

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-key-change-before-deployment"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clients.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False,
    )



def validate_client_data(name, email, phone, current_client_id=None):
    name = name.strip()
    email = email.strip().lower()
    phone = phone.strip()

    if not name or len(name) > 100:
        return None, "Введите имя длиной от 1 до 100 символов."

    if not email or len(email) > 120:
        return None, "Введите электронную почту длиной до 120 символов."


    normalized_phone = re.sub(r"[\s()\-]", "", phone)

    if normalized_phone.startswith("+7"):
        digits = normalized_phone[2:]
    elif normalized_phone.startswith("8"):
        digits = normalized_phone[1:]
    else:
        return None, "Введите номер в формате +7 701 123 45 67 или 8 701 123 45 67."

    if not digits.isdigit() or len(digits) != 10:
        return None, "Номер должен содержать 10 цифр после +7 или 8."

    if digits[0] in "0" or digits[0] not in "67":
        return None, "Введите корректный мобильный номер Казахстана."


    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return None, "Введите корректный адрес электронной почты."

    domain = email.rsplit("@", 1)[1]
    if "." not in domain:
        return None, "После @ укажите домен с точкой, например gmail.com."

    domain_parts = domain.split(".")
    if any(not part for part in domain_parts) or len(domain_parts[-1]) < 2:
        return None, "Укажите корректное окончание домена, например .com или .kz."

    existing = Client.query.filter_by(email=email).first()
    if existing and existing.id != current_client_id:
        return None, "Клиент с такой электронной почтой уже существует."

    return {"name": name, "email": email, "phone": phone}, None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data, error = validate_client_data(
            request.form.get("name", ""),
            request.form.get("email", ""),
            request.form.get("phone", ""),
        )

        if error:
            flash(error, "error")
        else:
            try:
                db.session.add(Client(**data))
                db.session.commit()
                flash("Клиент успешно добавлен.", "success")
                return redirect(url_for("index"))
            except IntegrityError:
                db.session.rollback()
                flash("Не удалось сохранить клиента. Проверь данные.", "error")

    clients = Client.query.order_by(Client.created_at.desc()).all()
    return render_template("index.html", clients=clients)


@app.route("/edit/<int:client_id>", methods=["GET", "POST"])
def edit_client(client_id):
    client = db.session.get(Client, client_id)

    if client is None:
        flash("Клиент не найден.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        data, error = validate_client_data(
            request.form.get("name", ""),
            request.form.get("email", ""),
            request.form.get("phone", ""),
            current_client_id=client.id,
        )

        if error:
            flash(error, "error")
        else:
            client.name = data["name"]
            client.email = data["email"]
            client.phone = data["phone"]

            try:
                db.session.commit()
                flash("Данные клиента обновлены.", "success")
                return redirect(url_for("index"))
            except IntegrityError:
                db.session.rollback()
                flash("Не удалось обновить клиента. Проверь данные.", "error")

    return render_template("edit.html", client=client)


@app.route("/delete/<int:client_id>", methods=["POST"])
def delete_client(client_id):
    client = db.session.get(Client, client_id)

    if client is None:
        flash("Клиент не найден.", "error")
    else:
        db.session.delete(client)
        db.session.commit()
        flash("Клиент удалён.", "success")

    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=False)
