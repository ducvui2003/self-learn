@echo off
setlocal

REM One-click pytest runner for Phase 6 (Spring `mvn test` equivalent)
cd /d "%~dp0"
set "VENV_PY=%~dp0..\.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo [ERROR] Shared .venv not found. Run .\run.bat once first.
    pause
    exit /b 1
)

echo [INFO] Installing Phase 6 package and running pytest...
"%VENV_PY%" -m pip install --no-build-isolation --no-deps -e . >nul
"%VENV_PY%" -m pytest -v

endlocal
