#!/usr/bin/env python3
"""
Test script for video recording functionality
"""

import os
import sys
import time

# Set environment variable to force visible browser for testing
os.environ['FORCE_VISIBLE_BROWSER'] = 'true'

def test_video_recording():
    """Test video recording functionality"""
    print("🎥 Testing Video Recording Functionality")
    print("=" * 50)
    
    try:
        from csv_action_handler import CSVActionHandler
        
        print("✅ CSVActionHandler imported successfully")
        
        # Create handler
        handler = CSVActionHandler(browser='chrome', session_id='test_video')
        print("✅ Handler created successfully")
        
        # Setup driver with video recording
        print("🔧 Setting up browser with video recording...")
        handler.setup_driver()
        
        if handler.driver is None:
            print("❌ Failed to setup browser driver")
            return False
        
        print("✅ Browser driver setup successful")
        print("🎥 Video recording should be active")
        
        # Test basic functionality with video recording
        print("🌐 Opening Google.com...")
        handler.driver.get("https://www.google.com")
        time.sleep(2)
        
        print("🔍 Searching for 'AI Agent'...")
        search_box = handler.driver.find_element("name", "q")
        search_box.send_keys("AI Agent")
        time.sleep(1)
        
        print("🔍 Clicking search button...")
        search_button = handler.driver.find_element("name", "btnK")
        search_button.click()
        time.sleep(3)
        
        print("⏳ Keeping browser open for 5 seconds to record...")
        time.sleep(5)
        
        # Close browser and stop recording
        print("🔄 Closing browser and stopping recording...")
        handler.teardown_driver()
        
        # Check if video was created
        video_info = handler.get_video_info()
        if video_info['exists']:
            print("✅ Video recording test completed successfully!")
            print(f"🎬 Video saved: {video_info['filename']}")
            print(f"📁 Size: {video_info['size_mb']} MB")
            print(f"📍 Path: {video_info['path']}")
            return True
        else:
            print("❌ Video was not created")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🧪 Video Recording Test")
    print("This will test the video recording functionality")
    print("Make sure you have opencv-python installed: pip install opencv-python")
    print()
    
    success = test_video_recording()
    
    if success:
        print("\n🎉 SUCCESS: Video recording is working!")
        print("You can now run CSV scripts and get video recordings.")
        print("Videos will be saved in the 'videos' folder.")
    else:
        print("\n❌ FAILED: Video recording test failed.")
        print("Please check your installation and try again.")
    
    input("\nPress Enter to exit...")
