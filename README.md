# 🚗 Vehicle Detection and Counting System

A real-time vehicle detection, tracking, and counting web application built with Python, Flask, and OpenCV. The system can process video files or live camera feeds to detect and count vehicles by type — cars, trucks, motorcycles, and buses — and export the results as a CSV report.

---

## 📸 Features

- 🎥 **Real-time video processing** — supports uploaded video files and live camera feeds
- 🔍 **Vehicle detection** — detects cars, trucks, motorcycles, and buses using OpenCV
- 📍 **Vehicle tracking** — tracks vehicles across frames with unique IDs
- 📊 **Live statistics** — displays counts per vehicle type updated in real time
- 📈 **Configurable detection line** — set the counting line position as a percentage of frame height
- 💾 **CSV export** — download timestamped vehicle count data as a CSV file
- 🖥️ **Web interface** — clean browser-based UI built with Flask and Bootstrap

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, Flask 3.1 |
| Computer Vision | OpenCV 4.11, NumPy, SciPy |
| Data | Pandas |
| Frontend | HTML, CSS, JavaScript |
| Server | Gunicorn |
| Package Manager | uv |

---

## 📁 Project Structure

```
Vehicle-Detection-and-Counting-System/
├── app.py                  # Main Flask application & routes
├── vehicle_detector.py     # Vehicle detection logic (OpenCV)
├── vehicle_tracker.py      # Vehicle tracking across frames
├── vehicle_counter.py      # Counting logic with detection line
├── Vehicle.py              # Vehicle data model
├── utils.py                # Helper utilities (video source handling)
├── main.py                 # Entry point
├── pyproject.toml          # Project dependencies
├── uv.lock                 # Dependency lock file
├── static/
│   ├── css/custom.css      # Custom styles
│   └── js/app.js           # Frontend JavaScript
└── templates/
    ├── layout.html         # Base HTML layout
    ├── index.html          # Upload / home page
    └── results.html        # Live results & video feed page
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`

### 1. Clone the Repository

```bash
git clone https://github.com/chhavi934/Vehicle-Detection-and-Counting-System.git
cd Vehicle-Detection-and-Counting-System
```

### 2. Install Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install flask opencv-python numpy pandas scipy gunicorn
```

### 3. Run the Application

```bash
python main.py
```

Or using Gunicorn (production):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. Open in Browser

```
http://localhost:5000
```

---

## 🚀 Usage

1. Open the web app in your browser at `http://localhost:5000`
2. Choose your video source:
   - **Upload a video file** (MP4, AVI, etc.)
   - **Use a live camera** (enter camera ID, default: `0`)
3. Configure detection settings:
   - **Minimum area** — filter small detections (default: 500 px²)
   - **Detection line position** — set counting line height (0.0 to 1.0)
4. Click **Start Processing**
5. View real-time vehicle counts on the results page
6. Click **Download CSV** to export the count data

---

## 📊 CSV Output

The exported CSV contains the following columns:

| Column | Description |
|--------|-------------|
| `timestamp` | Date and time of the record |
| `frame_count` | Frame number in the video |
| `total_vehicles` | Cumulative total vehicle count |
| `cars` | Count of cars |
| `trucks` | Count of trucks |
| `motorcycles` | Count of motorcycles |
| `buses` | Count of buses |

---

## 🔧 Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_area` | `500` | Minimum contour area (pixels²) to consider as a vehicle |
| `detection_line` | `0.5` | Vertical position of counting line (0 = top, 1 = bottom) |
| `SESSION_SECRET` | env var | Flask session secret key |
| Port | `5000` | Application port (configurable in `main.py`) |

---

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home/upload page |
| `/upload` | POST | Submit video source and start processing |
| `/results` | GET | Live results page |
| `/video_feed` | GET | MJPEG video stream |
| `/stats` | GET | JSON with current vehicle counts |
| `/stop_processing` | GET | Stop video processing |
| `/download_csv` | GET | Download CSV report |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Chhavi Tomar**  
GitHub: [@chhavi934](https://github.com/chhavi934)
