from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os


app = Flask(__name__)


@app.template_filter('add_stars')
def add_stars_filter(s):
    return f"★{s}★"


def init_db():
    if not os.path.exists('membership.db'):
        conn = sqlite3.connect('membership.db')
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS members (
                iid INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                phone TEXT,
                birthdate TEXT
            )
            '''
        )
        cursor.execute(
            '''
            INSERT OR IGNORE INTO members (
                username, email, password, phone, birthdate
            )
            VALUES (
                'admin', 'admin@example.com',
                'admin123', '0912345678', '1990-01-01'
            )
            '''
        )
        conn.commit()
        conn.close()


init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        phone = request.form['phone'].strip()
        birthdate = request.form['birthdate'].strip()

        if not username or not email or not password:
            return render_template(
                'error.html',
                message='請輸入用戶名、電子郵件和密碼'
            )

        conn = sqlite3.connect('membership.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM members WHERE username = ?',
            (username,)
        )
        if cursor.fetchone():
            conn.close()
            return render_template(
                'error.html',
                message='用戶名已存在'
            )

        cursor.execute(
            '''
            INSERT INTO members (
                username, email, password, phone, birthdate
            )
            VALUES (?, ?, ?, ?, ?)
            ''',
            (username, email, password, phone, birthdate)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not email or not password:
            return render_template(
                'error.html',
                message='請輸入電子郵件和密碼'
            )

        conn = sqlite3.connect('membership.db')
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM members WHERE email = ? AND password = ?',
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template(
                'welcome.html',
                username=user[1],
                iid=user[0]
            )
        else:
            return render_template(
                'error.html',
                message='電子郵件或密碼錯誤'
            )

    return render_template('login.html')


@app.route('/edit_profile/<int:iid>', methods=['GET', 'POST'])
def edit_profile(iid):
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        phone = request.form['phone'].strip()
        birthdate = request.form['birthdate'].strip()

        if not username or not email or not password:
            conn.close()
            return render_template(
                'error.html',
                message='請輸入用戶名、電子郵件和密碼'
            )

        cursor.execute(
            'SELECT * FROM members WHERE username = ? AND iid != ?',
            (username, iid)
        )
        if cursor.fetchone():
            conn.close()
            return render_template(
                'error.html',
                message='用戶名已被使用'
            )

        cursor.execute(
            'SELECT * FROM members WHERE email = ? AND iid != ?',
            (email, iid)
        )
        if cursor.fetchone():
            conn.close()
            return render_template(
                'error.html',
                message='電子郵件已被使用'
            )

        cursor.execute(
            '''
            UPDATE members
            SET username = ?, email = ?, password = ?, phone = ?, birthdate = ?
            WHERE iid = ?
            ''',
            (username, email, password, phone, birthdate, iid)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('welcome', iid=iid))
    else:
        cursor.execute('SELECT * FROM members WHERE iid = ?', (iid,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return render_template('edit_profile.html', user=user)
        else:
            return render_template(
                'error.html',
                message='用戶不存在'
            )


@app.route('/welcome/<int:iid>')
def welcome(iid):
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM members WHERE iid = ?', (iid,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template(
            'welcome.html',
            username=user[0],
            iid=iid
        )
    else:
        return render_template(
            'error.html',
            message='用戶不存在'
        )


@app.route('/delete/<int:iid>')
def delete(iid):
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM members WHERE iid = ?', (iid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ✅ 建議使用 Flask CLI 方式啟動應用：
# Windows:
#   set FLASK_APP=app.py
#   flask --debug run
# macOS/Linux:
#   export FLASK_APP=app.py
#   flask --debug run
