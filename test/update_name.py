import sqlite3

DB_PATH = 'camera_db.sqlite'

def update_embeddings_by_id(embedding_ids, new_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for embedding_id in embedding_ids:
        # Update name for each embedding ID
        c.execute('''UPDATE embeddings SET name = ? WHERE id = ?''', (new_name, embedding_id))

    conn.commit()
    conn.close()
    print(f"Updated embeddings with IDs {embedding_ids} to '{new_name}'.")

# Example usage
embedding_ids_to_update = [4]  # List of embedding IDs you want to update
update_embeddings_by_id(embedding_ids_to_update, "Wilbert")
