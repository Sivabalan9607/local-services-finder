from app.database import get_pool
from passlib.hash import bcrypt

pool = get_pool()
conn = pool.get_connection()
cur = conn.cursor()

# Clear old data
cur.execute("DELETE FROM reviews")
cur.execute("DELETE FROM bookings")
cur.execute("DELETE FROM services")
cur.execute("DELETE FROM users WHERE username IN ('admin','john')")

# Create users
pw = bcrypt.hash("admin123")
cur.execute(
    "INSERT INTO users (username, full_name, email, phone, password_hash, role) VALUES (%s, %s, %s, %s, %s, %s)",
    ("admin", "Admin", "admin@test.com", "555-0000", pw, "admin"),
)

pw2 = bcrypt.hash("test123")
cur.execute(
    "INSERT INTO users (username, full_name, email, phone, password_hash, role) VALUES (%s, %s, %s, %s, %s, %s)",
    ("john", "John Doe", "john@test.com", "555-1111", pw2, "customer"),
)

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

for cat, name, phone, addr, pin, img in services:
    cur.execute(
        "INSERT INTO services (category, name, phone, address, pincode, image) VALUES (%s, %s, %s, %s, %s, %s)",
        (cat, name, phone, addr, pin, img),
    )

# Get user id for customer
cur.execute("SELECT id FROM users WHERE username='john'")
customer_id = cur.fetchone()[0]

# Add some sample reviews
cur.execute("SELECT id, name FROM services")
svcs = cur.fetchall()

import random
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
for svc in svcs[:6]:
    for _ in range(random.randint(1, 3)):
        rating = random.randint(3, 5)
        comment = random.choice(comments)
        cur.execute(
            "INSERT INTO reviews (user_id, service_id, rating, comment) VALUES (%s, %s, %s, %s)",
            (customer_id, svc[0], rating, comment),
        )

# Update ratings
cur.execute("""
    UPDATE services s
    SET rating = (
        SELECT COALESCE(ROUND(AVG(rating), 1), 0)
        FROM reviews
        WHERE service_id = s.id
    )
""")

conn.commit()
cur.close()
conn.close()
print("Chennai data seeded!")
print("Login: john / test123")
print("Admin: admin / admin123")
