from fastapi import APIRouter, Depends, HTTPException, Header
from supabase import Client
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database import get_db
from app.models import UserCreate, UserOut, Token, LoginRequest
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Auth"])


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Client = Depends(get_db)):
    try:
        # Check if username exists
        res = db.table("users").select("id").eq("username", user.username).execute()
        if res.data:
            raise HTTPException(status_code=400, detail="Username already taken")

        # Check if email exists
        if user.email:
            res_email = db.table("users").select("id").eq("email", user.email).execute()
            if res_email.data:
                raise HTTPException(status_code=400, detail="Email already registered")

        hashed = bcrypt.hash(user.password)
        insert_res = db.table("users").insert({
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "password_hash": hashed,
            "role": user.role
        }).execute()

        if not insert_res.data:
            raise HTTPException(status_code=500, detail="Failed to register user")

        u = insert_res.data[0]
        uid = u["id"]
        token = create_token({"sub": str(uid), "role": u["role"]})
        return Token(
            access_token=token,
            user=UserOut(
                id=uid, username=u["username"], full_name=u["full_name"],
                email=u["email"], phone=u["phone"], role=u["role"]
            )
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: Client = Depends(get_db)):
    try:
        # Allow logging in with username OR email
        res = db.table("users").select("*").eq("username", body.username).execute()
        user = None
        if res.data:
            user = res.data[0]
        else:
            # Try email
            res_email = db.table("users").select("*").eq("email", body.username).execute()
            if res_email.data:
                user = res_email.data[0]

        if not user or not bcrypt.verify(body.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username/email or password")

        token = create_token({"sub": str(user["id"]), "role": user["role"]})
        return Token(
            access_token=token,
            user=UserOut(
                id=user["id"], username=user["username"],
                full_name=user.get("full_name"), email=user.get("email"),
                phone=user.get("phone"), role=user["role"]
            )
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_current_user(authorization: str = Header(...), db: Client = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        res = db.table("users").select("id, username, full_name, role").eq("id", user_id).execute()
        if not res.data:
            raise HTTPException(status_code=401, detail="User not found")
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
