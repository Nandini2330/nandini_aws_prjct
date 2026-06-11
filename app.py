from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import boto3

app = Flask(__name__)

BUCKET_NAME = "nandini-project-bucket-2026"
s3 = boto3.client("s3")

def get_db_connection():
    return mysql.connector.connect(
        host="virtualclassroom-db.c38ekmug8xsr.ap-southeast-2.rds.amazonaws.com",
        user="admin",
        password="Nandini12345",
        database="virtualclassroom"
    )

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100),
            password VARCHAR(100)
        )""")
        cur.execute("INSERT INTO users(username,password) VALUES(%s,%s)", (username,password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username,password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return redirect(url_for("dashboard"))
        return "Invalid Login"
    return render_template("login.html")

@app.route("/instructor", methods=["GET","POST"])
def instructor():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            return redirect(url_for("upload"))
        return "Invalid Instructor Login"
    return render_template("instructor.html")

@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file.filename:
            s3.upload_fileobj(file, BUCKET_NAME, file.filename)

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS materials(
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255)
            )""")
            cur.execute("INSERT INTO materials(filename) VALUES(%s)", (file.filename,))
            conn.commit()
            cur.close()
            conn.close()
            return "File Uploaded Successfully"
    return render_template("upload.html")

@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(255)
    )
    """)

    cursor.execute("SELECT filename FROM materials")
    files = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        files=files
    )

@app.route("/logout")
def logout():
    return redirect(url_for("home"))

@app.route("/download/<filename>")
def download(filename):
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": filename},
        ExpiresIn=3600
    )
    return redirect(url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
