from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession
from database import SessionLocal, Base, engine
from models import Session as SessionModel
from auth import get_current_user
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = [
    "http://localhost:3000",  # your Next.js dev server
    "http://127.0.0.1:3000",
    "https://auth-frontend-bice.vercel.app/"
    # add production domain(s) here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],       # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

MAX_DEVICES = 1

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Models
class SessionCreate(BaseModel):
    device_id: str
    device_name: str
    platform: str

class RevokeDevice(BaseModel):
    device_id: str

# Create session
@app.get("/health")
async def health():
    return{"status":"up"}
@app.post("/api/sessions")
async def create_session(data: SessionCreate, request: Request, user=Depends(get_current_user), db: DbSession = Depends(get_db)):
    user_id = user["sub"]
    sessions = db.query(SessionModel).filter(SessionModel.user_id == user_id).all()

    if data.device_id not in [s.device_id for s in sessions] and len(sessions) >= MAX_DEVICES:
        # Limit exceeded → send active devices
        devices = [
            {
                "device_id": s.device_id,
                "device_name": s.device_name,
                "platform": s.platform,
                "ip_address": s.ip_address,
                "last_used": s.last_used.isoformat()
            }
            for s in sessions
        ]
        return JSONResponse(
    content={"status": "limit_exceeded", "active_devices": devices},
    status_code=409
)

    # Add or update session
    now = datetime.datetime.now(datetime.timezone.utc)
    session = db.query(SessionModel).filter(SessionModel.user_id == user_id, SessionModel.device_id == data.device_id).first()
    if session:
        session.last_used = now
    else:
        session = SessionModel(
            user_id=user_id,
            device_id=data.device_id,
            device_name=data.device_name,
            platform=data.platform,
            ip_address=request.client.host,
            last_used=now
        )
        db.add(session)
    db.commit()
    return {"status": "ok"}

# Revoke session
@app.post("/api/sessions/revoke")
async def revoke_session(data: RevokeDevice, user=Depends(get_current_user), db: DbSession = Depends(get_db)):
    user_id = user["sub"]
    session = db.query(SessionModel).filter(SessionModel.user_id == user_id, SessionModel.device_id == data.device_id).first()
    if session:
        db.delete(session)
        db.commit()
    return {"status": "revoked"}

# Check user info
@app.get("/api/me")
async def get_me(user=Depends(get_current_user)):
    return {
        "full_name": user.get("name"),
        "phone": user.get("phone_number", "N/A")
    }
@app.get("/api/check-session")
async def check_session(request:Request,device_id: str=None, user=Depends(get_current_user), db: DbSession = Depends(get_db)):
    if request.method == "OPTIONS":
        return {}
    user_id = user["sub"]
    session = db.query(SessionModel).filter(SessionModel.user_id == user_id, SessionModel.device_id == device_id).first()
    print(session)
    if not session:
        raise HTTPException(status_code=401, detail="You have been logged out due to another device login")
    return {"status": "active", "last_used": session.last_used}
