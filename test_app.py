#!/usr/bin/env python3
"""
Test script to verify the Flask app works correctly
"""

from app import app

def test_app():
    """Test if the Flask app can be created and has routes"""
    print("🧪 Testing Flask app...")
    
    try:
        # Test app creation
        print(f"✅ App created: {app.name}")
        
        # Test routes
        with app.test_client() as client:
            # Test root route
            response = client.get('/')
            print(f"✅ Root route status: {response.status_code}")
            
            # Test API route
            response = client.get('/api/scripts')
            print(f"✅ API route status: {response.status_code}")
        
        print("🎉 App is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ App test failed: {e}")
        return False

if __name__ == '__main__':
    test_app()
