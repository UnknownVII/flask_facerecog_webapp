import sqlite3

DB_PATH = 'camera_db.sqlite'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cameras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    ip TEXT,
                    username TEXT,
                    password TEXT,
                    stream INTEGER DEFAULT 0,
                    rtsp_url TEXT,
                    working INTEGER DEFAULT 0
                )''')
    conn.commit()
    conn.close()

def build_rtsp_url(ip, username, password, stream):
    return f"rtsp://{username}:{password}@{ip}/stream{stream}"


def add_camera(name, ip, username, password, stream):
    rtsp_url = build_rtsp_url(ip, username, password, stream)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO cameras (name, ip, username, password, stream, rtsp_url)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (name, ip, username, password, stream, rtsp_url))
    conn.commit()
    conn.close()

def update_camera(id, name, ip, username, password, stream):
    rtsp_url = build_rtsp_url(ip, username, password, stream)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''UPDATE cameras SET name=?, ip=?, username=?, password=?, stream=?, rtsp_url=?, working=0
                 WHERE id=?''',
              (name, ip, username, password, stream, rtsp_url, id))
    conn.commit()
    conn.close()


def get_all_cameras():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, rtsp_url, working FROM cameras")
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_working_cameras():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, rtsp_url, working FROM cameras WHERE working = 1")
    rows = c.fetchall()
    conn.close()
    return rows


def set_camera_status(id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE cameras SET working=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()

def get_camera_by_id(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, name, ip, username, password, stream, rtsp_url, working 
                 FROM cameras WHERE id = ?''', (id,))
    row = c.fetchone()
    conn.close()
    return row

def delete_camera(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM cameras WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def is_ip_unique(ip):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cameras WHERE ip=?", (ip,))
    count = c.fetchone()[0]
    conn.close()
    return count == 0
