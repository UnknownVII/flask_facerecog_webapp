import sqlite3

DB_PATH = 'camera_db.sqlite'

def update_all_embeddings(new_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Update every row in the embeddings table
    c.execute('''UPDATE embeddings SET name = ?''', (new_name,))

    conn.commit()
    conn.close()
    print(f"Updated all embeddings to '{new_name}'.")

update_all_embeddings('Wilbert')