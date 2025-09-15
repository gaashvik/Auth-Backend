# FastAPI Device Session Backend

A **FastAPI** backend for managing user sessions across devices. Supports creating, revoking, and checking sessions, with JWT authentication and device limits.

## Features
- Limit active devices per user (`MAX_DEVICES = 1`).
- Track device ID, name, platform, IP, and last used time.
- Revoke sessions.
- Fetch basic user info.
- Health check endpoint `/health`.

## API Endpoints
- `GET /health` → Server status.
- `POST /api/sessions` → Create/update session.
- `POST /api/sessions/revoke` → Revoke session.
- `GET /api/me` → Get user info.
- `GET /api/check-session?device_id=DEVICE_ID` → Check session status.

## Setup & Deployment
1. Clone repo: `git clone <repo>`
2. Create venv and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Run locally: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
4. Deploy on Render with Python 3, build command `pip install -r requirements.txt`, start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.

## Notes
- Update `origins` for frontend domains.
- Backend expects JWT auth handled by `get_current_user`.
- Adjust `MAX_DEVICES` as needed.

## License
MIT

