from dotenv import load_dotenv
from flask import Flask

from .routes import main
from .models import init_db, init_embeddings_db

import os

def create_app():
    load_dotenv()
    app = Flask(
        __name__,
        static_folder=os.path.join("app", "static")
    )
    app.secret_key = os.getenv("SECRET_KEY")
    # Set up a static folder for the snapshots
    # Register the Blueprint
    app.register_blueprint(main)
    init_db()
    init_embeddings_db()
    return app