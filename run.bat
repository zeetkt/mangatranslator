@echo off
cd /d "%~dp0"

if not exist venv (
    echo First launch -- running setup...
    call setup.bat
    if errorlevel 1 (
        pause
        exit /b 1
    )
)

set HF_HOME=%CD%\cache\huggingface
set TORCH_HOME=%CD%\cache\torch
set EASYOCR_MODULE_PATH=%CD%\cache\easyocr
set TRANSFORMERS_CACHE=%CD%\cache\huggingface\transformers
set HUGGINGFACE_HUB_CACHE=%CD%\cache\huggingface\hub

call venv\Scripts\activate
python app.py %*
pause
