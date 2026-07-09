# seed_supabase.py
from app.database import get_db
from passlib.hash import bcrypt
import random

db = get_db()

# Clear old data
print("Clearing old data from Supabase...")
try:
    db.table("reviews").delete().neq("id", 0).execute()
    db.table("bookings").delete().neq("id", 0).execute()
    db.table("services").delete().neq("id", 0).execute()
    db.table("users").delete().in_("username", ["admin", "john"]).execute()
except Exception as e:
    print(f"Warning during table cleanup: {e}")
    print("Please make sure the supabase_schema.sql script was executed in your Supabase Dashboard SQL Editor.")

# Create users
print("Seeding users...")
pw = bcrypt.hash("admin123")
res_admin = db.table("users").insert({
    "username": "admin", 
    "full_name": "Admin", 
    "email": "admin@test.com", 
    "phone": "555-0000", 
    "password_hash": pw, 
    "role": "admin"
}).execute()

pw2 = bcrypt.hash("test123")
res_customer = db.table("users").insert({
    "username": "john", 
    "full_name": "John Doe", 
    "email": "john@test.com", 
    "phone": "555-1111", 
    "password_hash": pw2, 
    "role": "customer"
}).execute()

if not res_customer.data or not res_admin.data:
    raise ValueError("Failed to create seed users in Supabase.")

customer_id = res_customer.data[0]['id']
provider_id = res_admin.data[0]['id']

# Services with Chennai addresses and images
services = [
    ("Plumber",     "Raju Plumbing",         "9876543210", "12, Anna Nagar West, Chennai",            "600040", "plumber.jpg"),
    ("Plumber",     "Shyam Plumbing Works",  "9876543211", "45, T Nagar, Chennai",                     "600017", "plumber.jpg"),
    ("Electrician", "Kumar Electricals",     "9876543212", "78, Velachery, Chennai",                   "600042", "electrician.jpg"),
    ("Electrician", "Singh Electric Works",  "9876543213", "23, Adyar, Chennai",                       "600020", "electrician.jpg"),
    ("Mechanic",    "Patel Garage",          "9876543214", "56, Chromepet, Chennai",                   "600044", "mechanic.jpg"),
    ("Mechanic",    "Sharma Auto Repair",    "9876543215", "89, Porur, Chennai",                       "600116", "mechanic.jpg"),
    ("AC Tech",     "Cool Ace Services",     "9876543216", "34, Thoraipakkam, OMR, Chennai",          "600097", "ac_tech.jpg"),
    ("Cleaner",     "Sparkle Cleaners",      "9876543217", "67, Mylapore, Chennai",                    "600004", "cleaner.jpg"),
    ("Painter",     "Rainbow Painting Co",   "9876543218", "101, Nungambakkam, Chennai",               "600034", "painter.jpg"),
    ("Carpenter",   "Woodcraft Solutions",   "9876543219", "22, Tambaram, Chennai",                    "600045", "carpenter.jpg"),
    ("Electrician", "VoltMaster Electricals", "9876543220", "15, Thiruvanmiyur, Chennai",              "600041", "electrician.jpg"),
    ("Plumber",     "Ganga Plumbing",        "9876543221", "8, Perambur, Chennai",                     "600011", "plumber.jpg"),
]

print("Seeding services...")
svcs = []
for cat, name, phone, addr, pin, img in services:
    res = db.table("services").insert({
        "category": cat,
        "name": name,
        "phone": phone,
        "address": addr,
        "pincode": pin,
        "image": img,
        "provider_id": provider_id
    }).execute()
    svcs.append(res.data[0])

# Add some sample reviews
comments = [
    "Excellent service! Very professional.",
    "Good work, reasonably priced.",
    "Quick response and quality work.",
    "Satisfied with the service.",
    "Very knowledgeable and friendly.",
    "Did a great job, will hire again.",
    "On time and did quality work.",
    "Best service provider in the area.",
]

print("Seeding reviews...")
for svc in svcs[:6]:
    for _ in range(random.randint(1, 3)):
        rating = random.randint(3, 5)
        comment = random.choice(comments)
        db.table("reviews").insert({
            "user_id": customer_id,
            "service_id": svc['id'],
            "rating": rating,
            "comment": comment
        }).execute()

# Update service ratings based on reviews average
print("Updating service ratings...")
for svc in svcs:
    avg_res = db.table("reviews").select("rating").eq("service_id", svc['id']).execute()
    ratings = [r['rating'] for r in avg_res.data]
    if ratings:
        avg = sum(ratings) / len(ratings)
        db.table("services").update({"rating": round(avg, 1)}).eq("id", svc['id']).execute()

print("Supabase Chennai data seeded successfully!")
print("Login: john / test123")
print("Admin: admin / admin123")
