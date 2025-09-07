@echo off
echo 🧹 AI Agent Project Cleanup
echo ===========================
echo.

echo Removing unnecessary files...
echo.

REM Remove temporary/test files
if exist "browser_test.py" (
    del "browser_test.py"
    echo ✅ Removed browser_test.py
)

if exist "test_script.csv" (
    del "test_script.csv"
    echo ✅ Removed test_script.csv
)

if exist "demo_script.csv" (
    del "demo_script.csv"
    echo ✅ Removed demo_script.csv
)

if exist "fix_and_restart.bat" (
    del "fix_and_restart.bat"
    echo ✅ Removed fix_and_restart.bat
)

if exist "config.py" (
    del "config.py"
    echo ✅ Removed config.py
)

if exist "restart_server.bat" (
    del "restart_server.bat"
    echo ✅ Removed restart_server.bat
)

REM Remove cache folders
if exist "__pycache__" (
    rmdir /s /q "__pycache__"
    echo ✅ Removed __pycache__ folder
)

if exist "allure-report" (
    rmdir /s /q "allure-report"
    echo ✅ Removed old allure-report folder
)

if exist "allure-results" (
    rmdir /s /q "allure-results"
    echo ✅ Removed old allure-results folder
)

echo.
echo 🎉 Cleanup completed!
echo.
echo 📁 Remaining essential files:
echo    - web_interface.html (Web dashboard)
echo    - web_server.py (Backend server)
echo    - csv_action_handler.py (Automation engine)
echo    - start_web_interface.py (Startup script)
echo    - start_web_interface.bat (Windows launcher)
echo    - sample_actions.csv (Your script)
echo    - enhanced_sample_actions.csv (Your enhanced script)
echo    - README.md (Documentation)
echo    - requirements.txt (Dependencies)
echo.
echo Optional documentation files (can be removed if not needed):
echo    - TROUBLESHOOTING.md
echo    - WEB_INTERFACE_README.md
echo    - CSV_ACTIONS_GUIDE.md
echo.

pause
