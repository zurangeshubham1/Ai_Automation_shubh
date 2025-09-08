#!/usr/bin/env python3
"""
Simple video recording test
"""

import os
import sys
import time

# Set environment variable to force visible browser for testing
os.environ['FORCE_VISIBLE_BROWSER'] = 'true'

def simple_video_test():
    """Simple test of video recording functionality"""
    print("🎥 Simple Video Recording Test")
    print("=" * 40)
    
    try:
        from csv_action_handler import CSVActionHandler
        
        print("✅ CSVActionHandler imported successfully")
        
        # Create handler
        handler = CSVActionHandler(browser='chrome', session_id='simple_test')
        print("✅ Handler created successfully")
        
        # Setup driver with video recording
        print("🔧 Setting up browser with video recording...")
        handler.setup_driver()
        
        if handler.driver is None:
            print("❌ Failed to setup browser driver")
            return False
        
        print("✅ Browser driver setup successful")
        print("🎥 Video recording should be active")
        
        # Simple test - just open a page and wait
        print("🌐 Opening example.com...")
        handler.driver.get("https://example.com")
        time.sleep(3)
        
        print("⏳ Recording for 5 seconds...")
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
    print("🧪 Simple Video Recording Test")
    print("This will test basic video recording functionality")
    print()
    
    success = simple_video_test()
    
    if success:
        print("\n🎉 SUCCESS: Video recording is working!")
        print("The video recording feature is ready to use.")
    else:
        print("\n❌ FAILED: Video recording test failed.")
        print("Please check your installation and try again.")
    
    input("\nPress Enter to exit...")
