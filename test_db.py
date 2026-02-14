import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="otp_db",
        user="postgres",
        password="Suhas@123"
    )
    print("Connected successfully!")
    conn.close()
except Exception as e:
    print("Error:", e)
