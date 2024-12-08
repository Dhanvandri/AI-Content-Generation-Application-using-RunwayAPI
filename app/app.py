from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import threading
from .generate_content import generate_content

app = Flask(__name__)

# Retrieve the secret key from an environment variable
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

DB_PATH = r"/home/devil/Documents/python/flaskproject/app/database/content.db"

def connect_db():
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def home():
    """Redirect to the login page."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login and log the event in the database."""
    if request.method == 'POST':
        user_id = request.form['user_id'].strip()
        if not user_id:
            flash("User ID cannot be empty!")
            return redirect(url_for('login'))

        try:
            with connect_db() as conn:
                if conn is None:
                    flash("Database connection failed.")
                    return redirect(url_for('login'))

                # Check if user exists
                cur = conn.cursor()
                cur.execute("SELECT * FROM content_generation WHERE user_id = ?", (user_id,))
                user_data = cur.fetchone()

                # Log the login event
                cur.execute("INSERT INTO login_logs (user_id, action) VALUES (?, ?)", (user_id, 'LOGIN'))
                conn.commit()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            flash("Internal server error.")
            return redirect(url_for('login'))

        # Redirect user to prompt page
        return redirect(url_for('prompt', user_id=user_id))

    return render_template('login.html')

@app.route('/prompt/<user_id>', methods=['GET', 'POST'])
def prompt(user_id):
    """Page to input text prompt and trigger content generation."""
    if request.method == 'POST':
        prompt_text = request.form['prompt']
        if not prompt_text.strip():
            flash("Prompt cannot be empty!")
            return redirect(url_for('prompt', user_id=user_id))

        # Start content generation in a background thread
        thread = threading.Thread(target=generate_content, args=(user_id, prompt_text))
        thread.start()

        flash("Content generation started! Please check back later.")
        return redirect(url_for('gallery', user_id=user_id))

    return render_template('prompt.html', user_id=user_id)

@app.route('/gallery/<user_id>')
def gallery(user_id):
    """Display generated content for the user."""
    try:
        with connect_db() as conn:
            if conn is None:
                flash("Database connection failed.")
                return redirect(url_for('login'))

            cur = conn.cursor()
            cur.execute("SELECT video_paths, image_paths FROM content_generation WHERE user_id = ?", (user_id,))
            data = cur.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash("Internal server error.")
        return redirect(url_for('login'))

    if data:
        video_paths = data["video_paths"].split(',') if data["video_paths"] else []
        image_paths = data["image_paths"].split(',') if data["image_paths"] else []
        return render_template('gallery.html', videos=video_paths, images=image_paths, user_id=user_id)

    flash("No content available for this user.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
