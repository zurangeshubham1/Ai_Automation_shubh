# 🌐 Visible Browser Mode Guide

## Problem
Your AI Agent is currently running in a cloud environment (Railway), which automatically detects this and runs the browser in **headless mode** (without a visible interface). This is why you can't see the browser window.

## Solution
I've created a **Visible Browser Mode** that bypasses the cloud detection and allows you to see the browser windows during automation.

## How to Use Visible Browser Mode

### Option 1: Use the New Startup Script (Recommended)
```bash
# Run the visible browser startup script
python start_visible_browser.py
```

Or on Windows, double-click:
```
start_visible_browser.bat
```

### Option 2: Set Environment Variable Manually
```bash
# Set the environment variable
set FORCE_VISIBLE_BROWSER=true

# Then run your normal startup
python start_web_interface.py
```

### Option 3: Test Browser Functionality First
```bash
# Test if visible browser works
python test_visible_browser.py
```

## What This Does

1. **Sets Environment Variable**: `FORCE_VISIBLE_BROWSER=true` tells the system to ignore cloud detection
2. **Bypasses Headless Mode**: Forces the browser to open with a visible window
3. **Local Testing**: Perfect for development and debugging your automation scripts

## Files Created

- `start_visible_browser.py` - Main startup script with visible browser mode
- `start_visible_browser.bat` - Windows batch file for easy startup
- `test_visible_browser.py` - Test script to verify browser functionality
- `VISIBLE_BROWSER_GUIDE.md` - This guide

## Expected Behavior

When you run scripts in visible browser mode:
- ✅ Browser windows will be **visible** and you can watch the automation
- ✅ You can interact with the browser if needed
- ✅ Screenshots will still be taken for reports
- ✅ All automation features work normally

## Troubleshooting

### If browser still doesn't appear:
1. Make sure you're running locally (not on Railway)
2. Check that Chrome/Firefox is installed
3. Run `python test_visible_browser.py` to diagnose issues
4. Ensure webdriver-manager can download drivers

### If you get driver errors:
```bash
pip install webdriver-manager
```

## Switching Back to Cloud Mode

To go back to headless mode (for cloud deployment):
```bash
# Remove or set to false
set FORCE_VISIBLE_BROWSER=false
# or just don't set it at all
```

## Next Steps

1. Run `python start_visible_browser.py`
2. Open http://localhost:5000 in your browser
3. Try running one of your CSV scripts
4. You should now see the browser window open and perform the actions!

---

**Note**: This mode is specifically for local development and testing. For production deployment on Railway, the system will automatically use headless mode.
