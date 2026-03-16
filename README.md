# Expenses Manager API

![CI](https://github.com/piotrgolebiewski07/expenses_manager/actions/workflows/ci.yml/badge.svg)

Backend API for managing personal expenses built with **FastAPI**.

The application allows users to register, log in, and manage their expenses.  
This project demonstrates a typical backend architecture with authentication,
database migrations, seed data and Docker support.

---

## Architecture

```
Client
   ↓
FastAPI (REST API)
   ↓
SQLAlchemy (ORM)
   ↓
SQLite Database
```

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- SQLite
- Docker

---

## Features

- User registration and login
- JWT authentication
- Expense management
- Database migrations
- Seed data for testing
- Docker support

---

## Continuous Integration

This project uses **GitHub Actions** for Continuous Integration.

The CI pipeline automatically:

- installs Python dependencies
- builds the Docker image
- starts the container
- verifies that the API responds

The workflow runs on every push and pull request to the `main` branch.

---

## Requirements

- Docker installed

---

## Run with Docker

Build the image:

```bash
docker build -t expenses-manager .
```

Run the container:

```bash
docker run -p 8000:8000 expenses-manager
```

The container will automatically:

- create database tables
- seed the database with test data
- start the API server

---

## API Documentation

After starting the container open:

```
http://localhost:8000/api/v1/docs
```

---

## Test User

Seed script creates a test user:

```
email: seed@example.com
password: seedpassword
```

---

## Example API Request

Example login request:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
-H "Content-Type: application/json" \
-d '{
"email": "seed@example.com",
"password": "seedpassword"
}'
```

Example response:

```json
{
  "access_token": "your_jwt_token",
  "token_type": "bearer"
}
```

---

## Project Structure

```
expenses_manager
│
├── app
│   ├── api
│   ├── models
│   ├── users
│   └── main.py
│
├── alembic
├── scripts
├── Dockerfile
├── start.sh
└── requirements.txt
```

---

## Author

Piotr Gołębiewski

---

## License

This project is licensed under the MIT License.