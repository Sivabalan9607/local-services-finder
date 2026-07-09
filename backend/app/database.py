import mysql.connector
from mysql.connector import pooling
import os
from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

_pool = None
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="urban_pool",
            pool_size=10,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            autocommit=True,
        )
    return _pool


def get_db():
    conn = get_pool().get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4")
    cursor.close()
    conn.close()

    conn = get_pool().get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE,
            full_name VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            phone VARCHAR(20),
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('customer', 'provider', 'admin') DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        INSERT IGNORE INTO categories (name) VALUES
        ('Plumber'), ('Electrician'), ('Mechanic'),
        ('Cleaner'), ('Painter'), ('Carpenter'),
        ('AC Technician'), ('Mover')
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            provider_id INT,
            category VARCHAR(255),
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            address TEXT,
            pincode VARCHAR(20),
            image VARCHAR(255),
            rating DECIMAL(2,1) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            service_id INT NOT NULL,
            booking_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            service_id INT NOT NULL,
            rating INT CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
        )
    """)

    cursor.close()
    conn.close()
