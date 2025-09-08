#!/usr/bin/env python3
"""
AI Agent Web Server - Flask Backend for Browser Automation Dashboard
"""

import os
import json
import subprocess
import threading
import time
import glob
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import csv
from csv_action_handler import CSVActionHandler
import uuid
import shutil

app = Flask(__name__)
CORS(app)

# Global variables
active_sessions = {}
script_sessions = {}

# Use the main CSVActionHandler class directly
WebCSVHandler = CSVActionHandler

# Video storage directory
VIDEO_DIR = 'recorded_videos'
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

def get_available_scripts():
    """Get list of available CSV scripts"""
    scripts = []
    csv_files = glob.glob("*.csv")
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                actions = list(reader)
                
            scripts.append({
                'name': csv_file,
                'path': csv_file,
                'actions': len(actions),
                'status': 'ready',
                'last_modified': datetime.fromtimestamp(os.path.getmtime(csv_file)).isoformat()
            })
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    return scripts

def get_video_info(filepath):
    """Get video file information"""
    try:
        stat = os.stat(filepath)
        size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        # Format file size - prioritize MB for videos
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.2f} MB"
        
        return {
            'name': os.path.basename(filepath),
            'size': size_str,
            'date': modified_time.strftime('%Y-%m-%d %H:%M'),
            'duration': 'Unknown'  # Could be enhanced with video metadata
        }
    except Exception as e:
        print(f"Error getting video info for {filepath}: {e}")
        return None

def get_available_videos():
    """Get list of available video files"""
    videos = []
    video_extensions = ['.webm', '.mp4', '.avi', '.mov']
    
    for ext in video_extensions:
        pattern = os.path.join(VIDEO_DIR, f"*{ext}")
        video_files = glob.glob(pattern)
        
        for video_file in video_files:
            video_info = get_video_info(video_file)
            if video_info:
                videos.append(video_info)
    
    # Sort by modification time (newest first)
    videos.sort(key=lambda x: x['date'], reverse=True)
    return videos

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('.', 'web_interface.html')

@app.route('/api/scripts')
def api_scripts():
    """Get available scripts"""
    try:
        scripts = get_available_scripts()
        print(f"DEBUG: Found {len(scripts)} scripts: {[s['name'] for s in scripts]}")
        return jsonify({'success': True, 'scripts': scripts})
    except Exception as e:
        print(f"DEBUG: Error getting scripts: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-installation', methods=['POST'])
def api_check_installation():
    """Check system installation status"""
    try:
        data = request.get_json()
        browser = data.get('browser', 'chrome')
        
        # Check if required packages are installed
        required_packages = ['selenium', 'allure-pytest', 'flask', 'flask-cors']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        # Check if browser drivers exist
        driver_status = check_browser_drivers(browser)
        
        return jsonify({
            'success': len(missing_packages) == 0 and driver_status['available'],
            'missing_packages': missing_packages,
            'driver_status': driver_status
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/install-dependencies', methods=['POST'])
def api_install_dependencies():
    """Install required dependencies"""
    try:
        data = request.get_json()
        browser = data.get('browser', 'chrome')
        
        # Install Python packages
        packages = ['selenium', 'allure-pytest', 'flask', 'flask-cors']
        for package in packages:
            try:
                subprocess.run(['pip', 'install', package], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                return jsonify({'success': False, 'error': f'Failed to install {package}: {e.stderr.decode()}'})
        
        # Download browser drivers
        download_driver(browser)
        
        return jsonify({'success': True, 'message': 'Dependencies installed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download-drivers', methods=['POST'])
def api_download_drivers():
    """Download browser drivers"""
    try:
        data = request.get_json()
        browser = data.get('browser', 'chrome')
        
        success = download_driver(browser)
        return jsonify({'success': success, 'message': f'Driver for {browser} downloaded'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/run-script', methods=['POST'])
def api_run_script():
    """Run a CSV script"""
    try:
        data = request.get_json()
        script_name = data.get('script')
        browser = data.get('browser', 'chrome')
        auto_record = data.get('autoRecord', True)
        
        print(f"DEBUG: Attempting to run script: {script_name}")
        print(f"DEBUG: Auto-record enabled: {auto_record}")
        print(f"DEBUG: Script exists: {os.path.exists(script_name) if script_name else 'No script name'}")
        print(f"DEBUG: Current directory: {os.getcwd()}")
        print(f"DEBUG: Files in directory: {os.listdir('.')}")
        
        if not script_name or not os.path.exists(script_name):
            return jsonify({'success': False, 'error': f'Script not found: {script_name}'})
        
        # Create session
        session_id = str(uuid.uuid4())
        handler = WebCSVHandler(browser, session_id)
        
        # Set auto-recording preference
        handler.auto_record_enabled = auto_record
        
        # Store session
        script_sessions[session_id] = {
            'handler': handler,
            'script': script_name,
            'browser': browser,
            'start_time': datetime.now(),
            'status': 'running'
        }
        
        # Run script in background thread
        def run_script():
            try:
                print(f"DEBUG: Starting script execution for {script_name}")
                
                # Add overall timeout for script execution (5 minutes)
                import signal
                
                def script_timeout_handler(signum, frame):
                    print(f"DEBUG: Script {script_name} timed out after 5 minutes")
                    script_sessions[session_id]['status'] = 'timeout'
                    script_sessions[session_id]['error'] = 'Script execution timed out after 5 minutes'
                    # Force close browser
                    if hasattr(handler, 'driver') and handler.driver:
                        try:
                            handler.driver.quit()
                        except:
                            pass
                    raise TimeoutError("Script execution timed out")
                
                # Set timeout for entire script execution
                signal.signal(signal.SIGALRM, script_timeout_handler)
                signal.alarm(300)  # 5 minutes timeout
                
                try:
                    result = handler.run_actions_from_csv(script_name)
                    signal.alarm(0)  # Cancel timeout
                    
                    script_sessions[session_id]['status'] = handler.status
                    script_sessions[session_id]['end_time'] = datetime.now()
                    script_sessions[session_id]['result'] = result
                    print(f"DEBUG: Script {script_name} completed with status: {handler.status}")
                    
                except TimeoutError:
                    print(f"DEBUG: Script {script_name} timed out")
                    script_sessions[session_id]['status'] = 'timeout'
                    script_sessions[session_id]['error'] = 'Script execution timed out'
                    script_sessions[session_id]['end_time'] = datetime.now()
                    
            except Exception as e:
                print(f"DEBUG: Script {script_name} failed with error: {str(e)}")
                script_sessions[session_id]['status'] = 'error'
                script_sessions[session_id]['error'] = str(e)
                script_sessions[session_id]['end_time'] = datetime.now()
                # Make sure to close browser if it was opened
                if hasattr(handler, 'driver') and handler.driver:
                    try:
                        handler.driver.quit()
                    except:
                        pass
        
        thread = threading.Thread(target=run_script)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'sessionId': session_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop-script', methods=['POST'])
def api_stop_script():
    """Stop a running script"""
    try:
        data = request.get_json()
        session_id = data.get('sessionId')
        
        if session_id in script_sessions:
            session = script_sessions[session_id]
            if hasattr(session['handler'], 'driver') and session['handler'].driver:
                session['handler'].driver.quit()
            session['status'] = 'stopped'
            session['end_time'] = datetime.now()
            return jsonify({'success': True, 'message': 'Script stopped'})
        else:
            return jsonify({'success': False, 'error': 'Session not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/script-progress/<session_id>')
def api_script_progress(session_id):
    """Get script execution progress"""
    try:
        if session_id in script_sessions:
            session = script_sessions[session_id]
            handler = session['handler']
            
            return jsonify({
                'success': True,
                'status': handler.status,
                'progress': handler.progress,
                'current_action': handler.current_action,
                'logs': handler.logs[-10:],  # Last 10 log entries
                'session_id': session_id
            })
        else:
            return jsonify({'success': False, 'error': 'Session not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload-script', methods=['POST'])
def api_upload_script():
    """Upload a new CSV script"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and file.filename.endswith('.csv'):
            filename = file.filename
            file.save(filename)
            
            # Validate CSV format
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    actions = list(reader)
                
                if not actions:
                    os.remove(filename)
                    return jsonify({'success': False, 'error': 'Empty CSV file'})
                
                return jsonify({'success': True, 'message': f'Script uploaded: {filename}'})
            except Exception as e:
                os.remove(filename)
                return jsonify({'success': False, 'error': f'Invalid CSV format: {str(e)}'})
        else:
            return jsonify({'success': False, 'error': 'Only CSV files are allowed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def check_browser_drivers(browser):
    """Check if browser drivers are available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.edge.service import Service as EdgeService
        
        if browser == 'chrome':
            try:
                driver = webdriver.Chrome()
                driver.quit()
                return {'available': True, 'message': 'Chrome driver ready'}
            except:
                return {'available': False, 'message': 'Chrome driver not found'}
        
        elif browser == 'firefox':
            try:
                driver = webdriver.Firefox()
                driver.quit()
                return {'available': True, 'message': 'Firefox driver ready'}
            except:
                return {'available': False, 'message': 'Firefox driver not found'}
        
        elif browser == 'edge':
            try:
                driver = webdriver.Edge()
                driver.quit()
                return {'available': True, 'message': 'Edge driver ready'}
            except:
                return {'available': False, 'message': 'Edge driver not found'}
        
    except Exception as e:
        return {'available': False, 'message': f'Driver check failed: {str(e)}'}

def download_driver(browser):
    """Download browser driver"""
    try:
        if browser == 'chrome':
            # Use webdriver-manager for automatic driver management
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                ChromeDriverManager().install()
                return True
            except ImportError:
                subprocess.run(['pip', 'install', 'webdriver-manager'], check=True)
                from webdriver_manager.chrome import ChromeDriverManager
                ChromeDriverManager().install()
                return True
        
        elif browser == 'firefox':
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                GeckoDriverManager().install()
                return True
            except ImportError:
                subprocess.run(['pip', 'install', 'webdriver-manager'], check=True)
                from webdriver_manager.firefox import GeckoDriverManager
                GeckoDriverManager().install()
                return True
        
        elif browser == 'edge':
            try:
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                EdgeChromiumDriverManager().install()
                return True
            except ImportError:
                subprocess.run(['pip', 'install', 'webdriver-manager'], check=True)
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                EdgeChromiumDriverManager().install()
                return True
        
        return False
    except Exception as e:
        print(f"Error downloading driver: {e}")
        return False

@app.route('/api/test-browser', methods=['POST'])
def api_test_browser():
    """Test if browser can be opened"""
    try:
        data = request.get_json()
        browser = data.get('browser', 'chrome')
        
        print(f"DEBUG: Testing {browser} browser...")
        
        # Create a test handler
        test_handler = WebCSVHandler(browser)
        
        try:
            # Try to setup the driver
            test_handler.setup_driver()
            
            # Test basic functionality
            test_handler.driver.get("https://www.google.com")
            title = test_handler.driver.title
            
            # Close the browser
            test_handler.teardown_driver()
            
            print(f"DEBUG: {browser} browser test successful")
            return jsonify({
                'success': True, 
                'message': f'{browser} browser test passed',
                'title': title
            })
            
        except Exception as e:
            print(f"DEBUG: {browser} browser test failed: {str(e)}")
            return jsonify({
                'success': False, 
                'error': str(e)
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/cleanup', methods=['POST'])
def api_cleanup():
    """Clean up old sessions and temporary files"""
    try:
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session in script_sessions.items():
            if session['status'] in ['completed', 'error', 'stopped']:
                # Remove sessions older than 1 hour
                if (current_time - session.get('end_time', current_time)).seconds > 3600:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            if session_id in script_sessions:
                session = script_sessions[session_id]
                if hasattr(session['handler'], 'driver') and session['handler'].driver:
                    try:
                        session['handler'].driver.quit()
                    except:
                        pass
                del script_sessions[session_id]
        
        return jsonify({'success': True, 'cleaned': len(sessions_to_remove)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Video Management API Endpoints
@app.route('/api/videos')
def api_videos():
    """Get list of available videos"""
    try:
        videos = get_available_videos()
        return jsonify({'success': True, 'videos': videos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/save-video', methods=['POST'])
def api_save_video():
    """Save uploaded video file"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'})
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"recording_{timestamp}_{video_file.filename}"
        filepath = os.path.join(VIDEO_DIR, filename)
        
        # Save the file
        video_file.save(filepath)
        
        return jsonify({'success': True, 'filename': filename, 'message': 'Video saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/video/<filename>')
def api_get_video(filename):
    """Serve video file"""
    try:
        filepath = os.path.join(VIDEO_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=False)
        else:
            return jsonify({'success': False, 'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download-video/<filename>')
def api_download_video(filename):
    """Download video file"""
    try:
        filepath = os.path.join(VIDEO_DIR, filename)
        if os.path.exists(filepath):
            # Send file with appropriate content type
            if filename.endswith('.mp4'):
                return send_file(filepath, as_attachment=True, download_name=filename, mimetype='video/mp4')
            elif filename.endswith('.webm'):
                return send_file(filepath, as_attachment=True, download_name=filename, mimetype='video/webm')
            else:
                return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-video/<filename>', methods=['DELETE'])
def api_delete_video(filename):
    """Delete video file"""
    try:
        filepath = os.path.join(VIDEO_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': 'Video deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clear-old-videos', methods=['DELETE'])
def api_clear_old_videos():
    """Clear videos older than 7 days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = 0
        
        for video_file in glob.glob(os.path.join(VIDEO_DIR, '*')):
            if os.path.isfile(video_file):
                file_time = datetime.fromtimestamp(os.path.getmtime(video_file))
                if file_time < cutoff_date:
                    os.remove(video_file)
                    deleted_count += 1
        
        return jsonify({'success': True, 'deleted': deleted_count, 'message': f'Cleared {deleted_count} old videos'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting AI Agent Web Server...")
    
    # Get port from environment variable (Railway) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print(f"📱 Dashboard will be available at: http://localhost:{port}")
    print("🔧 Make sure to install dependencies first!")
    
    # Start cleanup thread
    def cleanup_thread():
        while True:
            time.sleep(300)  # Cleanup every 5 minutes
            try:
                app.test_client().post('/api/cleanup')
            except:
                pass
    
    cleanup = threading.Thread(target=cleanup_thread)
    cleanup.daemon = True
    cleanup.start()
    
    # Use debug=False for production deployment
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode, threaded=True)
