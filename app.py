from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DB = 'songs.db'

# Create DB and table if not exists
def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        conn.execute('''
            CREATE TABLE songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                filename TEXT NOT NULL,
                image TEXT
            )
        ''')
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# User homepage
@app.route('/')
def home():
    conn = get_db_connection()
    songs = conn.execute('SELECT * FROM songs').fetchall()
    conn.close()
    return render_template('index.html', songs=songs)

# Admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'amisha' and password == 'amisha123##':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return func(*args, **kwargs)
    return wrapper

# Admin dashboard
@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    songs = conn.execute('SELECT * FROM songs').fetchall()
    conn.close()
    return render_template('admin.html', songs=songs)

# Add song
@app.route('/admin/add', methods=['POST'])
@admin_required
def admin_add_song():
    title = request.form.get('title')
    artist = request.form.get('artist')
    filename = request.form.get('filename')
    image = request.form.get('image')
    if not title or not filename:
        flash('Title and filename are required!')
        return redirect(url_for('admin_dashboard'))
    conn = get_db_connection()
    conn.execute('INSERT INTO songs (title, artist, filename, image) VALUES (?, ?, ?, ?)',
                 (title, artist, filename, image))
    conn.commit()
    conn.close()
    flash('Song added successfully.')
    return redirect(url_for('admin_dashboard'))

# Edit song
@app.route('/admin/edit/<int:song_id>', methods=['POST'])
@admin_required
def admin_edit_song(song_id):
    title = request.form.get('title')
    artist = request.form.get('artist')
    filename = request.form.get('filename')
    image = request.form.get('image')
    if not title or not filename:
        flash('Title and filename are required!')
        return redirect(url_for('admin_dashboard'))
    conn = get_db_connection()
    conn.execute('UPDATE songs SET title=?, artist=?, filename=?, image=? WHERE id=?',
                 (title, artist, filename, image, song_id))
    conn.commit()
    conn.close()
    flash('Song updated successfully.')
    return redirect(url_for('admin_dashboard'))

# Delete song
@app.route('/admin/delete/<int:song_id>', methods=['POST'])
@admin_required
def admin_delete_song(song_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM songs WHERE id=?', (song_id,))
    conn.commit()
    conn.close()
    flash('Song deleted successfully.')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
