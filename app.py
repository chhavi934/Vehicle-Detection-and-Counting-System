import os
import logging
import cv2
import tempfile
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, Response, jsonify, send_file, redirect, url_for, session, flash
from vehicle_detector import VehicleDetector
from vehicle_tracker import VehicleTracker
from vehicle_counter import VehicleCounter
from utils import get_video_source

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Global variables
detector = None
tracker = None
counter = None
video_source = None
output_file = None
is_processing = False
frame_count = 0
total_vehicles = 0
stats = {
    'car': 0,
    'truck': 0,
    'motorcycle': 0,
    'bus': 0,
    'total': 0
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    global video_source, detector, tracker, counter, is_processing, output_file, stats
    
    # Reset statistics
    stats = {
        'car': 0,
        'truck': 0,
        'motorcycle': 0,
        'bus': 0,
        'total': 0
    }
    
    # Check if using camera or file upload
    source_type = request.form.get('source_type')
    
    if source_type == 'camera':
        camera_id = request.form.get('camera_id', '0')
        try:
            camera_id = int(camera_id)
        except ValueError:
            # If not an integer, assume it's a URL or path
            pass
        video_source = camera_id
    else:
        # Handle file upload
        if 'video' not in request.files:
            flash('No video file uploaded')
            return redirect(request.url)
            
        video_file = request.files['video']
        if video_file.filename == '':
            flash('No video file selected')
            return redirect(request.url)
            
        # Save uploaded file to temporary location
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        video_file.save(temp_file.name)
        video_source = temp_file.name
    
    # Configuration parameters from form
    min_area = int(request.form.get('min_area', 500))
    detection_line_position = float(request.form.get('detection_line', 0.5))
    
    # Initialize detector, tracker and counter
    detector = VehicleDetector(min_area=min_area)
    tracker = VehicleTracker()
    counter = VehicleCounter(line_position=detection_line_position)
    
    # Create CSV output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"vehicle_counts_{timestamp}.csv"
    
    # Set processing flag
    is_processing = True
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    global is_processing
    if not is_processing:
        return redirect(url_for('index'))
    return render_template('results.html')

def generate_frames():
    global video_source, detector, tracker, counter, is_processing, frame_count, total_vehicles, stats, output_file
    
    # Open video source
    cap = get_video_source(video_source)
    
    if not cap.isOpened():
        logger.error(f"Error: Could not open video source {video_source}")
        is_processing = False
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n'
               b'Error: Could not open video source\r\n\r\n')
        return
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Initialize counter with frame dimensions
    counter.set_frame_dimensions(frame_width, frame_height)
    
    # CSV data
    csv_data = []
    
    frame_count = 0
    total_vehicles = 0
    
    try:
        while cap.isOpened() and is_processing:
            success, frame = cap.read()
            if not success:
                break
                
            frame_count += 1
            
            # Detect vehicles
            detected_vehicles = detector.detect(frame)
            
            # Track vehicles
            tracked_vehicles = tracker.update(detected_vehicles)
            
            # Count vehicles
            vehicle_counts = counter.count_vehicles(tracked_vehicles, frame)
            
            # Update statistics
            for vehicle_type, count in vehicle_counts.items():
                if vehicle_type in stats:
                    stats[vehicle_type] += count
            
            stats['total'] = sum([stats[k] for k in stats if k != 'total'])
            total_vehicles = stats['total']
            
            # Prepare CSV data
            if frame_count % int(fps) == 0:  # Record data each second
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_data.append({
                    'timestamp': timestamp,
                    'frame_count': frame_count,
                    'total_vehicles': total_vehicles,
                    'cars': stats['car'],
                    'trucks': stats['truck'],
                    'motorcycles': stats['motorcycle'],
                    'buses': stats['bus']
                })
                
                # Save CSV periodically
                df = pd.DataFrame(csv_data)
                df.to_csv(output_file, index=False)
            
            # Draw detection zones and vehicle information
            frame = counter.draw_detection_zones(frame)
            frame = detector.draw_detections(frame, tracked_vehicles)
            
            # Add text with statistics
            cv2.putText(frame, f"Total Vehicles: {total_vehicles}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Cars: {stats['car']}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Trucks: {stats['truck']}", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Motorcycles: {stats['motorcycle']}", (10, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Buses: {stats['bus']}", (10, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
    except Exception as e:
        logger.error(f"Error in video processing: {str(e)}")
    finally:
        # Final CSV save
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(output_file, index=False)
            
        # Clean up
        cap.release()
        is_processing = False

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stats')
def get_stats():
    global stats, total_vehicles, frame_count
    return jsonify({
        'stats': stats,
        'total_vehicles': total_vehicles,
        'frame_count': frame_count,
        'is_processing': is_processing
    })

@app.route('/stop_processing')
def stop_processing():
    global is_processing
    is_processing = False
    return jsonify({'status': 'stopped'})

@app.route('/download_csv')
def download_csv():
    global output_file
    if output_file and os.path.exists(output_file):
        return send_file(output_file, as_attachment=True, download_name=os.path.basename(output_file))
    else:
        flash('No data available for download')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
