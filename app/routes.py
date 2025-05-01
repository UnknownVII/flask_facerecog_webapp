from flask import Blueprint, render_template, Response, send_file, make_response
from .camera import gen_frames, refresh_camera_feed, get_face_count, take_snapshot, reset_snapshot
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/snapshot')
def snapshot():
    if os.path.exists("app/static/snapshots/snapshot.jpg"):
        response = make_response(send_file("static/snapshots/snapshot.jpg", mimetype='image/jpeg'))
        response.headers['Cache-Control'] = 'no-store'
        return response
    else:
        return "No snapshot yet", 404

@main.route('/reset_snapshot')
def reset_snapshot_route():
    reset_snapshot()
    return "Snapshot reset", 200

@main.route('/face_count')
def face_count():
    return get_face_count()

@main.route('/refresh_camera')
def refresh_camera():
    return refresh_camera_feed()
