from flask import Flask
import psycopg2
import os

app = Flask(__name__)


@app.route("/")
def index():
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
        )
        conn.close()
        return f"Connected to PostgreSQL | Using {os.environ.get('APP_NAME')}"
    except Exception as e:
        return f"Failed to connect: {e}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
