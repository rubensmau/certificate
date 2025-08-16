from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Set the static folder to the parent directory (where index.html is located)
app = Flask(__name__, static_folder="..", static_url_path="")
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost:5432/tokens")


def get_db_connection():
    # conn = psycopg2.connect(DATABASE_URL)
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tokens",
        user="kkldb",
        password=os.environ.get("DB_PASSWORD"),  # Make sure this is included
    )
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()

    # First, create table without UNIQUE constraint
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            id SERIAL PRIMARY KEY,
            token VARCHAR(255) NOT NULL,
            de VARCHAR(255),
            para VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """
    )

    # Remove UNIQUE constraint if it exists (for existing databases)
    try:
        cur.execute("ALTER TABLE tokens DROP CONSTRAINT IF EXISTS tokens_token_key;")
    except Exception as e:
        # Constraint might not exist, that's fine
        pass

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def serve_index():
    """Serve the main index.html page"""
    return send_file("../index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/api/certificate", methods=["POST"])
def store_certificate():
    """Store certificate data (token, de, para) without validation"""
    print("=== Certificate POST request received ===")
    try:
        data = request.get_json()
        print(f"Request data: {data}")

        if not data:
            print("ERROR: No data provided")
            return jsonify({"error": "No data provided"}), 400

        token = data.get("token")
        de = data.get("de")
        para = data.get("para")

        if not token:
            print("ERROR: Token is required")
            return jsonify({"error": "Token is required"}), 400

        print(f"Inserting: token={token}, de={de}, para={para}")
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert certificate data (allows multiple entries with same token)
        cur.execute(
            """
            INSERT INTO tokens (token, de, para) 
            VALUES (%s, %s, %s) 
            RETURNING id, token, de, para, created_at
            """,
            (token, de, para),
        )

        result = cur.fetchone()
        conn.commit()

        cur.close()
        conn.close()

        return (
            jsonify(
                {
                    "id": result[0],
                    "token": result[1],
                    "de": result[2],
                    "para": result[3],
                    "created_at": result[4].isoformat(),
                }
            ),
            201,
        )

    except Exception as e:
        app.logger.error(f"Error storing certificate: {str(e)}")
        return jsonify({"error": "Failed to store certificate"}), 500


@app.route("/api/tokens", methods=["GET"])
def list_tokens():
    """List all tokens (admin endpoint)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT id, token, de, para, created_at FROM tokens ORDER BY created_at DESC"
        )

        tokens = cur.fetchall()

        cur.close()
        conn.close()

        # Convert datetime objects to ISO format
        for token in tokens:
            token["created_at"] = (
                token["created_at"].isoformat() if token["created_at"] else None
            )

        return jsonify({"tokens": tokens}), 200

    except Exception as e:
        app.logger.error(f"Error listing tokens: {str(e)}")
        return jsonify({"error": "Failed to list tokens"}), 500


@app.route("/api/test-db", methods=["GET"])
def test_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "DB connected", "result": result[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Initialize database tables
init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
