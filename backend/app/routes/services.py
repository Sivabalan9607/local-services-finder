import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from mysql.connector import MySQLConnection
from app.database import get_db, UPLOAD_DIR
from app.models import ServiceCreate, ServiceOut, BookingCreate, BookingOut, ReviewCreate, ReviewOut
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Services"])


def _clean(cursor):
    try:
        while cursor.nextset():
            pass
    except Exception:
        pass
    cursor.close()


# ---------- CATEGORIES ----------

@router.get("/categories")
def get_categories(db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT DISTINCT category FROM services UNION SELECT name FROM categories ORDER BY 1")
        rows = cursor.fetchall()
        seen = set()
        result = []
        for r in rows:
            v = list(r.values())[0]
            if v and v not in seen:
                seen.add(v)
                result.append({"name": v})
        return result
    finally:
        _clean(cursor)


# ---------- SERVICES (public) ----------

@router.get("/services", response_model=list[ServiceOut])
def list_services(category: str = "", pincode: str = "", db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT * FROM services WHERE 1=1"
        params = []
        if category:
            query += " AND category = %s"
            params.append(category)
        if pincode:
            query += " AND pincode LIKE %s"
            params.append(f"%{pincode}%")
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        for r in rows:
            r["rating"] = float(r["rating"]) if r.get("rating") else 0
        return rows
    finally:
        _clean(cursor)


@router.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM services WHERE id = %s", (service_id,))
        row = cursor.fetchone()
        cursor.fetchall()
        if not row:
            raise HTTPException(404, "Service not found")
        row["rating"] = float(row["rating"]) if row.get("rating") else 0
        return row
    finally:
        _clean(cursor)


# ---------- ADMIN CRUD ----------

@router.post("/services", response_model=ServiceOut)
def create_service(
    name: str = Form(...),
    category: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    pincode: str = Form(...),
    image: UploadFile = None,
    user: dict = Depends(get_current_user),
    db: MySQLConnection = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    provider_id = user["id"]
    filename = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(image.file.read())

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO services (provider_id, category, name, phone, address, pincode, image) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (provider_id, category, name, phone, address, pincode, filename),
        )
        sid = cursor.lastrowid
        row = {"id": sid, "provider_id": provider_id, "category": category, "name": name,
               "phone": phone, "address": address, "pincode": pincode, "image": filename, "rating": 0}
        return row
    finally:
        _clean(cursor)


@router.put("/services/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    name: str = Form(...),
    category: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    pincode: str = Form(...),
    image: UploadFile = None,
    db: MySQLConnection = Depends(get_db),
):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM services WHERE id = %s", (service_id,))
        existing = cursor.fetchone()
        cursor.fetchall()
        if not existing:
            raise HTTPException(404, "Service not found")

        filename = existing["image"]
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            path = os.path.join(UPLOAD_DIR, filename)
            with open(path, "wb") as f:
                f.write(image.file.read())
            if existing["image"]:
                old = os.path.join(UPLOAD_DIR, existing["image"])
                if os.path.exists(old):
                    os.remove(old)

        cursor.execute(
            "UPDATE services SET name=%s, category=%s, phone=%s, address=%s, pincode=%s, image=%s WHERE id=%s",
            (name, category, phone, address, pincode, filename, service_id),
        )
        cursor.fetchall()

        return {"id": service_id, "provider_id": existing["provider_id"], "category": category,
                "name": name, "phone": phone, "address": address, "pincode": pincode, "image": filename, "rating": float(existing["rating"]) if existing.get("rating") else 0}
    finally:
        _clean(cursor)


@router.delete("/services/{service_id}")
def delete_service(service_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT image FROM services WHERE id = %s", (service_id,))
        row = cursor.fetchone()
        cursor.fetchall()
        if row and row.get("image"):
            path = os.path.join(UPLOAD_DIR, row["image"])
            if os.path.exists(path):
                os.remove(path)
        cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
        cursor.fetchall()
        return {"ok": True}
    finally:
        _clean(cursor)


# ---------- BOOKINGS ----------

@router.post("/bookings", response_model=BookingOut)
def create_booking(body: BookingCreate, user: dict = Depends(get_current_user), db: MySQLConnection = Depends(get_db)):
    customer_id = user["id"]
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO bookings (customer_id, service_id, booking_date) VALUES (%s,%s,%s)",
            (customer_id, body.service_id, body.booking_date),
        )
        bid = cursor.lastrowid
        return BookingOut(id=bid, customer_id=customer_id, service_id=body.service_id, booking_date=body.booking_date)
    finally:
        _clean(cursor)


@router.get("/bookings", response_model=list[BookingOut])
def my_bookings(user: dict = Depends(get_current_user), db: MySQLConnection = Depends(get_db)):
    customer_id = user["id"]
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT b.id, b.customer_id, b.service_id, b.booking_date,
                   s.name AS service_name, s.phone AS service_phone,
                   s.address AS service_address, s.image AS service_image,
                   s.category
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            WHERE b.customer_id = %s
            ORDER BY b.created_at DESC
        """, (customer_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        _clean(cursor)


# ---------- REVIEWS ----------

@router.post("/reviews", response_model=ReviewOut)
def create_review(body: ReviewCreate, user: dict = Depends(get_current_user), db: MySQLConnection = Depends(get_db)):
    user_id = user["id"]
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO reviews (user_id, service_id, rating, comment) VALUES (%s,%s,%s,%s)",
            (user_id, body.service_id, body.rating, body.comment),
        )
        rid = cursor.lastrowid

        cursor.execute("SELECT AVG(rating) AS avg_r FROM reviews WHERE service_id = %s", (body.service_id,))
        avg = cursor.fetchone()["avg_r"] or 0
        cursor.fetchall()
        cursor.execute("UPDATE services SET rating = %s WHERE id = %s", (round(avg, 1), body.service_id))
        cursor.fetchall()

        return ReviewOut(id=rid, user_id=user_id, service_id=body.service_id, rating=body.rating, comment=body.comment)
    finally:
        _clean(cursor)


@router.get("/reviews/{service_id}", response_model=list[ReviewOut])
def get_reviews(service_id: int, db: MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.*, u.username
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.service_id = %s
            ORDER BY r.created_at DESC
        """, (service_id,))
        return cursor.fetchall()
    finally:
        _clean(cursor)


# ---------- STATIC FILES ----------

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

def mount_uploads(app: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
