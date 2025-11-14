from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from plyer import accelerometer, gps
from kivy.utils import platform
import requests
import time
import math

FIREBASE_URL = "https://accelerometer-for-potholes-default-rtdb.firebaseio.com/data.json"

# Filter constants
ALPHA_LPF = 0.8
ALPHA_HPF = 0.8
BASELINE_SAMPLES = 10

class AccelApp(App):
    def build(self):
        self.label = Label(text="Initializing sensors...", font_size='18sp')
        
        # Initialize variables
        self.baseline_z = 9.8
        self.filtered_z = 9.8
        self.hpf_z = 0
        self.last_z = 0
        self.baseline_window = []
        
        # GPS variables
        self.current_lat = 0
        self.current_lon = 0
        self.last_location = None
        self.speed = 0
        self.gps_enabled = False
        self.readings_since_reset = 0
        
        # Start sensors
        self.start_accelerometer()
        self.start_gps()
        
        # Update display every 0.5 seconds
        Clock.schedule_interval(self.update, 0.5)
        return self.label
    
    def start_accelerometer(self):
        """Initialize accelerometer with error handling"""
        try:
            accelerometer.enable()
            self.label.text = "Accelerometer enabled"
        except Exception as e:
            self.label.text = f"Accelerometer error: {e}"
            print(f"Accelerometer error: {e}")
    
    def start_gps(self):
        """Initialize GPS with proper permissions and error handling"""
        if platform == 'android':
            try:
                # Request Android permissions
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION
                ])
                
                # Configure and start GPS
                gps.configure(on_location=self.on_location, on_status=self.on_status)
                gps.start(minTime=1000, minDistance=0)
                self.gps_enabled = True
                self.label.text = "GPS starting..."
                print("GPS configured and started")
                
            except Exception as e:
                self.label.text = f"GPS setup failed: {e}"
                print(f"GPS error: {e}")
                self.gps_enabled = False
        else:
            self.label.text = "GPS only available on Android\nAccelerometer active"
            self.gps_enabled = False
    
    def on_location(self, **kwargs):
        """Called when GPS location updates"""
        try:
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            
            if lat is None or lon is None:
                print("Invalid GPS data received")
                return
            
            self.current_lat = lat
            self.current_lon = lon
            
            # Calculate speed if we have a previous location
            if self.last_location:
                lat1, lon1, t1 = self.last_location
                lat2, lon2, t2 = self.current_lat, self.current_lon, time.time()
                
                # Calculate distance using haversine formula
                distance = self.haversine(lat1, lon1, lat2, lon2)
                time_diff = t2 - t1
                
                if time_diff > 0:
                    # Speed in m/s converted to km/h
                    self.speed = (distance / time_diff) * 3.6
            
            # Update last location
            self.last_location = (self.current_lat, self.current_lon, time.time())
            print(f"GPS: Lat={lat:.6f}, Lon={lon:.6f}, Speed={self.speed:.2f} km/h")
            
        except Exception as e:
            print(f"Error in on_location: {e}")
    
    def on_status(self, stype, status):
        """Called when GPS status changes"""
        print(f"GPS Status: {stype} - {status}")
        if status == 'provider-enabled':
            self.label.text = "GPS enabled"
        elif status == 'provider-disabled':
            self.label.text = "GPS disabled - enable location services"
    
    def haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two GPS coordinates in meters"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    def low_pass_filter(self, new, prev):
        """Low-pass filter to remove high-frequency noise"""
        return ALPHA_LPF * prev + (1 - ALPHA_LPF) * new
    
    def high_pass_filter(self, new, prev, prev_filtered):
        """High-pass filter to remove gravity/baseline"""
        return ALPHA_HPF * (prev_filtered + new - prev)
    
    def update(self, dt):
        """Main update loop - called every 0.5 seconds"""
        try:
            # Get accelerometer data
            val = accelerometer.acceleration
            
            if val is None or None in val:
                return
            
            x, y, z = val
            
            # Apply filters
            self.filtered_z = self.low_pass_filter(z, self.filtered_z)
            self.hpf_z = self.high_pass_filter(z, self.last_z, self.hpf_z)
            self.last_z = z
            
            # Build baseline
            self.baseline_window.append(self.filtered_z)
            if len(self.baseline_window) > BASELINE_SAMPLES:
                self.baseline_window.pop(0)
            
            # Calculate baseline average
            if self.baseline_window:
                self.baseline_z = sum(self.baseline_window) / len(self.baseline_window)
            
            # Calculate deviation from baseline
            delta_z = self.filtered_z - self.baseline_z
            
            # Detect pothole (adjust sensitivity based on speed)
            sensitivity = max(1, min(4, 4 - self.speed * 0.5))  # slower = more sensitive
            
            if delta_z < -sensitivity:
                # Pothole detected!
                event = {
                    "timestamp": time.time(),
                    "pothole": True,
                    "delta_z": delta_z,
                    "x": x,
                    "y": y,
                    "z": z,
                    "lat": self.current_lat,
                    "lon": self.current_lon,
                    "speed": self.speed
                }
                
                # Send to Firebase
                try:
                    requests.post(FIREBASE_URL, json=event, timeout=2)
                    self.label.text = f"Pothole! ΔZ={delta_z:.2f}\nLat={self.current_lat:.5f}, Lon={self.current_lon:.5f}"
                except Exception as e:
                    print(f"Firebase error: {e}")
                    self.label.text = f"Pothole detected (offline)\nΔZ={delta_z:.2f}"
            else:
                # Normal data logging
                data = {
                    "x": x,
                    "y": y,
                    "z": z,
                    "delta_z": delta_z,
                    "lat": self.current_lat,
                    "lon": self.current_lon,
                    "speed": self.speed,
                    "timestamp": time.time()
                }
                
                try:
                    requests.post(FIREBASE_URL, json=data, timeout=2)
                except Exception as e:
                    print(f"Firebase error: {e}")
                
                # Update display
                gps_status = f"GPS: {self.current_lat:.5f}, {self.current_lon:.5f}" if self.gps_enabled else "GPS: Waiting..."
                self.label.text = f"ΔZ={delta_z:.2f} | Speed={self.speed:.1f} km/h\n{gps_status}"
            
            # Auto-clear Firebase every 75 readings
            self.readings_since_reset += 1
            if self.readings_since_reset >= 75:
                try:
                    requests.delete(FIREBASE_URL, timeout=2)
                    self.readings_since_reset = 0
                    print("Firebase data cleared")
                except Exception as e:
                    print(f"Firebase clear error: {e}")
        
        except Exception as e:
            self.label.text = f"Error: {e}"
            print(f"Update error: {e}")
    
    def on_stop(self):
        """Clean up when app closes"""
        try:
            accelerometer.disable()
            if self.gps_enabled:
                gps.stop()
        except Exception as e:
            print(f"Cleanup error: {e}")

if __name__ == "__main__":
    AccelApp().run()
