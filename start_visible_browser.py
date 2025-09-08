#!/usr/bin/env python3
"""
AI Agent Web Interface - Visible Browser Mode
This script starts the web interface with visible browser automation for local testing
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        'selenium',
        'allure-pytest',
        'flask',
        'flask-cors',
        'webdriver-manager'
    ]
    
    for package in requirements:
        try:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'web_interface.html',
        'web_server.py',
        'csv_action_handler.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    return True

def create_sample_scripts():
    """Create sample CSV scripts if they don't exist"""
    if not os.path.exists('sample_actions.csv'):
        print("📝 Creating sample_actions.csv...")
        sample_content = """action,xpath,data
open_url,https://example.com,
wait,3,
type,//input[@id="username"],testuser
type,//input[@id="password"],testpass
click,//button[@type="submit"],
verify,text=Welcome,
"""
        with open('sample_actions.csv', 'w') as f:
            f.write(sample_content)
        print("✅ sample_actions.csv created")
    
    if not os.path.exists('enhanced_sample_actions.csv'):
        print("📝 Creating enhanced_sample_actions.csv...")
        enhanced_content = """action,xpath,data
open_url,https://example.com/forms,
wait,5,
type,//input[@id="name"],John Doe
type,//input[@id="email"],john@example.com
select_dropdown,//select[@id="country"],United States
js_click,//button[@id="custom-dropdown"],
wait,2,
js_click,//div[text()="Option 1"],
upload_file,//input[@type="file"],C:\\Users\\Admin\\Pictures\\sample.jpg
wait_for_element,//div[@id="success-message"],
verify,text=Form submitted successfully,
click,//button[@id="submit"],
"""
        with open('enhanced_sample_actions.csv', 'w') as f:
            f.write(enhanced_content)
        print("✅ enhanced_sample_actions.csv created")

def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Browser opened automatically")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("🌐 Please open http://localhost:5000 manually")

def main():
    """Main startup function"""
    print("🤖 AI Agent Web Interface - VISIBLE BROWSER MODE")
    print("=" * 60)
    print("🔧 This mode forces visible browser automation for local testing")
    print("=" * 60)
    
    # Set environment variable to force visible browser
    os.environ['FORCE_VISIBLE_BROWSER'] = 'true'
    print("✅ Environment variable FORCE_VISIBLE_BROWSER set to 'true'")
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check required files
    if not check_files():
        print("❌ Please ensure all required files are in the current directory")
        input("Press Enter to exit...")
        return
    
    # Install requirements
    print("\n📦 Checking and installing requirements...")
    if not install_requirements():
        print("❌ Failed to install requirements")
        input("Press Enter to exit...")
        return
    
    # Create sample scripts
    print("\n📝 Setting up sample scripts...")
    create_sample_scripts()
    
    # Start browser opening thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start web server
    print("\n🚀 Starting web server with VISIBLE BROWSER mode...")
    print("📱 Dashboard will be available at: http://localhost:5000")
    print("🌐 Browser windows will be VISIBLE during automation")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Import and run the web server
        from web_server import app
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
    finally:
        print("👋 Goodbye!")

if __name__ == '__main__':
    main()
