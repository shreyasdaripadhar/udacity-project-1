from flask import Flask, jsonify
import json
from functools import wraps
import sqlite3
from threading import Lock
import mysql.connector


app = Flask(__name__)

@app.route("/")
def hello():
    app.logger.debug('/ is accessed')
    return "Hello World!"

DB_CONFIG = {
    'host': 'localhost', 
    'user': 'root',
    'password': 'progress',
    'database': 'course_1'
}

db_connection_count = 0

def get_db_connection():
    """Create and return a database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def track_db_connection(f):
    """Decorator to track database connections"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global db_connection_count
        db_connection_count += 1
        return f(*args, **kwargs)
    return decorated_function

@track_db_connection
def get_post_count():
    """Get total number of posts from POSTS table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM POSTS")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error getting post count: {e}")
        return 0

@app.route("/metrics")
def metrics():
    try:
        post_count = get_post_count()  # This will increment the connection counter
        
        metrics_data = {
            "db_connection_count": db_connection_count,
            "post_count": post_count
        }
        
        return jsonify(metrics_data), 200
        
    except Exception as e:
        error_response = {
            "error": "Failed to fetch metrics",
            "message": str(e)
        }
        return jsonify(error_response), 500

@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    app.logger.debug('/healthz is accessed')
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003)
