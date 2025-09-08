import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Browser settings
    BROWSER = os.getenv('BROWSER', 'chrome')
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    WINDOW_SIZE = os.getenv('WINDOW_SIZE', '1920,1080')
    
    # Test settings
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '20'))
    SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    
    # AI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    
    # Paths
    REPORTS_DIR = 'reports'
    SCREENSHOTS_DIR = 'screenshots'
    FEATURES_DIR = 'features'
    STEPS_DIR = 'features/steps'
    
    # Create directories if they don't exist
    for directory in [REPORTS_DIR, SCREENSHOTS_DIR, FEATURES_DIR, STEPS_DIR]:
        os.makedirs(directory, exist_ok=True)
