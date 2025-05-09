from app import create_app
from app.cache import  start_background_refresh


if __name__ == '__main__':
    app = create_app()
    start_background_refresh()
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True, )
