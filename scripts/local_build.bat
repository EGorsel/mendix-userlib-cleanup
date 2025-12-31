@echo off
setlocal

echo --- Mendix Userlib Cleanup: Local Build Script ---
echo This script requires 'pyinstaller' to be installed (pip install pyinstaller).

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller not found. Please run: pip install pyinstaller
    pause
    exit /b 1
)

echo [1/3] Cleaning up previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist mx--cleanuserlib.spec del mx--cleanuserlib.spec

cd /d "%~dp0.."

echo [2/3] Building standalone executable (Optimized)...
pyinstaller --noconfirm --onefile --console --name mx--cleanuserlib ^
    --exclude-module unittest ^
    --exclude-module email ^
    --exclude-module pydoc ^
    --exclude-module http ^
    --exclude-module html ^
    --exclude-module xml ^
    --add-data "src/core;src/core" ^
    --add-data "src/engines;src/engines" ^
    --add-data "config;config" ^
    --add-data "docs;docs" ^
    src/core/manager.py

if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b %errorlevel%
)

echo [3/3] Build successful!
echo The standalone executable can be found in: dist\mx--cleanuserlib\
pause
endlocal
