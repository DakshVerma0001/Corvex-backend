from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# ✅ USE PBKDF2 (NO BCRYPT)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# In-memory DB
fake_users_db = {}


# -----------------------------
# MODELS
# -----------------------------
class SignupRequest(BaseModel):
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------
# PASSWORD HANDLING
# -----------------------------
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


# -----------------------------
# TOKEN
# -----------------------------
def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------------
# ROUTES
# -----------------------------
@router.post("/signup")
def signup(data: SignupRequest):
    if data.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    fake_users_db[data.username] = {
        "password": hash_password(data.password)
    }

    return {"message": "User created successfully"}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = fake_users_db.get(data.username)

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(data.username)

    return {"access_token": token}