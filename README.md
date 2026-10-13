# Client Management System

A web application for managing client information, built with Python and Flask.

## Features

- Add new clients with name, email, and phone number
- View the complete client list
- Edit existing client information
- Delete clients with confirmation
- Search clients by name
- Validate user input
- Prevent duplicate email addresses
- Store client records in an SQLite database
- Protect forms against CSRF attacks
- Display success and error messages

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-WTF
- Email Validator
- HTML, CSS, JavaScript
- Pytest

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/kamishaga44/client_management_system.git
   cd client_management_system
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set a secret key using the `SECRET_KEY` environment variable.

5. Run the application:

   ```bash
   python app.py
   ```

6. Open the local address shown in the terminal in your browser.

## Running Tests

Run the automated test suite with:

```bash
pytest -v
```

The tests cover client creation, input validation, duplicate emails, searching, editing, deleting, and handling missing clients.

## Project Structure

```text
client_management_system/
├── app.py
├── test_app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   └── edit.html
└── static/
    └── style.css
```

## Security and Validation

- CSRF protection for forms
- Email format validation
- Mobile phone format validation for supported Kazakhstan number formats
- Duplicate email prevention
- Server-side validation of client data
- SQLite database for persistent storage

## Purpose

This project was developed to practice backend development, database integration, CRUD operations, form validation, and automated testing with Python and Flask.
