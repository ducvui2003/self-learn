@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM Phase 6 - Setup shared .venv (Python 3.12 + Zope 5 + pytest) and run
REM ============================================================

cd /d "%~dp0"
set "ROOT_DIR=%~dp0.."
set "VENV_DIR=%ROOT_DIR%\.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "RUNWSGI=%VENV_DIR%\Scripts\runwsgi.exe"

REM 1. Create shared .venv if it does not exist
if not exist "%VENV_PY%" (
    echo [INFO] Shared .venv not found. Looking for Python 3.12 or 3.13...

    py -3.12 --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo [INFO] Creating .venv with Python 3.12...
        py -3.12 -m venv "%VENV_DIR%"
    ) else (
        py -3.13 --version >nul 2>&1
        if !errorlevel! equ 0 (
            echo [INFO] Creating .venv with Python 3.13...
            py -3.13 -m venv "%VENV_DIR%"
        ) else (
            echo [ERROR] Python 3.12 or 3.13 was not found.
            pause
            exit /b 1
        )
    )

    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment at %VENV_DIR%.
        pause
        exit /b 1
    )

    echo [INFO] Upgrading pip and wheel...
    "%VENV_PY%" -m pip install -U pip wheel
)

REM 2. Install Zope 5 + pytest + Phase 6 package from pyproject.toml
echo [INFO] Installing dependencies and Phase 6 package (employee_api) from pyproject.toml...
"%VENV_PY%" -m pip install -e .
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies from pyproject.toml.
    pause
    exit /b 1
)

REM 3. Ensure var/ exists for ZODB Data.fs
if not exist "var" mkdir var

REM 4. Start Zope 5 WSGI server
echo.
echo [INFO] Starting Zope 5 (Phase 6 - Production & Testing) on http://127.0.0.1:8080 ...
echo [INFO] Run automated tests anytime with: .\test.bat
echo.
"%RUNWSGI%" -v etc\zope.ini

endlocal
