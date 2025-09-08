#!/usr/bin/env python3
"""
Video validation script
"""

import os
import cv2

def validate_video(video_path):
    """Validate if a video file is playable"""
    print(f"🔍 Validating video: {video_path}")
    
    if not os.path.exists(video_path):
        print("❌ Video file does not exist")
        return False
    
    file_size = os.path.getsize(video_path)
    print(f"📁 File size: {file_size} bytes ({round(file_size / 1024, 2)} KB)")
    
    if file_size == 0:
        print("❌ Video file is empty")
        return False
    
    try:
        # Try to open with OpenCV
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print("❌ Cannot open video with OpenCV")
            return False
        
        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ Video opened successfully!")
        print(f"📊 Properties:")
        print(f"   - Frames: {frame_count}")
        print(f"   - FPS: {fps}")
        print(f"   - Resolution: {width}x{height}")
        
        # Try to read first frame
        ret, frame = cap.read()
        if ret:
            print("✅ Can read frames from video")
        else:
            print("❌ Cannot read frames from video")
            cap.release()
            return False
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Error validating video: {e}")
        return False

def main():
    """Main validation function"""
    print("🎥 Video Validation Tool")
    print("=" * 30)
    
    # Check both video files
    videos_dir = "videos"
    if os.path.exists(videos_dir):
        for filename in os.listdir(videos_dir):
            if filename.endswith('.mp4'):
                video_path = os.path.join(videos_dir, filename)
                print(f"\n📹 Checking: {filename}")
                is_valid = validate_video(video_path)
                
                if is_valid:
                    print(f"✅ {filename} is a valid, playable video!")
                else:
                    print(f"❌ {filename} has issues and may not play properly")
    else:
        print("❌ Videos directory not found")

if __name__ == '__main__':
    main()
    input("\nPress Enter to exit...")
