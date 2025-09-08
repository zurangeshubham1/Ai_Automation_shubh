#!/usr/bin/env python3
"""
AI Agent - Local Development Startup Script
This script sets up the environment for local development with visible browser
"""

import os
import sys
import subprocess

def main():
    print("🤖 AI Agent - Local Development Mode")
    print("=" * 50)
    
    # Set environment variables for local development
    os.environ['FORCE_VISIBLE_BROWSER'] = 'true'
    os.environ['FLASK_ENV'] = 'development'
    
    print("✅ Environment variables set:")
    print(f"   FORCE_VISIBLE_BROWSER = {os.environ.get('FORCE_VISIBLE_BROWSER')}")
    print(f"   FLASK_ENV = {os.environ.get('FLASK_ENV')}")
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Virtual environment not detected - consider activating .venv")
    
    print("\n🚀 Starting web server...")
    print("📱 Dashboard will be available at: http://localhost:5000")
    print("🌐 Browser windows will be VISIBLE during automation")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the web server
    try:
        from web_server import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
