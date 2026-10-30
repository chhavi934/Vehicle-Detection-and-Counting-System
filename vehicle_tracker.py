import numpy as np
import logging
from scipy.spatial import distance

logger = logging.getLogger(__name__)

class VehicleTracker:
    def __init__(self, distance_threshold=50, max_frames_to_skip=10):
        """
        Initialize the vehicle tracker
        
        Args:
            distance_threshold: Maximum distance for matching detections to existing tracks
            max_frames_to_skip: Maximum number of frames to keep a track alive without detection
        """
        self.distance_threshold = distance_threshold
        self.max_frames_to_skip = max_frames_to_skip
        self.next_track_id = 1
        self.tracks = {}  # Dictionary to store active tracks {id: [x, y, w, h, vehicle_type, frames_skipped]}
    
    def update(self, detections):
        """
        Update tracks with new detections
        
        Args:
            detections: List of detected vehicles [x, y, w, h, vehicle_type]
            
        Returns:
            List of tracked vehicles [id, x, y, w, h, vehicle_type]
        """
        # If no tracks exist yet, initialize with all detections
        if len(self.tracks) == 0:
            for detection in detections:
                x, y, w, h, vehicle_type = detection
                self.tracks[self.next_track_id] = [x, y, w, h, vehicle_type, 0]  # Last value is frames_skipped
                self.next_track_id += 1
        else:
            # Calculate centroids of existing tracks and new detections
            track_centroids = {}
            for track_id, track_info in self.tracks.items():
                x, y, w, h = track_info[:4]
                track_centroids[track_id] = (x + w//2, y + h//2)
                
            detection_centroids = []
            for detection in detections:
                x, y, w, h = detection[:4]
                detection_centroids.append((x + w//2, y + h//2))
                
            # Create distance matrix between tracks and detections
            distance_matrix = np.zeros((len(self.tracks), len(detections)))
            for i, track_id in enumerate(self.tracks.keys()):
                for j, det_centroid in enumerate(detection_centroids):
                    distance_matrix[i, j] = distance.euclidean(track_centroids[track_id], det_centroid)
            
            # Match tracks to detections using greedy algorithm
            assigned_tracks = set()
            assigned_detections = set()
            
            # While there are unassigned tracks and detections
            while True:
                # Find minimum distance
                if distance_matrix.size == 0 or np.min(distance_matrix) > self.distance_threshold:
                    break
                    
                # Get indices of minimum distance
                track_idx, det_idx = np.unravel_index(np.argmin(distance_matrix), distance_matrix.shape)
                
                # Get track_id from index
                track_id = list(self.tracks.keys())[track_idx]
                
                # If distance is below threshold, assign detection to track
                if distance_matrix[track_idx, det_idx] <= self.distance_threshold:
                    # Update track with new detection
                    x, y, w, h, vehicle_type = detections[det_idx]
                    self.tracks[track_id] = [x, y, w, h, vehicle_type, 0]  # Reset frames_skipped
                    
                    assigned_tracks.add(track_idx)
                    assigned_detections.add(det_idx)
                
                # Set this distance to infinity to avoid reassignment
                distance_matrix[track_idx, det_idx] = float('inf')
                
                # If all tracks or detections are assigned, break
                if len(assigned_tracks) == len(self.tracks) or len(assigned_detections) == len(detections):
                    break
            
            # Handle unassigned detections (new tracks)
            for i, detection in enumerate(detections):
                if i not in assigned_detections:
                    x, y, w, h, vehicle_type = detection
                    self.tracks[self.next_track_id] = [x, y, w, h, vehicle_type, 0]
                    self.next_track_id += 1
            
            # Handle unassigned tracks (increment frames_skipped)
            tracks_to_delete = []
            for i, track_id in enumerate(list(self.tracks.keys())):
                if i not in assigned_tracks:
                    # Increment frames_skipped
                    self.tracks[track_id][5] += 1
                    
                    # If track hasn't been seen for too long, mark for deletion
                    if self.tracks[track_id][5] > self.max_frames_to_skip:
                        tracks_to_delete.append(track_id)
            
            # Delete tracks that haven't been seen for too long
            for track_id in tracks_to_delete:
                del self.tracks[track_id]
        
        # Convert tracks to list format [id, x, y, w, h, vehicle_type]
        tracked_vehicles = []
        for track_id, track_info in self.tracks.items():
            x, y, w, h, vehicle_type, _ = track_info
            tracked_vehicles.append([track_id, x, y, w, h, vehicle_type])
            
        return tracked_vehicles
