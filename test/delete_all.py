import sqlite3

DB_PATH = 'camera_db.sqlite'

def delete_unknown_embeddings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Delete all embeddings with name "Unknown"
    c.execute('''DELETE FROM embeddings WHERE name = 'Unknown' ''')

    conn.commit()
    conn.close()
    print("Deleted all embeddings with name 'Unknown'.")

# Call the function to delete all "Unknown" embeddings
delete_unknown_embeddings()
