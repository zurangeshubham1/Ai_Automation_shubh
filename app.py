#!/usr/bin/env python3
"""
AI Agent Web App - Production Entry Point
This is the main entry point for cloud deployment
"""

import os
from web_server import app

if __name__ == '__main__':
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🚀 Starting AI Agent Web Server on {host}:{port}")
    app.run(host=host, port=port, debug=False)
