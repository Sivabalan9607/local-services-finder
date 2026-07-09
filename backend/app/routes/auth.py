from fastapi import APIRouter, Depends, HTTPException, Header
from mysql.connector import MySQLConnection
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.database import get_db
from app.models import UserCreate, UserOut, Token, LoginRequest
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["Auth"])


def _clean(cursor):
    try:
        while cursor.nextset():
            pass
    except Exception:
        pass
    cursor.close()


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=Token)
def register(user: UserCreate, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already taken")
        cursor.fetchall()

        hashed = bcrypt.hash(user.password)
        cursor.execute(
            "INSERT INTO users (username, full_name, email, phone, password_hash, role) VALUES (%s,%s,%s,%s,%s,%s)",
            (user.username, user.full_name, user.email, user.phone, hashed, user.role),
        )
        uid = cursor.lastrowid
        token = create_token({"sub": str(uid), "role": user.role})
        return Token(
            access_token=token,
            user=UserOut(id=uid, username=user.username, full_name=user.full_name, email=user.email, phone=user.phone, role=user.role),
        )
    finally:
        _clean(cursor)


@router.post("/login", response_model=Token)
def login(body: LoginRequest, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (body.username,))
        user = cursor.fetchone()
        cursor.fetchall()
        if not user or not bcrypt.verify(body.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = create_token({"sub": str(user["id"]), "role": user["role"]})
        return Token(
            access_token=token,
            user=UserOut(
                id=user["id"], username=user["username"],
                full_name=user.get("full_name"), email=user.get("email"),
                phone=user.get("phone"), role=user["role"],
            ),
        )
    finally:
        _clean(cursor)


def get_current_user(authorization: str = Header(...), db: MySQLConnection = Depends(get_db)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, full_name, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.fetchall()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        _clean(cursor)
