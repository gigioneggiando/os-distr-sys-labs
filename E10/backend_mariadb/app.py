from flask import Flask, jsonify, request
import mysql.connector
import os
import time
import json

app = Flask(__name__)


def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("DB_USER", "appuser"),
        password=os.environ.get("DB_PASSWORD", "apppass"),
        database=os.environ.get("DB_NAME", "people_db"),
    )


def ensure_db_ready(retries=20, delay=2):
    for _ in range(retries):
        try:
            conn = get_connection()
            conn.close()
            return True
        except Exception:
            time.sleep(delay)
    return False


@app.route("/health", methods=["GET"])
def health():
    if ensure_db_ready(retries=2, delay=1):
        return {"status": "ok"}, 200
    return {"status": "db not ready"}, 503


@app.route("/person/", methods=["POST"])
def create_person():
    payload = request.get_json(silent=True) or request.form
    username = payload.get("username")
    email = payload.get("email")
    phone = payload.get("phone")
    profile_picture_path = payload.get("profile_picture_path", "")

    if not username or not email or not phone:
        return jsonify({"error": "username, email and phone are required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (username, email, phone, profile_picture_path)
        VALUES (%s, %s, %s, %s)
        """,
        (username, email, phone, profile_picture_path),
    )
    conn.commit()
    inserted_id = cur.lastrowid
    cur.close()
    conn.close()

    return jsonify({"message": "person created", "id": inserted_id}), 201


@app.route("/persons/", methods=["GET"])
def get_persons():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, username, email, phone, profile_picture_path FROM users ORDER BY id"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Save a JSON serialization file as requested by the exercise.
    with open("/tmp/persons.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    return jsonify(rows), 200


if __name__ == "__main__":
    ensure_db_ready()
    app.run(host="0.0.0.0", port=5000)
