#!/usr/bin/env python3
"""
CSV Action Handler - Handles actions from CSV file when automatic recording fails
"""

import csv
import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import allure
from allure_commons.types import AttachmentType
try:
    import cv2
    import numpy as np
    VIDEO_RECORDING_AVAILABLE = True
except ImportError:
    VIDEO_RECORDING_AVAILABLE = False
    print("⚠️ OpenCV not available - video recording disabled")

import threading
import queue

class CSVActionHandler:
    """Handles actions from CSV file"""
    
    def __init__(self, browser='chrome', session_id=None):
        self.driver = None
        self.wait = None
        self.test_results = []
        self.screenshots_dir = "allure-results/screenshots"
        self.videos_dir = "videos"
        self.browser = browser
        self.session_id = session_id or f"session_{int(time.time())}"
        self.progress = 0
        self.status = 'ready'
        self.current_action = ''
        self.logs = []
        self.completed_actions = 0
        self.total_actions = 0
        
        # Video recording setup
        self.video_recorder = None
        self.recording_started = False
        self.video_path = None
        
        self.ensure_directories()
    
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs("allure-results", exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
        
    def setup_driver(self):
        """Setup browser driver based on selected browser"""
        try:
            # Check if running in cloud environment
            if self._is_cloud_environment():
                print("☁️ Running in cloud environment - setting up headless browser")
                if self._setup_headless_browser(self.browser):
                    print("✅ Headless browser setup successful - real automation enabled")
                    return
                else:
                    print("❌ Failed to setup headless browser - falling back to simulation")
                    self.driver = None
                    self.wait = None
                    return
            
            if self.browser.lower() == 'chrome':
                self._setup_chrome()
            elif self.browser.lower() == 'firefox':
                self._setup_firefox()
            elif self.browser.lower() == 'edge':
                self._setup_edge()
            else:
                print(f"⚠️ Unknown browser: {self.browser}, defaulting to Chrome")
                self._setup_chrome()
            
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 20)
            print(f"🌐 {self.browser.capitalize()} browser opened successfully!")
            
            # Initialize video recording
            self._setup_video_recording()
            
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            print("☁️ This might be due to cloud environment limitations")
            self.driver = None
            self.wait = None
    
    def _is_cloud_environment(self):
        """Check if running in cloud environment"""
        import os
        
        # Check if user explicitly wants visible browser mode
        if os.environ.get('FORCE_VISIBLE_BROWSER', '').lower() in ['true', '1', 'yes']:
            print("🔧 FORCE_VISIBLE_BROWSER detected - using visible browser mode")
            return False
        
        cloud_indicators = [
            'RAILWAY_ENVIRONMENT' in os.environ,
            'RENDER' in os.environ,
            'HEROKU' in os.environ,
            'VERCEL' in os.environ,
            'NETLIFY' in os.environ,
            os.path.exists('/.dockerenv'),  # Docker container
            'DISPLAY' not in os.environ,   # No display available
        ]
        return any(cloud_indicators)
    
    def _setup_headless_browser(self, browser_type='chrome'):
        """Setup headless browser for cloud environments"""
        try:
            if browser_type.lower() == 'chrome':
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-plugins')
                chrome_options.add_argument('--disable-images')
                chrome_options.add_argument('--remote-debugging-port=9222')
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                # Set Chrome binary path for Railway/cloud environments
                chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
                if os.path.exists(chrome_bin):
                    chrome_options.binary_location = chrome_bin
                    print(f"✅ Using Chrome binary: {chrome_bin}")
                else:
                    print(f"⚠️ Chrome binary not found at {chrome_bin}, using default")
                
                # Additional options for Railway/cloud deployment
                chrome_options.add_argument('--disable-background-timer-throttling')
                chrome_options.add_argument('--disable-backgrounding-occluded-windows')
                chrome_options.add_argument('--disable-renderer-backgrounding')
                chrome_options.add_argument('--disable-features=TranslateUI')
                chrome_options.add_argument('--disable-ipc-flooding-protection')
                chrome_options.add_argument('--disable-logging')
                chrome_options.add_argument('--disable-default-apps')
                chrome_options.add_argument('--disable-sync')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-extensions')
                chrome_options.add_argument('--disable-plugins')
                chrome_options.add_argument('--disable-images')
                chrome_options.add_argument('--disable-javascript')
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=VizDisplayCompositor')
                chrome_options.add_argument('--remote-debugging-port=9222')
                chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                
                # Try multiple approaches to setup Chrome
                driver_setup_success = False
                
                # Method 1: Try system chromedriver (most reliable for Railway)
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    driver_setup_success = True
                    print("✅ Chrome driver setup with system chromedriver")
                except Exception as e:
                    print(f"⚠️ System chromedriver failed: {e}")
                
                # Method 2: Try ChromeDriverManager
                if not driver_setup_success:
                    try:
                        service = Service(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        driver_setup_success = True
                        print("✅ Chrome driver setup with ChromeDriverManager")
                    except Exception as e:
                        print(f"⚠️ ChromeDriverManager failed: {e}")
                
                # Method 3: Try with xvfb-run (for headless environments)
                if not driver_setup_success:
                    try:
                        chrome_options.add_argument('--display=:99')
                        self.driver = webdriver.Chrome(options=chrome_options)
                        driver_setup_success = True
                        print("✅ Chrome driver setup with xvfb")
                    except Exception as e:
                        print(f"⚠️ xvfb setup failed: {e}")
                
                # Method 4: Try with minimal options (fallback)
                if not driver_setup_success:
                    try:
                        minimal_options = Options()
                        minimal_options.add_argument('--headless')
                        minimal_options.add_argument('--no-sandbox')
                        minimal_options.add_argument('--disable-dev-shm-usage')
                        minimal_options.add_argument('--disable-gpu')
                        minimal_options.add_argument('--window-size=1920,1080')
                        if os.path.exists(chrome_bin):
                            minimal_options.binary_location = chrome_bin
                        self.driver = webdriver.Chrome(options=minimal_options)
                        driver_setup_success = True
                        print("✅ Chrome driver setup with minimal options")
                    except Exception as e:
                        print(f"⚠️ Minimal options setup failed: {e}")
                
                if not driver_setup_success:
                    # Log system information for debugging
                    import platform
                    import subprocess
                    print(f"❌ All Chrome driver setup methods failed")
                    print(f"System: {platform.system()} {platform.release()}")
                    print(f"Python: {platform.python_version()}")
                    try:
                        result = subprocess.run(['which', 'chromium'], capture_output=True, text=True)
                        print(f"Chromium path: {result.stdout.strip()}")
                    except:
                        print("Chromium not found in PATH")
                    try:
                        result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
                        print(f"ChromeDriver path: {result.stdout.strip()}")
                    except:
                        print("ChromeDriver not found in PATH")
                    raise Exception("All Chrome driver setup methods failed")
                print(f"✅ Headless Chrome browser started successfully")
                
            elif browser_type.lower() == 'firefox':
                from selenium import webdriver
                from selenium.webdriver.firefox.options import Options
                from webdriver_manager.firefox import GeckoDriverManager
                from selenium.webdriver.firefox.service import Service
                
                firefox_options = Options()
                firefox_options.add_argument('--headless')
                firefox_options.add_argument('--no-sandbox')
                firefox_options.add_argument('--disable-dev-shm-usage')
                
                service = Service(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=firefox_options)
                print(f"✅ Headless Firefox browser started successfully")
                
            elif browser_type.lower() == 'edge':
                from selenium import webdriver
                from selenium.webdriver.edge.options import Options
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                from selenium.webdriver.edge.service import Service
                
                edge_options = Options()
                edge_options.add_argument('--headless')
                edge_options.add_argument('--no-sandbox')
                edge_options.add_argument('--disable-dev-shm-usage')
                edge_options.add_argument('--disable-gpu')
                edge_options.add_argument('--window-size=1920,1080')
                
                service = Service(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=edge_options)
                print(f"✅ Headless Edge browser started successfully")
            
            self.wait = WebDriverWait(self.driver, 10)
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup headless {browser_type} browser: {str(e)}")
            return False
    
    def _setup_chrome(self):
        """Setup Chrome driver"""
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _setup_firefox(self):
        """Setup Firefox driver"""
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        from webdriver_manager.firefox import GeckoDriverManager
        
        options = Options()
        options.add_argument('--start-maximized')
        
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=options)
    
    def _setup_edge(self):
        """Setup Edge driver"""
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.edge.service import Service
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _setup_video_recording(self):
        """Setup video recording for the session"""
        if not VIDEO_RECORDING_AVAILABLE:
            print("⚠️ Video recording not available - OpenCV not installed")
            self.recording_started = False
            return
            
        try:
            # Create video recorder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"automation_{self.session_id}_{timestamp}.mp4"
            self.video_path = os.path.join(self.videos_dir, video_filename)
            
            # Initialize video writer with better codec
            # Try different codecs for better compatibility
            codecs_to_try = [
                ('mp4v', cv2.VideoWriter_fourcc(*'mp4v')),
                ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
                ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
                ('H264', cv2.VideoWriter_fourcc(*'H264'))
            ]
            
            self.video_writer = None
            for codec_name, fourcc in codecs_to_try:
                try:
                    self.video_writer = cv2.VideoWriter(
                        self.video_path, 
                        fourcc, 
                        2,  # 2 FPS for reasonable file size
                        (1920, 1080)
                    )
                    if self.video_writer.isOpened():
                        print(f"🎥 Video recording started with {codec_name} codec: {self.video_path}")
                        break
                    else:
                        self.video_writer.release()
                        self.video_writer = None
                except Exception as e:
                    print(f"⚠️ Failed to initialize {codec_name} codec: {e}")
                    continue
            
            if self.video_writer is None:
                print("❌ Failed to initialize any video codec")
                self.recording_started = False
            else:
                self.recording_started = True
            
        except Exception as e:
            print(f"⚠️ Video recording setup failed: {e}")
            self.recording_started = False
    
    def _capture_video_frame(self, action_name=""):
        """Capture a frame for video recording"""
        if not VIDEO_RECORDING_AVAILABLE or not self.recording_started or not self.driver or not self.video_writer:
            return
        
        try:
            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()
            
            # Convert to OpenCV format
            nparr = np.frombuffer(screenshot, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                print("⚠️ Failed to decode screenshot")
                return
            
            # Resize frame to exact dimensions
            frame = cv2.resize(frame, (1920, 1080))
            
            # Ensure frame is in correct format (BGR)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # Add action text overlay
                if action_name:
                    cv2.putText(frame, f"Action: {action_name}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Add timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, 
                           (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add URL
                url = self.driver.current_url
                if len(url) > 50:
                    url = url[:47] + "..."
                cv2.putText(frame, url, 
                           (10, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Write frame to video
                self.video_writer.write(frame)
            else:
                print("⚠️ Invalid frame format")
            
        except Exception as e:
            print(f"⚠️ Failed to capture video frame: {e}")
    
    def teardown_driver(self):
        """Close browser and stop video recording"""
        if self.recording_started and self.video_writer:
            try:
                self.video_writer.release()
                self.video_writer = None
                self.recording_started = False
                
                # Verify video file was created and has content
                if os.path.exists(self.video_path):
                    file_size = os.path.getsize(self.video_path)
                    if file_size > 0:
                        print(f"🎬 Video recording completed: {self.video_path} ({round(file_size / 1024, 2)} KB)")
                    else:
                        print(f"⚠️ Video file created but is empty: {self.video_path}")
                        # Remove empty file
                        os.remove(self.video_path)
                else:
                    print(f"⚠️ Video file was not created: {self.video_path}")
            except Exception as e:
                print(f"⚠️ Error closing video recording: {e}")
        
        if self.driver:
            time.sleep(3)  # Keep browser open for 3 seconds
            self.driver.quit()
            print("🔄 Browser closed")
    
    def take_screenshot(self, step_name):
        """Take screenshot and attach to Allure report"""
        if self.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.screenshots_dir, f"{step_name}_{timestamp}.png")
            self.driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, name=step_name, attachment_type=AttachmentType.PNG)
            
            # Log screenshot info for live monitoring
            page_info = {
                'url': self.driver.current_url,
                'title': self.driver.title,
                'timestamp': timestamp,
                'action': step_name,
                'screenshot_path': screenshot_path
            }
            self.logs.append(f"📸 Screenshot taken: {step_name} - {self.driver.current_url}")
            
            return screenshot_path
        return None
    
    def generate_allure_report(self, test_name, actions, success):
        """Generate Allure report"""
        allure_results_dir = "allure-results"
        
        # Create test result JSON
        test_result = {
            "uuid": f"test-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": test_name,
            "fullName": f"CSV Action Test: {test_name}",
            "status": "passed" if success else "failed",
            "stage": "finished",
            "start": int(datetime.now().timestamp() * 1000),
            "stop": int(datetime.now().timestamp() * 1000),
            "steps": []
        }
        
        # Add steps to test result
        for i, action in enumerate(actions):
            step = {
                "name": f"Step {i+1}: {action['action']} on {action['xpath']}",
                "status": "passed" if action.get('success', True) else "failed",
                "stage": "finished",
                "start": int(datetime.now().timestamp() * 1000),
                "stop": int(datetime.now().timestamp() * 1000)
            }
            test_result["steps"].append(step)
        
        # Save test result
        result_file = os.path.join(allure_results_dir, f"{test_result['uuid']}-result.json")
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)
        
        print(f"📊 Allure report data saved: {result_file}")
        return result_file
    
    def parse_selector(self, selector):
        """Parse selector string into Selenium By object"""
        if selector.startswith('#'):
            return (By.ID, selector[1:])
        elif selector.startswith('.'):
            return (By.CLASS_NAME, selector[1:])
        elif selector.startswith('xpath='):
            return (By.XPATH, selector[6:])
        elif selector.startswith('css='):
            return (By.CSS_SELECTOR, selector[4:])
        elif selector.startswith('name='):
            return (By.NAME, selector[5:])
        elif selector.startswith('text='):
            text = selector[5:]
            return (By.XPATH, f"//*[contains(text(), '{text}')]")
        else:
            # Assume it's an XPath if it starts with //
            if selector.startswith('//'):
                return (By.XPATH, selector)
            else:
                return (By.ID, selector)
    
    def execute_action(self, action, xpath, data=""):
        """Execute a single action with Allure reporting and progress tracking"""
        step_name = f"{action}_{xpath.replace('//', '').replace('@', '').replace('=', '_')[:20]}"
        self.current_action = f"{action} on {xpath}"
        self.logs.append(f"Executing: {self.current_action}")
        print(f"🔄 Executing: {action} on {xpath}")
        
        # Check if running in cloud environment
        # Check if we have a real browser driver (headless or regular)
        if self.driver is None and action not in ['wait', 'verify']:
            print(f"☁️ No browser available: Simulating {action} action")
            self.logs.append(f"Simulated: {self.current_action}")
            time.sleep(1)  # Simulate action time
            return True
        
        # Take screenshot before action
        self.take_screenshot(f"before_{step_name}")
        
        # Capture video frame before action
        self._capture_video_frame(f"Before: {action}")
        
        try:
            if action.lower() == 'open_url':
                self.driver.get(xpath)
                time.sleep(2)
                print(f"   ✅ Opened URL: {xpath}")
                
            elif action.lower() == 'type' or action.lower() == 'type_text':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                element.clear()
                element.send_keys(data)
                print(f"   ✅ Typed '{data}' in {xpath}")
                
            elif action.lower() == 'click':
                element = self.wait.until(EC.element_to_be_clickable(self.parse_selector(xpath)))
                element.click()
                print(f"   ✅ Clicked {xpath}")
                
            elif action.lower() == 'verify' or action.lower() == 'verify_text':
                if xpath.startswith('text='):
                    text = xpath.replace('text=', '')
                    element = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{text}')]"))
                    )
                else:
                    element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                print(f"   ✅ Verified {xpath}")
                
            elif action.lower() == 'wait':
                seconds = int(data) if data.isdigit() else 5
                time.sleep(seconds)
                print(f"   ✅ Waited {seconds} seconds")
                
            elif action.lower() == 'select_dropdown' or action.lower() == 'select':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                from selenium.webdriver.support.ui import Select
                select = Select(element)
                select.select_by_visible_text(data)
                print(f"   ✅ Selected '{data}' from dropdown {xpath}")
                
            elif action.lower() == 'upload_file' or action.lower() == 'upload':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                element.send_keys(data)  # data should be the full file path
                print(f"   ✅ Uploaded file '{data}' to {xpath}")
                
            elif action.lower() == 'wait_for_element':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                print(f"   ✅ Element {xpath} is now present")
                
            elif action.lower() == 'wait_for_clickable':
                element = self.wait.until(EC.element_to_be_clickable(self.parse_selector(xpath)))
                print(f"   ✅ Element {xpath} is now clickable")
                
            elif action.lower() == 'wait_for_visible':
                element = self.wait.until(EC.visibility_of_element_located(self.parse_selector(xpath)))
                print(f"   ✅ Element {xpath} is now visible")
                
            elif action.lower() == 'clear':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                element.clear()
                print(f"   ✅ Cleared field {xpath}")
                
            elif action.lower() == 'double_click':
                element = self.wait.until(EC.element_to_be_clickable(self.parse_selector(xpath)))
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).double_click(element).perform()
                print(f"   ✅ Double clicked {xpath}")
                
            elif action.lower() == 'right_click':
                element = self.wait.until(EC.element_to_be_clickable(self.parse_selector(xpath)))
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).context_click(element).perform()
                print(f"   ✅ Right clicked {xpath}")
                
            elif action.lower() == 'hover':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).move_to_element(element).perform()
                print(f"   ✅ Hovered over {xpath}")
                
            elif action.lower() == 'scroll_to':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                print(f"   ✅ Scrolled to {xpath}")
                
            elif action.lower() == 'switch_to_frame':
                if xpath:
                    element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                    self.driver.switch_to.frame(element)
                else:
                    self.driver.switch_to.frame(data)  # data should be frame name or index
                print(f"   ✅ Switched to frame {xpath or data}")
                
            elif action.lower() == 'switch_to_default':
                self.driver.switch_to.default_content()
                print(f"   ✅ Switched to default content")
                
            elif action.lower() == 'js_click':
                element = self.wait.until(EC.presence_of_element_located(self.parse_selector(xpath)))
                self.driver.execute_script("arguments[0].click();", element)
                print(f"   ✅ JavaScript clicked {xpath}")
                
            elif action.lower() == 'execute_js':
                # Execute custom JavaScript code
                result = self.driver.execute_script(xpath)
                print(f"   ✅ Executed JavaScript: {xpath}")
                if result:
                    print(f"   📄 Result: {result}")
                
            else:
                print(f"   ⚠️ Unknown action: {action}")
            
            # Take screenshot after successful action
            self.take_screenshot(f"after_{step_name}")
            
            # Capture video frame after action
            self._capture_video_frame(f"After: {action}")
            
            # Update progress
            if hasattr(self, 'total_actions') and self.total_actions > 0:
                self.completed_actions += 1
                self.progress = int((self.completed_actions / self.total_actions) * 100)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            # Take screenshot on failure
            self.take_screenshot(f"failed_{step_name}")
            # Capture error frame
            self._capture_video_frame(f"Error: {action}")
            self.status = 'error'
            return False
    
    def read_csv_actions(self, csv_file):
        """Read actions from CSV file"""
        actions = []
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return actions
        
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    action = row.get('action', '').strip()
                    xpath = row.get('xpath', '').strip()
                    data = row.get('data', '').strip()
                    
                    if action and xpath:
                        actions.append({
                            'row': row_num,
                            'action': action,
                            'xpath': xpath,
                            'data': data
                        })
                    else:
                        print(f"⚠️ Skipping row {row_num}: missing action or xpath")
        
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
        
        return actions
    
    def run_actions_from_csv(self, csv_file):
        """Run actions from CSV file with Allure reporting and progress tracking"""
        test_name = os.path.splitext(os.path.basename(csv_file))[0]
        print(f"🚀 Running actions from CSV: {csv_file}")
        
        # Initialize progress tracking
        self.status = 'running'
        self.progress = 0
        self.completed_actions = 0
        
        # Read actions from CSV
        actions = self.read_csv_actions(csv_file)
        
        if not actions:
            print("❌ No valid actions found in CSV file")
            self.status = 'error'
            return False
        
        self.total_actions = len(actions)
        print(f"📋 Found {len(actions)} actions to execute")
        
        # Setup browser
        try:
            self.setup_driver()
            if self.driver is None:
                print("❌ Browser setup failed - cannot proceed with automation")
                self.status = 'error'
                return False
        except Exception as e:
            print(f"❌ Browser setup error: {e}")
            self.status = 'error'
            return False
        
        # Initialize Allure test
        with allure.step(f"CSV Action Test: {test_name}"):
            try:
                # Execute each action
                for i, action_data in enumerate(actions, 1):
                    with allure.step(f"Step {i}: {action_data['action']} on {action_data['xpath']}"):
                        print(f"\n📝 Step {i}/{len(actions)}: {action_data['action']} on {action_data['xpath']}")
                        success = self.execute_action(
                            action_data['action'], 
                            action_data['xpath'], 
                            action_data['data']
                        )
                        
                        # Store result for Allure report
                        action_data['success'] = success
                        
                        if not success:
                            print(f"❌ Test failed at step {i}")
                            allure.attach(f"Test failed at step {i}: {action_data['action']} on {action_data['xpath']}", 
                                        name="Test Failure", attachment_type=AttachmentType.TEXT)
                            return False
                
                print(f"\n🎉 ALL ACTIONS COMPLETED! Test passed successfully!")
                self.status = 'completed'
                self.progress = 100
                allure.attach("All actions completed successfully", 
                            name="Test Success", attachment_type=AttachmentType.TEXT)
                return True
                
            except Exception as e:
                error_msg = f"Test failed with error: {e}"
                print(f"❌ {error_msg}")
                self.status = 'error'
                self.logs.append(error_msg)
                self.logs.append(f"Error details: {type(e).__name__}: {str(e)}")
                allure.attach(f"Test failed with error: {e}", 
                            name="Test Error", attachment_type=AttachmentType.TEXT)
                return False
            
            finally:
                self.teardown_driver()
                
                # Generate Allure report
                self.generate_allure_report(test_name, actions, True)
                
                # Log video information
                if self.video_path and os.path.exists(self.video_path):
                    file_size = os.path.getsize(self.video_path)
                    self.logs.append(f"🎬 Video recorded: {self.video_path} ({round(file_size / (1024 * 1024), 2)} MB)")
    
    def get_video_info(self):
        """Get information about the recorded video"""
        if self.video_path and os.path.exists(self.video_path):
            file_size = os.path.getsize(self.video_path)
            return {
                'path': self.video_path,
                'filename': os.path.basename(self.video_path),
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'exists': True,
                'session_id': self.session_id
            }
        return {'exists': False}
    
    def create_sample_csv(self, test_name):
        """Create a sample CSV file for the user"""
        csv_file = f"{test_name}_actions.csv"
        
        sample_data = [
            {'action': 'open_url', 'xpath': 'https://example.com/login', 'data': ''},
            {'action': 'type', 'xpath': '//input[@id="username"]', 'data': 'admin'},
            {'action': 'type', 'xpath': '//input[@id="password"]', 'data': 'password123'},
            {'action': 'click', 'xpath': '//button[@id="loginButton"]', 'data': ''},
            {'action': 'verify', 'xpath': 'text=Welcome', 'data': ''},
        ]
        
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['action', 'xpath', 'data']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in sample_data:
                    writer.writerow(row)
            
            print(f"✅ Sample CSV created: {csv_file}")
            print("📋 CSV Format:")
            print("   action,xpath,data")
            print("   open_url,https://example.com/login,")
            print("   type,//input[@id='username'],admin")
            print("   type,//input[@id='password'],password123")
            print("   click,//button[@id='loginButton'],")
            print("   verify,text=Welcome,")
            
            return csv_file
            
        except Exception as e:
            print(f"❌ Error creating sample CSV: {e}")
            return None
    
    def generate_allure_html_report(self):
        """Generate HTML Allure report"""
        try:
            import subprocess
            import shutil
            
            # Try to find allure command
            allure_cmd = shutil.which('allure')
            if not allure_cmd:
                # Try common installation paths
                possible_paths = [
                    r'C:\Users\%USERNAME%\scoop\apps\allure\current\bin\allure.bat',
                    r'C:\ProgramData\scoop\apps\allure\current\bin\allure.bat',
                    r'C:\allure\bin\allure.bat'
                ]
                
                for path in possible_paths:
                    expanded_path = os.path.expandvars(path)
                    if os.path.exists(expanded_path):
                        allure_cmd = expanded_path
                        break
            
            if not allure_cmd:
                print("❌ Allure command not found. Please install Allure CLI:")
                print("   Download from: https://docs.qameta.io/allure/#_installing_a_commandline")
                return False
            
            print(f"🔍 Using Allure command: {allure_cmd}")
            
            result = subprocess.run([allure_cmd, 'generate', 'allure-results', '--clean', '-o', 'allure-report'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("📊 Allure HTML report generated successfully!")
                print("🌐 Open report: allure-report/index.html")
                return True
            else:
                print(f"❌ Error generating Allure report: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error generating Allure report: {e}")
            return False

def main():
    """Main entry point"""
    handler = CSVActionHandler()
    
    if len(os.sys.argv) > 1:
        csv_file = os.sys.argv[1]
        success = handler.run_actions_from_csv(csv_file)
        
        if success:
            print("\n🚀 Test completed successfully!")
        else:
            print("\n❌ Test failed!")
        
        # Generate Allure HTML report
        print("\n📊 Generating Allure report...")
        handler.generate_allure_html_report()
    else:
        print("🤖 CSV Action Handler")
        print("=" * 30)
        print()
        print("This tool runs actions from a CSV file when automatic recording fails.")
        print()
        print("CSV Format:")
        print("   action,xpath,data")
        print("   open_url,https://example.com/login,")
        print("   type,//input[@id='username'],admin")
        print("   type,//input[@id='password'],password123")
        print("   click,//button[@id='loginButton'],")
        print("   verify,text=Welcome,")
        print()
        print("Usage:")
        print("   python csv_action_handler.py <csv_file>")
        print()
        print("Examples:")
        print("   python csv_action_handler.py my_test_actions.csv")
        print()
        
        # Ask if user wants to create a sample CSV
        create_sample = input("Would you like to create a sample CSV file? (y/n): ").strip().lower()
        if create_sample == 'y':
            test_name = input("Enter test name for sample CSV: ").strip()
            if not test_name:
                test_name = "sample_test"
            
            csv_file = handler.create_sample_csv(test_name)
            if csv_file:
                print(f"\n📁 Sample CSV created: {csv_file}")
                print("   Edit this file with your actual actions and XPaths")
                print(f"   Then run: python csv_action_handler.py {csv_file}")

if __name__ == "__main__":
    main()
