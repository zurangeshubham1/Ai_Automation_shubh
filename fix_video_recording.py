#!/usr/bin/env python3
"""
Fix for video recording issues
"""

import os
import sys
import time

# Set environment variable to force visible browser for testing
os.environ['FORCE_VISIBLE_BROWSER'] = 'true'

def fix_video_recording():
    """Fix video recording with better codec handling"""
    print("🔧 Fixing Video Recording Issues")
    print("=" * 40)
    
    try:
        from csv_action_handler import CSVActionHandler
        
        print("✅ CSVActionHandler imported successfully")
        
        # Create handler
        handler = CSVActionHandler(browser='chrome', session_id='fix_test')
        print("✅ Handler created successfully")
        
        # Setup driver with video recording
        print("🔧 Setting up browser with fixed video recording...")
        handler.setup_driver()
        
        if handler.driver is None:
            print("❌ Failed to setup browser driver")
            return False
        
        print("✅ Browser driver setup successful")
        print("🎥 Video recording should be active")
        
        # Simple test - just open a page and wait
        print("🌐 Opening example.com...")
        handler.driver.get("https://example.com")
        time.sleep(2)
        
        # Capture a few frames
        print("📸 Capturing frames...")
        for i in range(3):
            handler._capture_video_frame(f"Frame {i+1}")
            time.sleep(1)
        
        print("⏳ Recording for 3 more seconds...")
        time.sleep(3)
        
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
            
            # Try to verify the video file
            if video_info['size'] > 0:
                print("✅ Video file has content and should be playable")
                return True
            else:
                print("❌ Video file is empty")
                return False
        else:
            print("❌ Video was not created")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🧪 Video Recording Fix Test")
    print("This will test the fixed video recording functionality")
    print()
    
    success = fix_video_recording()
    
    if success:
        print("\n🎉 SUCCESS: Video recording is now working!")
        print("The video file should be playable in any media player.")
    else:
        print("\n❌ FAILED: Video recording still has issues.")
        print("We may need to try a different approach.")
    
    input("\nPress Enter to exit...")
