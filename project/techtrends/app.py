import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from functools import wraps


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM POSTS').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

connection_count = 0
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count += 1
    return connection

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
        app.logger.debug('error in getting db connection')
        return 0

@app.route("/metrics")
def metrics():
    try:
        post_count = get_post_count()
        
        metrics_data = {
            "db_connection_count": connection_count,
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

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
