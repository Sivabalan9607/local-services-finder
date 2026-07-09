from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

r = client.post("/auth/login", json={"email": "john@example.com", "password": "test123"})
if r.status_code != 200:
    r = client.post("/auth/register", json={
        "full_name": "John Doe", "email": "john@example.com",
        "phone": "555-0100", "password": "test123", "role": "provider",
    })

print("Provider ready")

services = [
    {"category_id": 1, "title": "Electrical Wiring Repair", "description": "Complete wiring repair for homes and offices", "price": 89.99, "city": "New York"},
    {"category_id": 1, "title": "Smart Home Installation", "description": "Install smart switches, dimmers, and outlets", "price": 129.99, "city": "New York"},
    {"category_id": 2, "title": "Pipe Leak Repair", "description": "Fix leaking pipes under sinks and walls", "price": 69.99, "city": "New York"},
    {"category_id": 2, "title": "Drain Cleaning", "description": "Clear clogged drains in kitchen and bathroom", "price": 59.99, "city": "New York"},
    {"category_id": 3, "title": "Deep Home Cleaning", "description": "Full home deep cleaning service", "price": 149.99, "city": "New York"},
    {"category_id": 3, "title": "Office Sanitization", "description": "Complete office sanitization and cleaning", "price": 199.99, "city": "New York"},
    {"category_id": 4, "title": "AC Installation", "description": "Window and split AC installation", "price": 99.99, "city": "New York"},
    {"category_id": 4, "title": "AC Servicing", "description": "Annual AC maintenance and gas refill", "price": 79.99, "city": "New York"},
    {"category_id": 5, "title": "Apartment Moving", "description": "Full apartment packing and moving service", "price": 299.99, "city": "New York"},
    {"category_id": 6, "title": "Interior Painting", "description": "Professional interior wall painting", "price": 249.99, "city": "New York"},
]

for s in services:
    r = client.post("/api/services", json=s, params={"provider_id": 1})
    status = "OK" if r.status_code == 200 else f"FAIL ({r.status_code})"
    print(f"  {status}: {s['title']}")

print("Seed complete!")
