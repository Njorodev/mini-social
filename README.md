
#  Mini-Social API

A lightweight, high-performance social media backend built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. This project features a modular architecture, secure JWT authentication, and a personalized user feed logic.

##  Features

* ** Secure Auth**: JWT-based authentication with access and refresh tokens.
* ** Posts & Media**: Full CRUD for posts including support for `multipart/form-data` and image uploads.
* ** Engagement**: Interactive liking and commenting system.
* ** Social Graph**: Follow/unfollow system to build user networks.
* ** Personalized Feed**: A dynamic feed that aggregates posts from followed users + the user's own content, respecting visibility rules (`public`, `followers`, `private`).
* ** Robust Testing**: 100% endpoint coverage with `pytest` and modular fixtures in `conftest.py`.

---

##  Project Architecture

The project follows a modular structure for scalability:

```text
├── app/
│   ├── core/      # Security, JWT, and Global Config
│   ├── db/        # SQLAlchemy Models & Session management
│   ├── routers/   # API Endpoints (Auth, Posts, Feed, etc.)
│   ├── schemas/   # Pydantic Data Validation
│   ├── utils/     # Helper functions
│   └── main.py    # Application Entry Point
├── alembic/       # Database Migration Scripts
├── tests/         # Pytest test suite
└── venv/          # Virtual Environment

```

---

##  Tech Stack

* **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
* **Database**: [PostgreSQL](https://www.postgresql.org/) / [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
* **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
* **Validation**: [Pydantic v2](https://www.google.com/search?q=https://docs.pydantic.dev/)
* **Testing**: [Pytest](https://docs.pytest.org/) & [HTTPX](https://www.python-httpx.org/)

---

##  Getting Started

### 1. Prerequisites

* Python 3.10+
* PostgreSQL (or Supabase/Neon URI)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Njorodev/mini-social.git
cd mini-social

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

### 3. Environment Setup

Create a `.env` file in the root directory and add your credentials:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mini_social
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

```

### 4. Database Migrations

```bash
alembic upgrade head

```

### 5. Run the Application

```bash
uvicorn app.main:app --reload

```

The API will be available at `http://127.0.0.1:8000`.

View the interactive docs at `http://127.0.0.1:8000/docs`.

---

##  Testing

The project uses a comprehensive test suite covering all modules.

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

```

---

##  API Endpoints Summary

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Create a new user account |
| `POST` | `/auth/login` | Get JWT access & refresh tokens |
| `GET` | `/feed/` | Get personalized social feed |
| `POST` | `/posts/` | Create a new post (supports images) |
| `POST` | `/like/{post_id}` | Like/Unlike a post |
| `POST` | `/posts/{id}/comment` | Add a comment to a post |

---

##  Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

##  License

Distributed under the MIT License. See `LICENSE` for more information.

**Njoroge Dev** - [@Njorodev](https://github.com/Njorodev)

