import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from supabase import Client
from app.database import get_db, UPLOAD_DIR
from app.models import ServiceCreate, ServiceOut, BookingCreate, BookingOut, ReviewCreate, ReviewOut
from app.routes.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Services"])


# ---------- CATEGORIES ----------

@router.get("/categories")
def get_categories(db: Client = Depends(get_db)):
    try:
        # Select distinct categories from services and categories table
        res_svc = db.table("services").select("category").execute()
        res_cat = db.table("categories").select("name").execute()
        
        cats = set([r["category"] for r in res_svc.data if r.get("category")])
        cats.update([r["name"] for r in res_cat.data if r.get("name")])
        
        return [{"name": c} for c in sorted(list(cats))]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- SERVICES (public) ----------

@router.get("/services", response_model=list[ServiceOut])
def list_services(category: str = "", pincode: str = "", db: Client = Depends(get_db)):
    try:
        query = db.table("services").select("*")
        if category:
            query = query.eq("category", category)
        if pincode:
            query = query.ilike("pincode", f"%{pincode}%")
        
        res = query.order("created_at", desc=True).execute()
        
        rows = res.data
        for r in rows:
            r["rating"] = float(r["rating"]) if r.get("rating") else 0
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Client = Depends(get_db)):
    try:
        res = db.table("services").select("*").eq("id", service_id).execute()
        if not res.data:
            raise HTTPException(404, "Service not found")
        
        row = res.data[0]
        row["rating"] = float(row["rating"]) if row.get("rating") else 0
        return row
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- ADMIN CRUD ----------

@router.post("/services", response_model=ServiceOut)
def create_service(
    name: str = Form(...),
    category: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    pincode: str = Form(...),
    image: UploadFile = None,
    db: Client = Depends(get_db),
    provider_id: int = 1,
):
    try:
        filename = None
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            path = os.path.join(UPLOAD_DIR, filename)
            with open(path, "wb") as f:
                f.write(image.file.read())

        res = db.table("services").insert({
            "name": name,
            "category": category,
            "phone": phone,
            "address": address,
            "pincode": pincode,
            "image": filename,
            "provider_id": provider_id
        }).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create service")
        
        row = res.data[0]
        row["rating"] = float(row["rating"]) if row.get("rating") else 0
        return row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/services/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int,
    name: str = Form(...),
    category: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    pincode: str = Form(...),
    image: UploadFile = None,
    db: Client = Depends(get_db),
):
    try:
        filename = None
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            path = os.path.join(UPLOAD_DIR, filename)
            with open(path, "wb") as f:
                f.write(image.file.read())

        update_data = {
            "name": name,
            "category": category,
            "phone": phone,
            "address": address,
            "pincode": pincode,
        }
        if filename:
            update_data["image"] = filename

        res = db.table("services").update(update_data).eq("id", service_id).execute()
        if not res.data:
            raise HTTPException(404, "Service not found")
        
        row = res.data[0]
        row["rating"] = float(row["rating"]) if row.get("rating") else 0
        return row
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/services/{service_id}")
def delete_service(service_id: int, db: Client = Depends(get_db)):
    try:
        res = db.table("services").delete().eq("id", service_id).execute()
        if not res.data:
            raise HTTPException(404, "Service not found")
        return {"detail": "Service deleted"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- BOOKINGS ----------

@router.post("/bookings", response_model=BookingOut)
def create_booking(body: BookingCreate, current_user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    try:
        customer_id = current_user["id"]
        res = db.table("bookings").insert({
            "customer_id": customer_id,
            "service_id": body.service_id,
            "booking_date": str(body.booking_date)
        }).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create booking")
        
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings", response_model=list[BookingOut])
def get_bookings(current_user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    try:
        customer_id = current_user["id"]
        
        # Load bookings with nested services details
        res = db.table("bookings").select("*, services:service_id(*)").eq("customer_id", customer_id).order("created_at", desc=True).execute()
        
        rows = []
        for r in res.data:
            svc = r.pop("services", {})
            if svc:
                r["service_name"] = svc.get("name")
                r["service_category"] = svc.get("category")
                r["service_image"] = svc.get("image")
                r["service_address"] = svc.get("address")
            else:
                r["service_name"] = ""
                r["service_category"] = ""
                r["service_image"] = ""
                r["service_address"] = ""
            rows.append(r)
            
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- REVIEWS ----------

@router.post("/reviews", response_model=ReviewOut)
def create_review(body: ReviewCreate, current_user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    try:
        user_id = current_user["id"]
        
        # Insert review
        res = db.table("reviews").insert({
            "user_id": user_id,
            "service_id": body.service_id,
            "rating": body.rating,
            "comment": body.comment
        }).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create review")

        rid = res.data[0]["id"]

        # Recalculate average rating for service
        avg_res = db.table("reviews").select("rating").eq("service_id", body.service_id).execute()
        ratings = [r["rating"] for r in avg_res.data]
        avg = sum(ratings) / len(ratings) if ratings else 0

        # Update service rating
        db.table("services").update({"rating": round(avg, 1)}).eq("id", body.service_id).execute()

        return ReviewOut(
            id=rid,
            user_id=user_id,
            service_id=body.service_id,
            rating=body.rating,
            comment=body.comment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews/{service_id}", response_model=list[ReviewOut])
def get_reviews(service_id: int, db: Client = Depends(get_db)):
    try:
        # Load reviews with nested users details
        res = db.table("reviews").select("*, users:user_id(username)").eq("service_id", service_id).order("created_at", desc=True).execute()
        
        rows = []
        for r in res.data:
            usr = r.pop("users", {})
            r["username"] = usr.get("username") if usr else None
            rows.append(r)
            
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- STATIC FILES ----------

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

def mount_uploads(app: FastAPI):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
