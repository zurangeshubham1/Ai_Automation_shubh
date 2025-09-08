#!/usr/bin/env python3
"""
Test script to verify visible browser functionality
"""

import os
import sys
import time

# Set environment variable to force visible browser
os.environ['FORCE_VISIBLE_BROWSER'] = 'true'

def test_visible_browser():
    """Test if visible browser can be opened"""
    print("🧪 Testing Visible Browser Functionality")
    print("=" * 50)
    
    try:
        from csv_action_handler import CSVActionHandler
        
        print("✅ CSVActionHandler imported successfully")
        
        # Create handler
        handler = CSVActionHandler(browser='chrome', session_id='test')
        print("✅ Handler created successfully")
        
        # Setup driver
        print("🔧 Setting up visible browser...")
        handler.setup_driver()
        
        if handler.driver is None:
            print("❌ Failed to setup browser driver")
            return False
        
        print("✅ Browser driver setup successful")
        
        # Test basic functionality
        print("🌐 Opening Google.com...")
        handler.driver.get("https://www.google.com")
        
        title = handler.driver.title
        print(f"✅ Page loaded successfully. Title: {title}")
        
        # Wait a bit so user can see the browser
        print("⏳ Keeping browser open for 5 seconds so you can see it...")
        time.sleep(5)
        
        # Close browser
        print("🔄 Closing browser...")
        handler.teardown_driver()
        
        print("✅ Test completed successfully!")
        print("🎉 Visible browser functionality is working!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_visible_browser()
    
    if success:
        print("\n🎉 SUCCESS: Visible browser is working!")
        print("You can now use the AI Agent with visible browser windows.")
    else:
        print("\n❌ FAILED: Visible browser test failed.")
        print("Please check your browser installation and try again.")
    
    input("\nPress Enter to exit...")
