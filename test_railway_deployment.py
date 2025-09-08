#!/usr/bin/env python3
"""
Test script to verify Railway deployment functionality
"""

import os
import sys
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"⚠️ OpenCV import failed: {e} (video recording will be disabled)")
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"⚠️ NumPy import failed: {e}")
    
    return True

def test_environment():
    """Test environment variables and configuration"""
    print("\n🧪 Testing environment...")
    
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    # Check if we're in a cloud environment
    cloud_indicators = ['RAILWAY_ENVIRONMENT', 'PORT', 'DYNO']
    is_cloud = any(os.environ.get(indicator) for indicator in cloud_indicators)
    print(f"Cloud environment detected: {is_cloud}")
    
    if is_cloud:
        print("☁️ Running in cloud environment")
        for indicator in cloud_indicators:
            value = os.environ.get(indicator)
            if value:
                print(f"  {indicator}: {value}")
    
    return True

def test_browser_setup():
    """Test browser setup without actually opening browser"""
    print("\n🧪 Testing browser setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        print("✅ Chrome options configured successfully")
        
        # Try to create driver (this might fail in Railway)
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ Chrome driver created successfully")
            driver.quit()
            return True
        except Exception as e:
            print(f"⚠️ Chrome driver creation failed: {e}")
            print("💡 This is expected in Railway if Chrome is not installed")
            return False
            
    except Exception as e:
        print(f"❌ Browser setup test failed: {e}")
        return False

def test_csv_handler():
    """Test CSV action handler initialization"""
    print("\n🧪 Testing CSV action handler...")
    
    try:
        from csv_action_handler import CSVActionHandler
        
        handler = CSVActionHandler()
        print("✅ CSVActionHandler initialized successfully")
        
        # Test CSV reading
        if os.path.exists('sample_actions.csv'):
            actions = handler.read_csv_actions('sample_actions.csv')
            print(f"✅ CSV reading test passed - found {len(actions)} actions")
        else:
            print("⚠️ sample_actions.csv not found")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV handler test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Railway Deployment Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_browser_setup,
        test_csv_handler
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Railway deployment should work.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
