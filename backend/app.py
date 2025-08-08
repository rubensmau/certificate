from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432/tokens')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id SERIAL PRIMARY KEY,
            token VARCHAR(255) UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'UNUSED',
            created_at TIMESTAMP DEFAULT NOW(),
            used_at TIMESTAMP
        );
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/tokens', methods=['POST'])
def create_token():
    """Create a new token"""
    try:
        # Generate unique token
        token = str(uuid.uuid4())
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO tokens (token) VALUES (%s) RETURNING id, token, status, created_at",
            (token,)
        )
        
        result = cur.fetchone()
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({
            "token": result[1],
            "status": result[2],
            "created_at": result[3].isoformat(),
            "url": f"https://rubensmau.github.io/certificate/?token={result[1]}"
        }), 201
        
    except Exception as e:
        app.logger.error(f"Error creating token: {str(e)}")
        return jsonify({"error": "Failed to create token"}), 500

@app.route('/tokens/<token>', methods=['GET'])
def validate_token(token):
    """Validate token and mark as IN_USE"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if token exists and is unused
        cur.execute(
            "SELECT * FROM tokens WHERE token = %s",
            (token,)
        )
        
        result = cur.fetchone()
        
        if not result:
            cur.close()
            conn.close()
            return jsonify({"error": "Token not found"}), 404
            
        if result['status'] == 'COMPLETED':
            cur.close()
            conn.close()
            return jsonify({"error": "Token already used"}), 400
            
        # Mark token as IN_USE if it was UNUSED
        if result['status'] == 'UNUSED':
            cur.execute(
                "UPDATE tokens SET status = 'IN_USE' WHERE token = %s",
                (token,)
            )
            conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({
            "token": result['token'],
            "status": "IN_USE",
            "valid": True
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error validating token: {str(e)}")
        return jsonify({"error": "Failed to validate token"}), 500

@app.route('/tokens/<token>', methods=['DELETE'])
def complete_token(token):
    """Mark token as COMPLETED (used)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Update token status to COMPLETED
        cur.execute(
            "UPDATE tokens SET status = 'COMPLETED', used_at = NOW() WHERE token = %s AND status = 'IN_USE'",
            (token,)
        )
        
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return jsonify({"error": "Token not found or not in use"}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": "Token marked as completed"}), 200
        
    except Exception as e:
        app.logger.error(f"Error completing token: {str(e)}")
        return jsonify({"error": "Failed to complete token"}), 500

@app.route('/tokens', methods=['GET'])
def list_tokens():
    """List all tokens (admin endpoint)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT token, status, created_at, used_at FROM tokens ORDER BY created_at DESC"
        )
        
        tokens = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Convert datetime objects to ISO format
        for token in tokens:
            token['created_at'] = token['created_at'].isoformat() if token['created_at'] else None
            token['used_at'] = token['used_at'].isoformat() if token['used_at'] else None
        
        return jsonify({"tokens": tokens}), 200
        
    except Exception as e:
        app.logger.error(f"Error listing tokens: {str(e)}")
        return jsonify({"error": "Failed to list tokens"}), 500

# Initialize database tables
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))