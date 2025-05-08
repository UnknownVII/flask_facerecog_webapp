import threading
import time
import logging
from app.models import get_all_embeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)
embedding_cache = []

def load_embeddings():
    global embedding_cache
    try:
        embedding_cache = get_all_embeddings()  # This should update the global cache
        logger.info(f"Loaded {len(embedding_cache)} embeddings.")
        if not embedding_cache:
            logger.warning("No embeddings were loaded.")
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}")


def periodic_refresh(interval=60):  # Set a smaller interval for testing
    while True:
        logger.info(f"Starting embeddings refresh...")
        load_embeddings()  # This should refresh the embeddings in the cache
        logger.info(f"Embeddings refreshed. Next refresh in {interval} seconds.")
        time.sleep(interval)


def start_background_refresh():
    t = threading.Thread(target=periodic_refresh, daemon=True)
    t.start()
    logger.info("Background refresh started.")

# Example usage: Start the periodic refresh process
start_background_refresh()

