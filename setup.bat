@echo off
echo 🍽️ Pandeyji Eatery - Quick Setup
echo ================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt
echo.

echo Starting interactive setup...
python interactive_setup.py
echo.

echo Setup complete! 
echo.
echo To start the application:
echo   python run.py
echo.
echo To test the application:
echo   python test_application.py
echo.
pause
