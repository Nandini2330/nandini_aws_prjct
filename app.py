from flask import Flask
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host="virtualclassroom-db.c38ekmug8xsr.ap-southeast-2.rds.amazonaws.com",
        user="admin",
        password="nandini232005",
        database="virtualclassroom"
    )
    return conn

@app.route("/")
def home():
    try:
        conn = get_db_connection()
        conn.close()
        return "Connected to AWS RDS Successfully!"
    except Exception as e:
        return f"Database connection failed: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)