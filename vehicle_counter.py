import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class VehicleCounter:
    def __init__(self, line_position=0.5):
        """
        Initialize the vehicle counter
        
        Args:
            line_position: Relative position of the counting line (0-1)
        """
        self.line_position = line_position
        self.frame_width = None
        self.frame_height = None
        
        # Store vehicle counts
        self.vehicle_counts = {
            'car': 0,
            'truck': 0,
            'motorcycle': 0,
            'bus': 0,
            'total': 0
        }
        
        # Track which vehicles have already been counted
        self.counted_vehicles = set()
        
    def set_frame_dimensions(self, width, height):
        """
        Set the frame dimensions for calculating the counting line position
        
        Args:
            width: Frame width
            height: Frame height
        """
        self.frame_width = width
        self.frame_height = height
        
        # Calculate counting line y-position
        self.counting_line_y = int(self.frame_height * self.line_position)
        
        # Define detection zones (enter and exit zones)
        zone_height = int(self.frame_height * 0.1)  # 10% of frame height
        
        self.entry_zone = (0, self.counting_line_y - zone_height, 
                           self.frame_width, self.counting_line_y)
        
        self.exit_zone = (0, self.counting_line_y, 
                          self.frame_width, self.counting_line_y + zone_height)
        
        logger.debug(f"Counter initialized with dimensions: {width}x{height}")
        logger.debug(f"Counting line at y={self.counting_line_y}")
        logger.debug(f"Entry zone: {self.entry_zone}")
        logger.debug(f"Exit zone: {self.exit_zone}")
        
    def count_vehicles(self, tracked_vehicles, frame):
        """
        Count vehicles crossing the counting line
        
        Args:
            tracked_vehicles: List of tracked vehicles [id, x, y, w, h, vehicle_type]
            frame: Current video frame
            
        Returns:
            Dictionary of new vehicle counts in this frame
        """
        if self.frame_width is None or self.frame_height is None:
            logger.warning("Frame dimensions not set. Call set_frame_dimensions first.")
            return {'car': 0, 'truck': 0, 'motorcycle': 0, 'bus': 0}
        
        # Initialize counts for this frame
        frame_counts = {
            'car': 0,
            'truck': 0,
            'motorcycle': 0,
            'bus': 0
        }
        
        for vehicle in tracked_vehicles:
            vehicle_id, x, y, w, h, vehicle_type = vehicle
            
            # Calculate bottom center point of the vehicle
            vehicle_center_x = x + w // 2
            vehicle_bottom = y + h
            
            # Check if the vehicle has crossed the counting line (from top to bottom)
            if self.counting_line_y < vehicle_bottom and self.counting_line_y > y:
                if vehicle_id not in self.counted_vehicles:
                    # Count this vehicle
                    if vehicle_type in self.vehicle_counts:
                        self.vehicle_counts[vehicle_type] += 1
                        frame_counts[vehicle_type] += 1
                    else:
                        # Default to car if type not recognized
                        self.vehicle_counts['car'] += 1
                        frame_counts['car'] += 1
                    
                    # Update total count
                    self.vehicle_counts['total'] += 1
                    
                    # Mark as counted
                    self.counted_vehicles.add(vehicle_id)
                    
                    # Draw a line to show vehicle has been counted
                    cv2.line(frame, (x, vehicle_bottom), (x + w, vehicle_bottom), (0, 255, 255), 2)
                    
                    logger.debug(f"Counted vehicle ID {vehicle_id} of type {vehicle_type}")
        
        return frame_counts
    
    def draw_detection_zones(self, frame):
        """
        Draw counting line and detection zones on the frame
        
        Args:
            frame: Current video frame
            
        Returns:
            Frame with detection zones drawn
        """
        if self.frame_width is None or self.frame_height is None:
            return frame
        
        # Draw counting line
        cv2.line(frame, (0, self.counting_line_y), (self.frame_width, self.counting_line_y), 
                 (255, 0, 0), 2)
        
        # Draw entry zone (semi-transparent overlay)
        overlay = frame.copy()
        cv2.rectangle(overlay, (self.entry_zone[0], self.entry_zone[1]), 
                      (self.entry_zone[2], self.entry_zone[3]), (0, 255, 0), -1)
        
        # Draw exit zone (semi-transparent overlay)
        cv2.rectangle(overlay, (self.exit_zone[0], self.exit_zone[1]), 
                      (self.exit_zone[2], self.exit_zone[3]), (0, 0, 255), -1)
        
        # Apply transparency
        alpha = 0.3
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Add labels
        cv2.putText(frame, "Counting Line", (10, self.counting_line_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Add count information
        y_pos = self.frame_height - 120
        cv2.putText(frame, f"Count Statistics:", (self.frame_width - 250, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Cars: {self.vehicle_counts['car']}", (self.frame_width - 250, y_pos + 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Trucks: {self.vehicle_counts['truck']}", (self.frame_width - 250, y_pos + 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.putText(frame, f"Motorcycles: {self.vehicle_counts['motorcycle']}", (self.frame_width - 250, y_pos + 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        return frame
    
    def get_counts(self):
        """
        Get the current vehicle counts
        
        Returns:
            Dictionary of vehicle counts
        """
        return self.vehicle_counts
