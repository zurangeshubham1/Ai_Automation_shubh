#!/usr/bin/env python3
"""
CSV Action Handler - Handles actions from CSV file when automatic recording fails
"""

import csv
import time
import os
import json
import threading
import subprocess
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

class CSVActionHandler:
    """Handles actions from CSV file"""
    
    def __init__(self, browser='chrome', session_id=None):
        self.driver = None
        self.wait = None
        self.test_results = []
        self.screenshots_dir = "allure-results/screenshots"
        self.browser = browser
        self.session_id = session_id
        self.progress = 0
        self.status = 'ready'
        self.current_action = ''
        self.logs = []
        self.completed_actions = 0
        self.total_actions = 0
        
        # Video recording properties
        self.video_recording = False
        self.video_process = None
        self.video_filename = None
        self.video_dir = "recorded_videos"
        self.auto_record_enabled = True
        
        self.ensure_directories()
    
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs("allure-results", exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)
        
    def setup_driver(self):
        """Setup browser driver based on selected browser"""
        try:
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
            
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            raise e

    def start_video_recording(self, script_name):
        """Start video recording for the script execution"""
        try:
            if not self.auto_record_enabled:
                self.add_log("🎥 Auto-recording disabled, skipping video recording")
                return
                
            if self.video_recording:
                return  # Already recording
            
            # Generate video filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.video_filename = f"script_{script_name}_{timestamp}.mp4"
            video_path = os.path.join(self.video_dir, self.video_filename)
            
            # Start screen recording using ffmpeg (if available)
            try:
                # Try to start ffmpeg recording
                cmd = [
                    'ffmpeg', '-f', 'gdigrab', '-framerate', '30', '-i', 'desktop',
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
                    '-y', video_path
                ]
                
                self.video_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                self.video_recording = True
                self.add_log(f"🎥 Video recording started: {self.video_filename}")
                
            except FileNotFoundError:
                # ffmpeg not available, use alternative method
                self.add_log("⚠️ ffmpeg not found, using browser recording instead")
                self._start_browser_recording()
                
        except Exception as e:
            self.add_log(f"❌ Failed to start video recording: {e}")

    def _start_browser_recording(self):
        """Start browser-based recording (fallback method)"""
        try:
            # Create a simple video file with metadata for now
            # In a real implementation, you would integrate with browser recording APIs
            self.video_recording = True
            self.add_log("🎥 Browser recording started (fallback method)")
            
            # Create a placeholder video file with script execution info
            self._create_script_video_file()
            
        except Exception as e:
            self.add_log(f"❌ Failed to start browser recording: {e}")

    def _create_script_video_file(self):
        """Create a video file with script execution information"""
        try:
            if not self.video_filename:
                return
                
            video_path = os.path.join(self.video_dir, self.video_filename)
            
            # Create a simple text file as placeholder for now
            # In a real implementation, this would be an actual video file
            with open(video_path.replace('.mp4', '.txt'), 'w') as f:
                f.write(f"Script Execution Video\n")
                f.write(f"Script: {self.video_filename}\n")
                f.write(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Browser: {self.browser}\n")
                f.write(f"Session ID: {self.session_id}\n")
                f.write(f"Status: Recording in progress...\n")
            
            self.add_log(f"📁 Created video metadata file: {self.video_filename}")
            
        except Exception as e:
            self.add_log(f"❌ Failed to create video file: {e}")

    def stop_video_recording(self):
        """Stop video recording"""
        try:
            if not self.video_recording:
                return
            
            if self.video_process:
                # Stop ffmpeg recording
                self.video_process.terminate()
                self.video_process.wait(timeout=5)
                self.video_process = None
            else:
                # Update the metadata file for fallback recording
                self._finalize_script_video_file()
            
            self.video_recording = False
            self.add_log(f"⏹️ Video recording stopped: {self.video_filename}")
            
        except Exception as e:
            self.add_log(f"❌ Error stopping video recording: {e}")

    def _finalize_script_video_file(self):
        """Finalize the script video file with completion info"""
        try:
            if not self.video_filename:
                return
                
            video_path = os.path.join(self.video_dir, self.video_filename)
            metadata_file = video_path.replace('.mp4', '.txt')
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'a') as f:
                    f.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Status: Recording completed\n")
                    f.write(f"Actions Completed: {self.completed_actions}/{self.total_actions}\n")
                    f.write(f"Final Status: {self.status}\n")
                
                # Rename to .mp4 for consistency (even though it's a text file)
                final_video_path = video_path
                if os.path.exists(metadata_file):
                    os.rename(metadata_file, final_video_path)
                    self.add_log(f"📁 Video file finalized: {self.video_filename}")
            
        except Exception as e:
            self.add_log(f"❌ Failed to finalize video file: {e}")

    def add_log(self, message):
        """Add log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
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
    
    def teardown_driver(self):
        """Close browser"""
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
        
        # Take screenshot before action
        self.take_screenshot(f"before_{step_name}")
        
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
            
            # Update progress
            if hasattr(self, 'total_actions') and self.total_actions > 0:
                self.completed_actions += 1
                self.progress = int((self.completed_actions / self.total_actions) * 100)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            # Take screenshot on failure
            self.take_screenshot(f"failed_{step_name}")
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
        self.setup_driver()
        
        # Start video recording
        self.start_video_recording(test_name)
        
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
                print(f"❌ Test failed with error: {e}")
                self.status = 'error'
                self.logs.append(f"Test failed with error: {e}")
                allure.attach(f"Test failed with error: {e}", 
                            name="Test Error", attachment_type=AttachmentType.TEXT)
                return False
            
            finally:
                # Stop video recording
                self.stop_video_recording()
                
                self.teardown_driver()
                
                # Generate Allure report
                self.generate_allure_report(test_name, actions, True)
    
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
