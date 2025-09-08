#!/usr/bin/env python3
"""
Alternative Video Recorder using imageio for better compatibility
"""

import os
import time
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import imageio
from PIL import Image, ImageDraw, ImageFont
import io

class AlternativeVideoRecorder:
    def __init__(self, session_id, output_dir="videos"):
        self.session_id = session_id
        self.output_dir = output_dir
        self.frames = []
        self.recording = False
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Video file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_path = os.path.join(output_dir, f"automation_{session_id}_{timestamp}.mp4")
        
    def start_recording(self):
        """Start video recording"""
        self.recording = True
        self.frames = []
        print(f"🎥 Alternative video recording started: {self.video_path}")
        return True
    
    def stop_recording(self):
        """Stop video recording and save video"""
        if not self.recording or not self.frames:
            print("⚠️ No frames to save")
            return None
        
        try:
            # Save video using imageio
            with imageio.get_writer(self.video_path, fps=2, codec='libx264') as writer:
                for frame in self.frames:
                    writer.append_data(frame)
            
            self.recording = False
            file_size = os.path.getsize(self.video_path)
            print(f"🎬 Alternative video saved: {self.video_path} ({round(file_size / 1024, 2)} KB)")
            return self.video_path
            
        except Exception as e:
            print(f"❌ Failed to save video: {e}")
            return None
    
    def capture_frame(self, driver, action_name=""):
        """Capture a frame from the browser"""
        if not self.recording or not driver:
            return
        
        try:
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(screenshot))
            
            # Resize to standard size
            image = image.resize((1920, 1080), Image.Resampling.LANCZOS)
            
            # Add text overlay
            draw = ImageDraw.Draw(image)
            
            # Try to use a default font, fallback to basic if not available
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_medium = ImageFont.truetype("arial.ttf", 18)
                font_small = ImageFont.truetype("arial.ttf", 14)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add action text
            if action_name:
                draw.text((10, 10), f"Action: {action_name}", fill=(0, 255, 0), font=font_large)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            draw.text((10, image.height - 40), timestamp, fill=(255, 255, 255), font=font_medium)
            
            # Add URL
            url = driver.current_url
            if len(url) > 50:
                url = url[:47] + "..."
            draw.text((10, image.height - 20), url, fill=(255, 255, 255), font=font_small)
            
            # Convert to numpy array for imageio
            frame = np.array(image)
            
            # Ensure it's RGB (not RGBA)
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]
            
            self.frames.append(frame)
            
        except Exception as e:
            print(f"⚠️ Failed to capture frame: {e}")
    
    def get_video_info(self):
        """Get information about the recorded video"""
        if os.path.exists(self.video_path):
            file_size = os.path.getsize(self.video_path)
            return {
                'path': self.video_path,
                'filename': os.path.basename(self.video_path),
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'exists': True,
                'session_id': self.session_id
            }
        return {'exists': False}

def test_alternative_recorder():
    """Test the alternative video recorder"""
    print("🧪 Testing Alternative Video Recorder")
    print("=" * 50)
    
    try:
        # Set environment variable for visible browser
        os.environ['FORCE_VISIBLE_BROWSER'] = 'true'
        
        from csv_action_handler import CSVActionHandler
        
        # Create handler
        handler = CSVActionHandler(browser='chrome', session_id='alt_test')
        
        # Setup driver
        handler.setup_driver()
        
        if handler.driver is None:
            print("❌ Failed to setup browser")
            return False
        
        # Create alternative recorder
        alt_recorder = AlternativeVideoRecorder('alt_test')
        alt_recorder.start_recording()
        
        # Test basic functionality
        print("🌐 Opening example.com...")
        handler.driver.get("https://example.com")
        time.sleep(2)
        
        # Capture frames
        alt_recorder.capture_frame(handler.driver, "Open example.com")
        time.sleep(2)
        alt_recorder.capture_frame(handler.driver, "Page loaded")
        
        # Stop recording
        video_path = alt_recorder.stop_recording()
        
        # Close browser
        handler.driver.quit()
        
        if video_path and os.path.exists(video_path):
            print("✅ Alternative video recorder test successful!")
            return True
        else:
            print("❌ Alternative video recorder test failed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🎥 Alternative Video Recorder Test")
    print("This uses imageio instead of OpenCV for better compatibility")
    print()
    
    success = test_alternative_recorder()
    
    if success:
        print("\n🎉 SUCCESS: Alternative video recording works!")
    else:
        print("\n❌ FAILED: Alternative video recording test failed.")
    
    input("\nPress Enter to exit...")
