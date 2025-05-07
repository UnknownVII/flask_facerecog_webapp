from collections import deque
import sqlite3

DB_PATH = 'camera_db.sqlite'

name_update_queue = deque()

def queue_name_update(camera_id, new_name):
    name_update_queue.append((camera_id, new_name))

def update_names_in_queue():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    while name_update_queue:
        camera_id, new_name = name_update_queue.popleft()
        c.execute('UPDATE embeddings SET name = ? WHERE camera_id = ?', (new_name, camera_id))

    conn.commit()
    conn.close()
