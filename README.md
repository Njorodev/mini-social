
#  Mini-Social API

A lightweight, robust social media backend built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL/SQLite**. This project features a complete suite of social interactions including real-time feeds, secure authentication, and image upload support.

##  Features

* **Secure Authentication**: JWT-based auth with Access & Refresh tokens and password hashing via `bcrypt`.
* **Post Management**: Create, update (PATCH), and delete posts with support for `multipart/form-data` and image uploads.
* **Social Interactions**:
* **Following System**: Follow/unfollow users to build a network.
* **Likes**: Idempotent liking system for posts.
* **Comments**: Full CRUD for post discussions.


* **Personalized Feed**: A smart feed that aggregates posts from users you follow + your own content, respecting visibility rules (`public`, `followers`, `private`).
* **Admin Controls**: Role-based access control for administrative tasks.
* **Fully Tested**: 23+ automated tests covering every major endpoint.

---

##  Tech Stack

| Category | Technology |
| --- | --- |
| **Framework** | FastAPI |
| **Web Server** | Uvicorn |
| **Database** | SQLAlchemy (PostgreSQL / SQLite) |
| **Migrations** | Alembic |
| **Auth** | JWT (PyJWT), Passlib (Bcrypt) |
| **Testing** | Pytest, HTTPX |

---

##  Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/mini-social.git
cd mini-social

```


2. **Set up a Virtual Environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. **Install Dependencies**:
```bash
pip install -r requirements.txt

```


4. **Environment Variables**:
Create a `.env` file in the root directory:
```env
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

```



---

##  Getting Started

1. **Run Migrations**:
```bash
alembic upgrade head

```


2. **Start the Server**:
```bash
uvicorn app.main:app --reload

```


3. **Explore the API**:
Open your browser to `http://127.0.0.1:8000/docs` to view the interactive **Swagger UI**.

---

##  Running Tests

Ensure your application is robust by running the full test suite:

```bash
pytest

```

To see detailed logs or debug print statements:

```bash
pytest -s -v

```

---

##  Project Structure

```text
mini-social/
├── app/
│   ├── core/           # Security, Config, JWT logic
│   ├── db/             # Models, Session, Migrations
│   ├── routers/        # API Endpoints (Auth, Posts, Feed, etc.)
│   ├── schemas/        # Pydantic Models
│   ├── tests/          # Pytest Suite
│   └── main.py         # App Entry Point
├── uploads/            # Stored images (gitignored)
├── requirements.txt    # Dependencies
└── alembic.ini         # Migration Config

```

---

##  API Endpoints (Quick Reference)

### Authentication

* `POST /auth/register` - Create a new account.
* `POST /auth/login` - Get access & refresh tokens.
* `POST /auth/refresh` - Renew access token.

### Feed & Social

* `GET /feed/` - Personalized user feed.
* `POST /like/{post_id}/like` - Like/Unlike a post.
* `POST /posts/{post_id}/comments` - Add a comment.

