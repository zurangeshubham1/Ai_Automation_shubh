# 🎥 Video Recording Feature Guide

## 🎯 What This Feature Does

Your AI Agent now automatically records **video files** of all browser automation sessions! This gives you visual feedback of what's happening on the live Railway environment, even though the browser runs headless.

## 🚀 How It Works

### **Automatic Recording**
- ✅ **Every CSV script execution** is automatically recorded
- ✅ **Real-time video capture** at 2 FPS (frames per second)
- ✅ **Action overlays** showing what's happening
- ✅ **Timestamp and URL** displayed on each frame
- ✅ **MP4 format** for easy viewing

### **Video Content**
Each video includes:
- 📸 **Screenshots** of every action (before/after)
- 🏷️ **Action labels** (e.g., "Before: click", "After: type")
- ⏰ **Timestamps** for each frame
- 🌐 **Current URL** being accessed
- ❌ **Error frames** if actions fail

## 📁 File Structure

```
videos/
├── automation_session_123_20250107_143022.mp4
├── automation_session_456_20250107_144511.mp4
└── automation_session_789_20250107_145203.mp4
```

## 🌐 Live Website Features

### **New API Endpoints**
- `GET /api/videos` - List all recorded videos
- `GET /api/video/<session_id>` - Get video info for a session
- `GET /api/download-video/<session_id>` - Download session video
- `GET /api/download-video-file/<filename>` - Download specific video

### **Video Management**
- 📋 **List all videos** with creation time and file size
- ⬇️ **Download videos** directly from the web interface
- 🗂️ **Organized by session** and timestamp
- 🧹 **Automatic cleanup** of old videos

## 🔧 Installation Requirements

### **New Dependencies**
```bash
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
```

### **Updated requirements.txt**
```
selenium>=4.15.0
flask>=2.3.0
flask-cors>=4.0.0
allure-pytest>=2.13.0
webdriver-manager>=4.0.0
gunicorn>=21.0.0
opencv-python>=4.8.0
numpy>=1.24.0
```

## 🎬 How to Use

### **1. Run CSV Scripts (Automatic)**
```bash
# On live Railway site:
# 1. Upload your CSV script
# 2. Click "Run Selected"
# 3. Video recording starts automatically
# 4. Download video when complete
```

### **2. Local Testing**
```bash
# Test video recording locally:
python test_video_recording.py

# Or run with visible browser:
python start_visible_browser.py
```

### **3. Download Videos**
- **From Live Site**: Use the new video download buttons
- **From API**: `GET /api/videos` to list, then download
- **Direct Access**: Videos stored in `/videos/` folder

## 📊 Video Specifications

### **Technical Details**
- **Format**: MP4 (H.264)
- **Frame Rate**: 2 FPS (optimized for file size)
- **Resolution**: 1920x1080
- **File Size**: ~1-5 MB per minute of automation
- **Quality**: High quality screenshots with overlays

### **Performance**
- ✅ **Low CPU usage** (2 FPS recording)
- ✅ **Small file sizes** (optimized compression)
- ✅ **Fast processing** (real-time capture)
- ✅ **Cloud compatible** (works on Railway)

## 🎯 Use Cases

### **1. Debugging Automation**
- See exactly what the browser is doing
- Identify where scripts fail
- Verify element interactions

### **2. Documentation**
- Create visual documentation of processes
- Share automation results with team
- Training materials for new users

### **3. Quality Assurance**
- Review automation accuracy
- Validate business processes
- Audit automation performance

## 🔍 Example Workflow

### **Step 1: Run Script**
```
1. Upload CSV script to Railway
2. Click "Run Selected"
3. Watch execution logs
4. Wait for completion
```

### **Step 2: Download Video**
```
1. Go to video section
2. Find your session video
3. Click "Download"
4. Watch the automation video
```

### **Step 3: Review Results**
```
1. Open downloaded MP4 file
2. See each action performed
3. Identify any issues
4. Share with team if needed
```

## 🛠️ Troubleshooting

### **Video Not Created**
- Check if OpenCV is installed: `pip install opencv-python`
- Verify browser driver is working
- Check disk space in `/videos/` folder

### **Large File Sizes**
- Videos are optimized for 2 FPS
- File sizes are typically 1-5 MB per minute
- Consider cleanup of old videos

### **Download Issues**
- Check network connection
- Verify video file exists
- Try direct API access

## 🎉 Benefits

### **For Live Environment**
- ✅ **Visual feedback** of headless automation
- ✅ **Debugging capability** without visible browser
- ✅ **Documentation** of all automation runs
- ✅ **Quality assurance** through video review

### **For Development**
- ✅ **Local testing** with visible browser
- ✅ **Video recording** for both modes
- ✅ **Easy sharing** of automation results
- ✅ **Professional documentation**

## 🚀 Next Steps

1. **Deploy to Railway** with updated code
2. **Test video recording** with a simple CSV script
3. **Download and review** your first automation video
4. **Share videos** with your team for feedback

---

**Note**: Video recording works on both local (visible browser) and live (headless browser) environments, giving you the best of both worlds! 🎬✨
