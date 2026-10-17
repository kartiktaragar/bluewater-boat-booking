# Boat Booking API

FastAPI backend with SQLite persistence and JWT authentication. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## Windows PowerShell setup

Run these commands from the existing `BACK` folder. This uses the existing `.venv`; it does not create a new project or virtual environment.

```powershell
Set-Location "C:\Users\klebc\Desktop\PROJECT\BACK"
Copy-Item .env.example .env
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Edit `.env` and replace `SECRET_KEY` with a random value generated using:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Then start the API:

```powershell
uvicorn app.main:app --reload
```

SQLite creates `boat_booking.db` in the `BACK` folder when the application starts. The home page (`/`), health check (`/health`), and existing sample boat listing (`/api/boats`) remain available.

## Authentication API

- `POST /api/auth/register` accepts `email`, `full_name`, and `password`; email addresses are normalized, passwords must be 8–128 characters, and duplicate emails are rejected.
- `POST /api/auth/login` validates credentials and returns a bearer access token.
- `GET /api/auth/me` requires `Authorization: Bearer <access_token>`.
- `POST /api/auth/signup` remains as a backwards-compatible alias for register.

User responses contain public profile fields only. Passwords are stored as Argon2 hashes and access-token expiry is configured with `ACCESS_TOKEN_EXPIRE_MINUTES`. Never commit `.env` or use the example JWT secret in a deployed application.

## AI assistant

Set `GEMINI_API_KEY` in `.env` to enable the Gemini-powered chat endpoint. The model defaults to `gemini-3.8-flash` and can be overridden with `GEMINI_MODEL`.

- `POST /api/assistant/chat` accepts `{"message": "..."}` and returns `{"reply": "..."}`.
- Requests must contain 1–4000 characters. The endpoint returns `503` if Gemini is not configured and `502` if the upstream request fails.

## Test

Install the project test dependencies as part of `requirements.txt`, then run:

```powershell
python -m pytest -q
```
