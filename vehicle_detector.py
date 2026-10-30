import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VehicleDetector:
    def __init__(self, min_area=500, history=500, threshold=400):
        """
        Initialize the vehicle detector with background subtraction
        
        Args:
            min_area: Minimum contour area to be considered as a vehicle
            history: History parameter for background subtractor
            threshold: Threshold for detecting foreground
        """
        self.min_area = min_area
        # Initialize background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history, 
            varThreshold=threshold, 
            detectShadows=False
        )
        
        # Load YOLO weights and configuration if available
        try:
            # Load YOLO model - using a smaller YOLO model for better performance
            self.net = cv2.dnn.readNetFromDarknet(
                "yolov3-tiny.cfg", 
                "yolov3-tiny.weights"
            )
            self.use_yolo = True
            
            # Load COCO class labels
            with open("coco.names", "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
                
            # Vehicle classes in COCO dataset
            self.vehicle_classes = ["car", "motorcycle", "bus", "truck", "bicycle"]
            
            # Get output layer names
            layer_names = self.net.getLayerNames()
            try:
                self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers().flatten()]
            except:
                self.output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
                
            logger.info("YOLO model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Could not load YOLO model, using only background subtraction: {str(e)}")
            self.use_yolo = False
    
    def detect(self, frame):
        """
        Detect vehicles in the frame using background subtraction and/or YOLO
        
        Args:
            frame: Input frame from video
            
        Returns:
            List of detected vehicles with [x, y, w, h, vehicle_type]
        """
        detected_vehicles = []
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Apply morphological operations to remove noise
        kernel = np.ones((5, 5), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour as a potential vehicle
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by minimum area
            if area >= self.min_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Simple vehicle type classification based on aspect ratio and size
                aspect_ratio = float(w) / h
                
                if aspect_ratio < 0.6:
                    vehicle_type = "motorcycle"
                elif aspect_ratio < 1.0:
                    vehicle_type = "car" if area < 4000 else "bus"
                else:
                    vehicle_type = "truck" if area > 3000 else "car"
                
                detected_vehicles.append([x, y, w, h, vehicle_type])
        
        # Use YOLO for additional detection if available
        if self.use_yolo:
            try:
                height, width, _ = frame.shape
                
                # Prepare image for YOLO
                blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
                self.net.setInput(blob)
                
                # Run detection
                outputs = self.net.forward(self.output_layers)
                
                # Process YOLO detection results
                for output in outputs:
                    for detection in output:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        
                        # Only consider vehicle classes with confidence > 0.5
                        if self.classes[class_id] in self.vehicle_classes and confidence > 0.5:
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)
                            
                            # Calculate top-left corner coordinates
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)
                            
                            vehicle_type = self.classes[class_id]
                            detected_vehicles.append([x, y, w, h, vehicle_type])
            
            except Exception as e:
                logger.error(f"Error in YOLO detection: {str(e)}")
                
        return detected_vehicles
    
    def draw_detections(self, frame, vehicles):
        """
        Draw bounding boxes and labels for detected vehicles
        
        Args:
            frame: Input frame
            vehicles: List of tracked vehicles [id, x, y, w, h, vehicle_type]
            
        Returns:
            Frame with annotations
        """
        for vehicle in vehicles:
            # Extract vehicle data
            if len(vehicle) == 6:
                vehicle_id, x, y, w, h, vehicle_type = vehicle
            else:
                # Handle case where vehicle_id is not provided
                x, y, w, h, vehicle_type = vehicle
                vehicle_id = 0
                
            # Define colors for different vehicle types
            color_map = {
                "car": (0, 255, 0),       # Green
                "truck": (0, 0, 255),     # Red
                "motorcycle": (255, 0, 0), # Blue
                "bus": (255, 255, 0),     # Cyan
                "bicycle": (255, 0, 255)  # Magenta
            }
            
            color = color_map.get(vehicle_type, (255, 255, 255))  # Default to white if type not found
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Add vehicle ID and type
            label = f"ID: {vehicle_id}, {vehicle_type}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        return frame
