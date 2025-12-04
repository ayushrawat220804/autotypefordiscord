@echo off
echo ========================================
echo Building God OwO Discord Bot Executable
echo Made with ^<3 by Aditi and Ayush
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Installing/Upgrading dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Step 2: Building executable with PyInstaller...
python -m PyInstaller --onefile --windowed --name "God_Owo_DiscordBot" --icon=NONE --add-data "God_owo_discordbot.py;." God_owo_discordbot.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo Executable location: dist\God_Owo_DiscordBot.exe
echo ========================================
pause

