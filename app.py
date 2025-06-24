from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'

DB = 'songs.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT,
            filename TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM songs')
    songs = c.fetchall()
    conn.close()
    return render_template('index.html', songs=songs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'amisha' and request.form['password'] == 'amisha123##':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM songs')
    songs = c.fetchall()
    conn.close()
    return render_template('admin.html', songs=songs)

@app.route('/add_song', methods=['POST'])
def add_song():
    if 'admin' not in session:
        return redirect(url_for('login'))
    title = request.form['title']
    artist = request.form['artist']
    filename = request.form['filename']
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('INSERT INTO songs (title, artist, filename) VALUES (?, ?, ?)', (title, artist, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_song/<int:song_id>')
def delete_song(song_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('DELETE FROM songs WHERE id = ?', (song_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()  # Initialize DB here, no before_first_request
    app.run(debug=True)
