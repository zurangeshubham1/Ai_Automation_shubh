#!/usr/bin/env python3
"""
Video Recorder for Browser Automation
Creates video recordings of browser automation sessions
"""

import os
import time
import cv2
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading
import queue

class BrowserVideoRecorder:
    def __init__(self, session_id, output_dir="videos"):
        self.session_id = session_id
        self.output_dir = output_dir
        self.video_writer = None
        self.recording = False
        self.frame_queue = queue.Queue()
        self.recording_thread = None
        self.fps = 2  # 2 frames per second for reasonable file size
        self.frame_size = (1920, 1080)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Video file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = os.path.join(output_dir, f"automation_{session_id}_{timestamp}.mp4")
        
    def start_recording(self):
        """Start video recording"""
        try:
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                self.video_path, 
                fourcc, 
                self.fps, 
                self.frame_size
            )
            
            self.recording = True
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._recording_worker)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            print(f"🎥 Video recording started: {self.video_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start video recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop video recording"""
        self.recording = False
        
        if self.recording_thread:
            self.recording_thread.join(timeout=5)
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        print(f"🎬 Video recording stopped: {self.video_path}")
        return self.video_path
    
    def capture_frame(self, driver, action_name=""):
        """Capture a frame from the browser"""
        if not self.recording or not driver:
            return
        
        try:
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            
            # Convert to OpenCV format
            nparr = np.frombuffer(screenshot, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Resize frame if needed
            if frame.shape[:2] != self.frame_size[::-1]:
                frame = cv2.resize(frame, self.frame_size)
            
            # Add action text overlay
            if action_name:
                cv2.putText(frame, f"Action: {action_name}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add to queue
            self.frame_queue.put(frame)
            
        except Exception as e:
            print(f"⚠️ Failed to capture frame: {e}")
    
    def _recording_worker(self):
        """Worker thread for writing video frames"""
        while self.recording:
            try:
                # Get frame from queue with timeout
                frame = self.frame_queue.get(timeout=1)
                
                if self.video_writer:
                    self.video_writer.write(frame)
                
                self.frame_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Recording worker error: {e}")
                break
    
    def get_video_info(self):
        """Get information about the recorded video"""
        if os.path.exists(self.video_path):
            file_size = os.path.getsize(self.video_path)
            return {
                'path': self.video_path,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'exists': True
            }
        return {'exists': False}

class EnhancedCSVActionHandler:
    """Enhanced CSV Action Handler with Video Recording"""
    
    def __init__(self, browser='chrome', session_id=None):
        self.driver = None
        self.wait = None
        self.browser = browser
        self.session_id = session_id or f"session_{int(time.time())}"
        self.video_recorder = BrowserVideoRecorder(self.session_id)
        self.recording_started = False
        
    def setup_driver_with_recording(self):
        """Setup browser driver with video recording"""
        try:
            # Setup browser (headless for cloud, visible for local)
            if self._is_cloud_environment():
                print("☁️ Setting up headless browser with video recording")
                self._setup_headless_browser()
            else:
                print("🖥️ Setting up visible browser with video recording")
                self._setup_visible_browser()
            
            # Start video recording
            if self.video_recorder.start_recording():
                self.recording_started = True
                print("🎥 Video recording enabled")
            
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 20)
            
        except Exception as e:
            print(f"❌ Failed to setup driver with recording: {e}")
    
    def _is_cloud_environment(self):
        """Check if running in cloud environment"""
        import os
        if os.environ.get('FORCE_VISIBLE_BROWSER', '').lower() in ['true', '1', 'yes']:
            return False
        
        cloud_indicators = [
            'RAILWAY_ENVIRONMENT' in os.environ,
            'RENDER' in os.environ,
            'HEROKU' in os.environ,
            'VERCEL' in os.environ,
            'NETLIFY' in os.environ,
            os.path.exists('/.dockerenv'),
            'DISPLAY' not in os.environ,
        ]
        return any(cloud_indicators)
    
    def _setup_headless_browser(self):
        """Setup headless browser"""
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
    def _setup_visible_browser(self):
        """Setup visible browser"""
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def execute_action_with_recording(self, action, xpath, data=""):
        """Execute action with video recording"""
        action_name = f"{action}_{xpath.replace('//', '').replace('@', '').replace('=', '_')[:20]}"
        
        print(f"🎬 Recording: {action} on {xpath}")
        
        # Capture frame before action
        if self.recording_started:
            self.video_recorder.capture_frame(self.driver, f"Before: {action}")
        
        # Execute the action (simplified version)
        try:
            if action.lower() == 'open_url':
                self.driver.get(xpath)
                time.sleep(2)
            elif action.lower() == 'type':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                element.clear()
                element.send_keys(data)
            elif action.lower() == 'click':
                element = self.wait.until(EC.element_to_be_clickable(self.parse_selector(xpath)))
                element.click()
            elif action.lower() == 'wait':
                seconds = int(data) if data.isdigit() else 5
                time.sleep(seconds)
            
            # Capture frame after action
            if self.recording_started:
                self.video_recorder.capture_frame(self.driver, f"After: {action}")
            
            return True
            
        except Exception as e:
            print(f"❌ Action failed: {e}")
            # Capture error frame
            if self.recording_started:
                self.video_recorder.capture_frame(self.driver, f"Error: {action}")
            return False
    
    def teardown_with_recording(self):
        """Stop recording and close browser"""
        if self.recording_started:
            video_path = self.video_recorder.stop_recording()
            print(f"🎬 Video saved: {video_path}")
            return video_path
        
        if self.driver:
            self.driver.quit()
        
        return None

def main():
    """Demo of video recording functionality"""
    print("🎥 Browser Video Recording Demo")
    print("=" * 40)
    
    # This would be integrated into your existing CSV action handler
    print("✅ Video recording functionality created")
    print("📹 Records browser automation in real-time")
    print("💾 Saves as MP4 video file")
    print("🌐 Can be downloaded from web interface")

if __name__ == '__main__':
    main()
