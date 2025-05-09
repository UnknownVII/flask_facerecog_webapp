import sqlite3
import numpy as np

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

def init_embeddings_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    camera_id INTEGER,
                    name TEXT DEFAULT 'Unknown',
                    embedding BLOB,
                    snapshot BLOB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (camera_id) REFERENCES cameras (id)
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


def store_embedding(camera_id, embedding, face_img, name="Unknown"):
    import sqlite3
    import numpy as np
    import cv2

    embedding_bytes = embedding.tobytes()

    # Encode face image as JPEG
    snapshot_blob = None
    if face_img is not None and face_img.size > 0:
        success, encoded_img = cv2.imencode('.jpg', face_img)
        if success:
            snapshot_blob = encoded_img.tobytes()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT embedding FROM embeddings WHERE camera_id = ?', (camera_id,))
    rows = c.fetchall()

    for row in rows:
        saved_embedding = np.frombuffer(row[0], dtype=np.float32)
        if is_similar(embedding, saved_embedding):
            conn.close()
            return  # Skip if similar

    # Insert embedding + snapshot
    c.execute(
        '''INSERT INTO embeddings (camera_id, name, embedding, snapshot) VALUES (?, ?, ?, ?)''',
        (camera_id, name, embedding_bytes, snapshot_blob)
    )

    conn.commit()
    conn.close()

def is_similar(embedding1, embedding2, threshold=0.8):
    """Compute cosine similarity between two embeddings and return True if similar."""
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    cosine_similarity = dot_product / (norm1 * norm2)
    return cosine_similarity > threshold

def get_all_embeddings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id, name, embedding FROM embeddings''')
    rows = c.fetchall()

    embeddings = []
    for row in rows:
        emb = np.frombuffer(row[2], dtype=np.float32)  # Convert BLOB to numpy array
        embeddings.append({
            "id": row[0],
            "name": row[1],
            "embedding": emb
        })

    conn.close()
    return embeddings
