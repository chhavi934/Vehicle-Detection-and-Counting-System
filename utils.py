import cv2
import logging
import os
import numpy as np
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_video_source(source):
    """
    Open a video source (file, camera, URL)
    
    Args:
        source: Video source (file path, camera index, or URL)
        
    Returns:
        OpenCV VideoCapture object
    """
    # Check if source is an integer (camera index)
    if isinstance(source, int):
        logger.info(f"Opening camera with index {source}")
        return cv2.VideoCapture(source)
    
    # Check if source is a URL
    try:
        parsed_url = urlparse(source)
        if parsed_url.scheme in ['http', 'https', 'rtsp', 'rtmp']:
            logger.info(f"Opening video stream from URL: {source}")
            return cv2.VideoCapture(source)
    except:
        pass
    
    # Check if source is a file
    if isinstance(source, str) and os.path.isfile(source):
        logger.info(f"Opening video file: {source}")
        return cv2.VideoCapture(source)
    
    # Default to camera 0 if source is invalid
    logger.warning(f"Could not identify source type for {source}, defaulting to camera 0")
    return cv2.VideoCapture(0)

def download_yolo_files():
    """
    Download YOLO model files if not available
    
    Note: This function requires an internet connection
    """
    import urllib.request
    
    files = {
        "yolov3-tiny.weights": "https://pjreddie.com/media/files/yolov3-tiny.weights",
        "yolov3-tiny.cfg": "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg",
        "coco.names": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"
    }
    
    for filename, url in files.items():
        if not os.path.exists(filename):
            try:
                logger.info(f"Downloading {filename}...")
                urllib.request.urlretrieve(url, filename)
                logger.info(f"Downloaded {filename} successfully")
            except Exception as e:
                logger.error(f"Error downloading {filename}: {str(e)}")

def create_unique_colors(num_colors):
    """
    Create unique colors for visualization
    
    Args:
        num_colors: Number of colors to generate
        
    Returns:
        List of colors as (B, G, R) tuples
    """
    colors = []
    for i in range(num_colors):
        # Use HSV color space to generate evenly distributed colors
        hue = i / num_colors * 360
        saturation = 100
        value = 100
        
        # Convert HSV to BGR
        h = hue / 2
        s = saturation / 100
        v = value / 100
        
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r, g, b = (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
        colors.append((b, g, r))  # OpenCV uses BGR
    
    return colors

def calculate_iou(box1, box2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes
    
    Args:
        box1: First bounding box [x, y, w, h]
        box2: Second bounding box [x, y, w, h]
        
    Returns:
        IoU value between 0 and 1
    """
    # Convert to [x1, y1, x2, y2] format
    x1_1, y1_1 = box1[0], box1[1]
    x2_1, y2_1 = box1[0] + box1[2], box1[1] + box1[3]
    
    x1_2, y1_2 = box2[0], box2[1]
    x2_2, y2_2 = box2[0] + box2[2], box2[1] + box2[3]
    
    # Calculate area of each box
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    # Calculate intersection area
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i <= x1_i or y2_i <= y1_i:
        return 0.0  # No intersection
    
    intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union area
    union_area = area1 + area2 - intersection_area
    
    # Calculate IoU
    iou = intersection_area / union_area
    
    return iou
