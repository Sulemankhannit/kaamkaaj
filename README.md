# KaamKaaj ⚔️

**KaamKaaj** is a gamified task management API where productivity meets RPG mechanics. Built with FastAPI and PostgreSQL, it transforms your daily goals (`Lakshya`) and tasks (`Kaam`) into quests where users (`Khiladis`) can earn XP, level up, and even have their proof of work (`Saboot`) verified by an AI Reviewer.

##  Features

- **Gamified Productivity**: Complete tasks to earn XP and level up your Khiladi.
- **Goals & Quests System**: Organize tasks under overarching goals (Lakshyas).
- **AI Verification**: Tasks requiring verification are automatically reviewed by an AI based on text or image proofs (Saboot).
- **Secure Authentication**: JWT-based authentication, bcrypt password hashing, and email OTP verification.
- **Rate Limiting**: Built-in rate limiting using `slowapi` to prevent abuse.
- **Cloud Storage Integration**: Direct upload of image proofs to Cloudinary.

##  Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) & SQLAlchemy
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Cloud Storage**: [Cloudinary](https://cloudinary.com/) (for image uploads)
- **Security**: JWT, Passlib (bcrypt)
- **Rate Limiting**: SlowAPI

##  Project Structure

```text
kaamkaaj/
├── core/                  # Core configurations, security, and rate limiting
├── routes/                # API Endpoints (Auth, Khiladi, Lakshya, Kaam, Dashboard)
├── schemas/               # Pydantic/SQLModel models for data validation
├── utils/                 # Utility functions (AI Reviewer, Email sending)
├── alembic/               # Database migrations
├── main.py                # FastAPI application entry point
└── requirements.txt       # Project dependencies
```

##  Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL server running
- Cloudinary Account
- SMTP Email Account (for OTPs)

### 1. Clone the repository

```bash
git clone <repository-url>
cd kaamkaaj_copy
```

### 2. Set up the virtual environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory and add the following keys:

```ini
# Security
KAAMKAJ_SECRET_KEY=your_super_secret_jwt_key

# Database
DB_USER=postgres
DB_PASSWORD=your_db_password
HOST=localhost
PORT=5432
DB_NAME=kaamkaaj

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Email / SMTP
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`
Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`

## API Overview

- **`/khiladi`**: Player registration, OTP email verification, and profile management.
- **`/login`**: OAuth2 login to receive JWT access tokens.
- **`/dashboard`**: Unified overview of the Khiladi's progress, XP, and active Lakshyas.
- **`/lakshya`**: CRUD operations for top-level goals.
- **`/kaam`**: Quests creation, filtering, and submissions. Supports uploading proof (image/text) which triggers background AI review if verification is required.

---
*Welcome to the tavern, Adventurer. Your journey begins here!*
