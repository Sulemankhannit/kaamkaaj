# KaamKaaj | The AI Accountability Engine

**KaamKaaj** isn't just another gamified task manager—it's an **unforgiving Accountability Engine**. 

Built with FastAPI and PostgreSQL, KaamKaaj introduces RPG mechanics where you only get rewarded if you actually put in the work. You can set your goals (`Lakshya`) and list your tasks (`Kaam`), but you don't earn XP just by checking a box. If a task requires proof, you must submit a **Saboot** (image or text evidence), which is strictly judged and verified by our **AI Reviewer**. No cutting corners, no cheating the system.

##  The Core Hook: AI Accountability

- **No Saboot, No XP**: You only get points for the tasks you promised to prove. A simple checklist won't cut it.
- **Strict AI Judging**: Your submitted proof (whether it's an uploaded image or a text description) is sent to an AI background worker. The AI rigorously evaluates your Saboot against your task description to determine if the task was genuinely completed.
- **Earn Your Level**: If the AI accepts your proof, your Kaam is marked complete and you earn your XP. If it rejects it, you get nothing. 

##  Gamified Productivity

- **Khiladi Profile**: Start as a level 1 adventurer and grind your way to the top by earning XP from verified tasks.
- **Lakshya & Kaam**: Group your daily grinds (`Kaam`) under epic overarching goals (`Lakshya`).
- **Secure Authentication**: JWT-based authentication, bcrypt password hashing, and mandatory OTP email verification to keep your Khiladi account secure.

##  Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Fast, asynchronous Python API)
- **Database ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) & SQLAlchemy
- **Database**: PostgreSQL (Migrations handled by Alembic)
- **Cloud Storage**: [Cloudinary](https://cloudinary.com/) (For storing your Saboot images)
- **Security & Rate Limiting**: Passlib (bcrypt), JWT, and SlowAPI
- **AI Worker**: Background task execution for the AI Reviewer

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

## Getting Started

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
- **`/kaam`**: Quests creation, filtering, and submissions. **The AI Engine lives here.** Upload your `Saboot` to trigger a background AI review. The task only resolves if the AI accepts your proof.

---
*Welcome to the tavern, Adventurer. Your journey begins here, but remember: the AI is watching.*
