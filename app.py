from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import random
from datetime import datetime, timedelta
import hashlib

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Database Connection
# ---------------------------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="otp_db",
        user="postgres",
        password="Suhas@123"   # your DB password
    )

# ---------------------------
# Request Models
# ---------------------------
class LoginRequest(BaseModel):
    username: str
    first_name: str | None = None
    second_name: str | None = None
    gender: str | None = None


class VerifyOTP(BaseModel):
    username: str
    otp: str


# ---------------------------
# OTP Utilities
# ---------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp(input_otp: str, stored_hash: str) -> bool:
    return hash_otp(input_otp) == stored_hash


# ===========================
# LOGIN ENDPOINT
# ===========================
@app.post("/login")
def login(data: LoginRequest):
    conn = get_connection()
    cur = conn.cursor()

    # Check if user exists
    cur.execute("SELECT user_id FROM users WHERE username = %s", (data.username,))
    user = cur.fetchone()

    # If new user → create
    if not user:
        if not data.first_name or not data.second_name or not data.gender:
            raise HTTPException(status_code=400, detail="New user must provide profile details")

        cur.execute(
            """
            INSERT INTO users (username, first_name, second_name, gender)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id
            """,
            (data.username, data.first_name, data.second_name, data.gender)
        )
        user_id = cur.fetchone()[0]
    else:
        user_id = user[0]

    # Generate OTP
    otp = generate_otp()
    otp_hash = hash_otp(otp)
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Store OTP
    cur.execute(
        """
        INSERT INTO user_otp (user_id, otp_hash, expires_at)
        VALUES (%s, %s, %s)
        """,
        (user_id, otp_hash, expires_at)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {
        "message": "OTP generated",
        "otp_for_testing": otp   # Remove in production
    }


# ===========================
# VERIFY ENDPOINT
# ===========================
@app.post("/verify")
def verify(data: VerifyOTP):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users WHERE username = %s", (data.username,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user[0]

    # Get latest OTP
    cur.execute(
        """
        SELECT otp_id, otp_hash, expires_at
        FROM user_otp
        WHERE user_id = %s AND is_verified = FALSE
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user_id,)
    )

    otp_record = cur.fetchone()

    if not otp_record:
        raise HTTPException(status_code=400, detail="No OTP found")

    otp_id, otp_hash, expires_at = otp_record

    # Check expiry
    if datetime.utcnow() > expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")

    # Verify OTP
    if not verify_otp(data.otp, otp_hash):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Mark OTP as verified
    cur.execute(
        "UPDATE user_otp SET is_verified = TRUE WHERE otp_id = %s",
        (otp_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Login successful"}
