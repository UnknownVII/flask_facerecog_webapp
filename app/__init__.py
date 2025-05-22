import os
from flask import Flask
from dotenv import load_dotenv

from app.globals import reload_camera_data
from .routes import main
from .models import init_db, init_embeddings_db

# Load env once
load_dotenv()

def create_app():
    init_db()
    init_embeddings_db()

    app = Flask(
        __name__,
        static_folder=os.path.join("app", "static")
    )

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        DEBUG=os.getenv("DEBUG", "False") == "True"
    )

    app.register_blueprint(main)
    
    reload_camera_data()

    return app
