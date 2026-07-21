"""
Time-bucketing module for aggregating high-frequency sensor data (10-100Hz) 
into 2-second windows with statistical features (mean, max, rate-of-change).
"""

from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
from schemas import TimeBucketedData


class TimeBucketAggregator:
    """
    Aggregates raw high-frequency sensor data into fixed 2-second time windows.
    
    Input: Raw sensor readings at 10-100Hz
    Output: TimeBucketedData with mean, max, min, rate_of_change per 2-second window
    """
    
    def __init__(self, window_seconds: float = 2.0):
        self.window_seconds = window_seconds
        self.buffers: Dict[str, deque] = defaultdict(deque)
        self.last_values: Dict[str, float] = {}
        
    def add_reading(self, sensor_id: str, value: float, timestamp: datetime) -> None:
        """
        Add a raw sensor reading to the appropriate time bucket.
        
        Args:
            sensor_id: Unique identifier for the sensor
            value: Raw sensor reading
            timestamp: When the reading was taken
        """
        self.buffers[sensor_id].append((timestamp, value))
        
    def get_completed_buckets(self, current_time: datetime) -> List[TimeBucketedData]:
        """
        Extract all completed 2-second time buckets from the buffers.
        
        Args:
            current_time: Current timestamp for determining completed windows
            
        Returns:
            List of TimeBucketedData objects for completed windows
        """
        completed_buckets = []
        cutoff_time = current_time - timedelta(seconds=self.window_seconds)
        
        for sensor_id, buffer in self.buffers.items():
            # Group readings into proper 2-second windows
            # Sort buffer by timestamp
            sorted_readings = sorted(buffer, key=lambda x: x[0])
            
            # Find the window start for the first reading
            if not sorted_readings:
                continue
            
            # Process readings in 2-second windows
            i = 0
            while i < len(sorted_readings):
                timestamp, value = sorted_readings[i]
                
                # Skip readings that are still in the current (incomplete) window
                if timestamp >= cutoff_time:
                    i += 1
                    continue
                
                # Calculate window start (floor to 2-second boundary)
                window_start = datetime.fromtimestamp(
                    (timestamp.timestamp() // self.window_seconds) * self.window_seconds
                )
                window_end = window_start + timedelta(seconds=self.window_seconds)
                
                # Collect all readings in this window
                window_readings = []
                while i < len(sorted_readings) and sorted_readings[i][0] < window_end:
                    # Only include readings that are before cutoff_time (completed windows)
                    if sorted_readings[i][0] < cutoff_time:
                        window_readings.append(sorted_readings[i])
                    i += 1
                
                if window_readings:
                    # Sort by timestamp
                    window_readings.sort(key=lambda x: x[0])
                    actual_window_start = window_readings[0][0]
                    actual_window_end = window_readings[-1][0]
                    
                    values = [v for _, v in window_readings]
                    
                    # Calculate statistics
                    mean_value = statistics.mean(values)
                    max_value = max(values)
                    min_value = min(values)
                    
                    # Calculate rate of change (slope)
                    if len(window_readings) >= 2:
                        first_val = window_readings[0][1]
                        last_val = window_readings[-1][1]
                        time_diff = (actual_window_end - actual_window_start).total_seconds()
                        rate_of_change = (last_val - first_val) / time_diff if time_diff > 0 else 0.0
                    else:
                        rate_of_change = 0.0
                    
                    bucket = TimeBucketedData(
                        sensor_id=sensor_id,
                        window_start=actual_window_start,
                        window_end=actual_window_end,
                        mean_value=mean_value,
                        max_value=max_value,
                        min_value=min_value,
                        rate_of_change=rate_of_change,
                        sample_count=len(window_readings)
                    )
                    completed_buckets.append(bucket)
                    
                    # Update last value for next window's rate calculation
                    self.last_values[sensor_id] = values[-1]
            
            # Remove processed readings from buffer
            self.buffers[sensor_id] = deque(
                [(ts, val) for ts, val in sorted_readings if ts >= cutoff_time]
            )
        
        return completed_buckets
    
    def get_current_window_stats(self, sensor_id: str, current_time: datetime) -> Optional[TimeBucketedData]:
        """
        Get statistics for the current (potentially incomplete) time window.
        
        Args:
            sensor_id: Sensor identifier
            current_time: Current timestamp
            
        Returns:
            TimeBucketedData for current window, or None if no data
        """
        if sensor_id not in self.buffers or not self.buffers[sensor_id]:
            return None
            
        window_start = current_time - timedelta(seconds=self.window_seconds)
        window_readings = [
            (ts, val) for ts, val in self.buffers[sensor_id]
            if ts >= window_start
        ]
        
        if not window_readings:
            return None
            
        window_readings.sort(key=lambda x: x[0])
        values = [v for _, v in window_readings]
        
        mean_value = statistics.mean(values)
        max_value = max(values)
        min_value = min(values)
        
        if len(window_readings) >= 2:
            first_val = window_readings[0][1]
            last_val = window_readings[-1][1]
            time_diff = (window_readings[-1][0] - window_readings[0][0]).total_seconds()
            rate_of_change = (last_val - first_val) / time_diff if time_diff > 0 else 0.0
        else:
            rate_of_change = 0.0
        
        return TimeBucketedData(
            sensor_id=sensor_id,
            window_start=window_readings[0][0],
            window_end=window_readings[-1][0],
            mean_value=mean_value,
            max_value=max_value,
            min_value=min_value,
            rate_of_change=rate_of_change,
            sample_count=len(window_readings)
        )
    
    def clear_buffer(self, sensor_id: str) -> None:
        """Clear all buffered data for a specific sensor."""
        if sensor_id in self.buffers:
            self.buffers[sensor_id].clear()
    
    def clear_all_buffers(self) -> None:
        """Clear all buffered data."""
        self.buffers.clear()
        self.last_values.clear()
