@echo off
cd /d "%~dp0"

echo ========================================
echo   Manga Translator - Setup
echo ========================================

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.10+ required.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version') do echo  Python: %%a

REM Create venv
if not exist venv (
    echo  Creating virtual environment...
    python -m venv venv
)

REM Activate and upgrade pip
call venv\Scripts\activate
python -m pip install --upgrade pip -q

REM Install dependencies
echo  Installing dependencies (this may take a while)...
pip install -r requirements.txt -q

REM Patch manga-ocr
echo  Patching manga-ocr for compatibility...
python patch_manga_ocr.py

REM Create dirs
if not exist input mkdir input
if not exist output mkdir output
if not exist models mkdir models
if not exist fonts mkdir fonts
if not exist cache mkdir cache

echo.
echo  Setup complete! Run run.bat to start.
echo ========================================
pause
