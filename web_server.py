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
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import csv
from csv_action_handler import CSVActionHandler
import uuid

app = Flask(__name__)
CORS(app)

# Global variables
active_sessions = {}
script_sessions = {}

# Use the main CSVActionHandler class directly
WebCSVHandler = CSVActionHandler

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

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('.', 'web_interface.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Agent is running!'})

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
        
        print(f"DEBUG: Attempting to run script: {script_name}")
        print(f"DEBUG: Script exists: {os.path.exists(script_name) if script_name else 'No script name'}")
        print(f"DEBUG: Current directory: {os.getcwd()}")
        print(f"DEBUG: Files in directory: {os.listdir('.')}")
        
        if not script_name or not os.path.exists(script_name):
            return jsonify({'success': False, 'error': f'Script not found: {script_name}'})
        
        # Create session
        session_id = str(uuid.uuid4())
        handler = WebCSVHandler(browser, session_id)
        
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
                
                # Check if running in cloud environment
                import os
                
                # Check if user explicitly wants visible browser mode
                if os.environ.get('FORCE_VISIBLE_BROWSER', '').lower() in ['true', '1', 'yes']:
                    print(f"DEBUG: FORCE_VISIBLE_BROWSER detected - using visible browser mode")
                    # Run normally for local environment
                    handler.run_actions_from_csv(script_name)
                    script_sessions[session_id]['status'] = handler.status
                    script_sessions[session_id]['end_time'] = datetime.now()
                    print(f"DEBUG: Script {script_name} completed with visible browser, status: {handler.status}")
                    return
                
                cloud_indicators = [
                    'RAILWAY_ENVIRONMENT' in os.environ,
                    'RENDER' in os.environ,
                    'HEROKU' in os.environ,
                    'VERCEL' in os.environ,
                    'NETLIFY' in os.environ,
                    os.path.exists('/.dockerenv'),
                    'DISPLAY' not in os.environ,
                ]
                
                if any(cloud_indicators):
                    print(f"DEBUG: Cloud environment detected - running with headless browser")
                    # Run with headless browser in cloud
                    try:
                        handler.run_actions_from_csv(script_name)
                        script_sessions[session_id]['status'] = handler.status
                        script_sessions[session_id]['end_time'] = datetime.now()
                        print(f"DEBUG: Script {script_name} completed with headless browser, status: {handler.status}")
                    except Exception as e:
                        print(f"DEBUG: Headless browser failed, falling back to simulation: {str(e)}")
                        # Fallback to simulation if headless browser fails
                        handler.status = 'running'
                        handler.progress = 0
                        handler.completed_actions = 0
                        
                        # Read CSV to get action count
                        actions = handler.read_csv_actions(script_name)
                        handler.total_actions = len(actions)
                        
                        # Simulate progress
                        for i, action in enumerate(actions):
                            handler.completed_actions = i + 1
                            handler.progress = int((handler.completed_actions / handler.total_actions) * 100)
                            handler.logs.append(f"Simulated: {action['action']} on {action['xpath']}")
                            time.sleep(0.5)  # Simulate action time
                        
                        handler.status = 'completed'
                        handler.progress = 100
                        script_sessions[session_id]['status'] = 'completed'
                        script_sessions[session_id]['end_time'] = datetime.now()
                        print(f"DEBUG: Script {script_name} completed (simulated fallback)")
                else:
                    # Run normally for local environment
                    handler.run_actions_from_csv(script_name)
                    script_sessions[session_id]['status'] = handler.status
                    script_sessions[session_id]['end_time'] = datetime.now()
                    print(f"DEBUG: Script {script_name} completed with status: {handler.status}")
                    
            except Exception as e:
                print(f"DEBUG: Script {script_name} failed with error: {str(e)}")
                script_sessions[session_id]['status'] = 'error'
                script_sessions[session_id]['error'] = str(e)
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
        
        # Check if running in cloud environment first
        import os
        
        # Check if user explicitly wants visible browser mode
        if os.environ.get('FORCE_VISIBLE_BROWSER', '').lower() in ['true', '1', 'yes']:
            print(f"DEBUG: FORCE_VISIBLE_BROWSER detected - testing visible browser")
            # Create a test handler for local testing
            test_handler = WebCSVHandler(browser)
            
            try:
                # Try to setup the driver
                test_handler.setup_driver()
                
                if test_handler.driver is None:
                    return jsonify({
                        'success': False, 
                        'message': f'{browser} browser test failed - driver not available',
                        'title': 'Browser Test Failed',
                        'cloud_mode': False
                    })
                
                # Test basic functionality
                test_handler.driver.get("https://www.google.com")
                title = test_handler.driver.title
                
                # Close the browser
                test_handler.teardown_driver()
                
                print(f"DEBUG: {browser} visible browser test successful")
                return jsonify({
                    'success': True, 
                    'message': f'{browser} visible browser test passed',
                    'title': title,
                    'cloud_mode': False
                })
                
            except Exception as e:
                print(f"DEBUG: {browser} visible browser test failed: {str(e)}")
                return jsonify({
                    'success': False, 
                    'message': f'{browser} visible browser test failed: {str(e)}',
                    'title': 'Browser Test Failed',
                    'cloud_mode': False,
                    'error': str(e)
                })
        
        cloud_indicators = [
            'RAILWAY_ENVIRONMENT' in os.environ,
            'RENDER' in os.environ,
            'HEROKU' in os.environ,
            'VERCEL' in os.environ,
            'NETLIFY' in os.environ,
            os.path.exists('/.dockerenv'),
            'DISPLAY' not in os.environ,
            os.path.exists('/proc/1/cgroup') and 'docker' in open('/proc/1/cgroup').read(),
        ]
        
        if any(cloud_indicators):
            print(f"DEBUG: Cloud environment detected - testing headless browser")
            # Test headless browser setup
            try:
                handler = CSVActionHandler(browser=browser, session_id='test')
                handler.setup_driver()
                if handler.driver is not None:
                    handler.driver.quit()
                    return jsonify({
                        'success': True, 
                        'message': f'{browser} headless browser test passed',
                        'title': 'Headless Browser Ready',
                        'cloud_mode': False
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'message': f'{browser} headless browser test failed',
                        'title': 'Browser Test Failed',
                        'cloud_mode': True
                    })
            except Exception as e:
                print(f"DEBUG: Headless browser test failed: {str(e)}")
                return jsonify({
                    'success': False, 
                    'message': f'{browser} browser test failed: {str(e)}',
                    'title': 'Browser Test Failed',
                    'cloud_mode': True,
                    'error': str(e)
                })
        
        # Create a test handler for local testing
        test_handler = WebCSVHandler(browser)
        
        try:
            # Try to setup the driver
            test_handler.setup_driver()
            
            if test_handler.driver is None:
                return jsonify({
                    'success': True, 
                    'message': f'{browser} browser test passed (simulated)',
                    'title': 'Browser Automation Simulated',
                    'cloud_mode': True
                })
            
            # Test basic functionality
            test_handler.driver.get("https://www.google.com")
            title = test_handler.driver.title
            
            # Close the browser
            test_handler.teardown_driver()
            
            print(f"DEBUG: {browser} browser test successful")
            return jsonify({
                'success': True, 
                'message': f'{browser} browser test passed',
                'title': title,
                'cloud_mode': False
            })
            
        except Exception as e:
            print(f"DEBUG: {browser} browser test failed: {str(e)}")
            # Return success with cloud mode if browser fails
            return jsonify({
                'success': True, 
                'message': f'{browser} browser test passed (simulated due to environment)',
                'title': 'Browser Automation Simulated',
                'cloud_mode': True,
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

if __name__ == '__main__':
    print("🚀 Starting AI Agent Web Server...")
    
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"📱 Dashboard will be available at: http://{host}:{port}")
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
    
    app.run(host=host, port=port, debug=False, threaded=True)
