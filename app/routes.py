from collections import namedtuple
import math
from flask import Blueprint, flash, jsonify, redirect, render_template, Response, request

from app.models import add_camera, delete_camera, get_all_cameras, get_all_embeddings, get_all_logs_embeddings,  get_camera_by_id, is_ip_unique, update_camera
from app.utils import is_valid_ip, validate_rtsp
from .camera import get_camera_stream
from .globals import camera_list, face_data, camera_refresh_lock, reload_camera_data, skip_detection_flags

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', cameras=camera_list)

@main.route("/toggle-detection/<camera_id>", methods=["POST"])
def toggle_detection(camera_id):
    if camera_id not in skip_detection_flags:
        return jsonify({"error": "Invalid camera ID"}), 404

    skip_detection_flags[camera_id] = not skip_detection_flags[camera_id]
    status = "disabled" if skip_detection_flags[camera_id] else "enabled"
    return jsonify({
        "camera_id": camera_id,
        "detection": status
    }), 200

@main.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    if camera_id not in camera_list:
        flash("Camera not found.", "danger")
        return "Camera not found", 404
    return Response(get_camera_stream(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/cameras', methods=['GET'])
def cameras():
    cameras = get_all_cameras()
    return render_template('cameras.html', cameras=cameras)

@main.route('/logs', methods=['GET'])
def logs_dashboard():
    page = int(request.args.get('page', 1))
    per_page = 20
    page_window = 3  # Number of pages to show around current

    logs = get_all_logs_embeddings()
    grouped_logs = {}
    known_count = sum(1 for log in logs if log["name"] != "Unknown")
    unknown_count = len(logs) - known_count

    for log in logs:
        name = log["name"]
        if name not in grouped_logs:
            grouped_logs[name] = {
                "count": 0,
                "snapshot": log["snapshot"],
                "latest_timestamp": log["timestamp"]
            }
        grouped_logs[name]["count"] += 1

    sorted_grouped = sorted(grouped_logs.items(), key=lambda x: x[1]["latest_timestamp"], reverse=True)

    total_grouped = len(sorted_grouped)
    total_pages = max(math.ceil(total_grouped / per_page), 1)

    # Clamp current page
    page = max(1, min(page, total_pages))

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated_grouped = sorted_grouped[start:end]

    # Pagination window logic
    start_page = max(1, page - page_window)
    end_page = min(total_pages, page + page_window)

    return render_template("logs_grouped.html",
                           logs=logs,
                           known_count=known_count,
                           unknown_count=unknown_count,
                           grouped_logs=paginated_grouped,
                           page=page,
                           total_pages=total_pages,
                           start_page=start_page,
                           end_page=end_page,
                           page_window=page_window)

@main.route('/logs/<name>', methods=['GET'])
def logs_by_name(name):
    page = int(request.args.get('page', 1))
    per_page = 20
    page_window = 3  # How many pages to show around current

    logs = get_all_logs_embeddings()
    filtered_logs = [log for log in logs if log['name'] == name]
    total_logs = len(filtered_logs)
    total_pages = max(math.ceil(total_logs / per_page), 1)

    # Clamp current page
    page = max(1, min(page, total_pages))

    # Pagination logic
    start = (page - 1) * per_page
    end = start + per_page
    paginated_logs = filtered_logs[start:end]

    start_item = start + 1 if total_logs > 0 else 0
    end_item = min(end, total_logs)

    # Pagination window logic
    start_page = max(1, page - page_window)
    end_page = min(total_pages, page + page_window)

    return render_template(
        "logs_by_name.html",
        logs=paginated_logs,
        name=name,
        page=page,
        total_pages=total_pages,
        start_item=start_item,
        end_item=end_item,
        total_logs=total_logs,
        start_page=start_page,
        end_page=end_page,
        page_window=page_window
    )

@main.route('/add_camera', methods=['POST'])
def add_camera_route():
    name = request.form['name']
    ip = request.form['ip']
    stream = request.form['stream']
    username = request.form['username']
    password = request.form['password']

    if not is_valid_ip(ip):
        flash("Invalid IP address format.", "danger")
        return redirect('/cameras')

    if not is_ip_unique(ip):
        flash("IP address already exists.", "danger")
        return redirect('/cameras')

    add_camera(name, ip, username, password, stream)
    flash("Camera added successfully!", "success")
    return redirect('/cameras')

@main.route('/validate_camera/<int:camera_id>', methods=['GET'])
def validate_camera(camera_id):
    cameras = get_all_cameras()
    camera = next((c for c in cameras if c[0] == camera_id), None)
    if camera:
        try:
            success = validate_rtsp(camera[2], camera_id)
            return jsonify(success=success)
        except Exception as e:
            return jsonify(success=False, message=str(e))
    else:
        return jsonify(success=False, message="Camera not found")

@main.route('/delete_camera/<int:id>', methods=['POST'])
def delete_camera_route(id):
    try:
        # Delete the camera from the database
        delete_camera(id)
        reload_camera_data()
        # Provide feedback to the user
        flash("Camera deleted successfully.", "success")
        return jsonify({'message': 'Camera deleted successfully'})
    
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return jsonify({'message': f"Error: {str(e)}"}), 500

@main.route('/edit_camera/<int:id>', methods=['POST'])
def edit_camera(id):
    name = request.form['name']
    ip = request.form['ip']
    username = request.form['username']
    password = request.form['password']
    stream = request.form['stream']
    
    try:
        update_camera(id, name, ip, username, password, stream)
        reload_camera_data()
        flash("Camera updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect('/cameras')

# Define the Camera named tuple
Camera = namedtuple('Camera', ['id', 'name', 'ip', 'username', 'password', 'stream', 'rtsp_url', 'working'])

@main.route('/get_camera/<int:id>')
def get_camera(id):
    camera = get_camera_by_id(id)
    if camera:
        camera_data = Camera(*camera)
        return jsonify({
            'id': camera_data.id,
            'name': camera_data.name,
            'ip': camera_data.ip,
            'username': camera_data.username,
            'password': camera_data.password,
            'rtsp_url': camera_data.rtsp_url,
            'stream': camera_data.stream,
            'working': bool(camera_data.working)
        })
    else:
        flash("Camera not found.", "danger")
        return jsonify({'error': 'Camera not found'}), 404

@main.route("/camera_stats/<camera_id>")
def camera_stats(camera_id):
    data = face_data.get(camera_id, {"count": 0, "confidences": []})
    # Ensure confidences are native Python floats
    data["confidences"] = [float(c) for c in data.get("confidences", [])]
    
    return jsonify(data)

@main.route('/refresh_cameras', methods=['GET'])
def refresh_cameras():
    try:
        # Acquire the global refresh lock
        with camera_refresh_lock:
            # Reload the camera data
            reload_camera_data()
        flash("Refreshed Successfully", "success")
        return jsonify({'success': True})

    except Exception as e:
        print(f"Error during camera refresh: {e}")
        flash("Camera not found.", "danger")
        return jsonify({'success': False, 'error': str(e)})
    

