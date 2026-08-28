@echo off
title ElectroLab 3D - Simulador de Campo Electrico
color 0A

echo ============================================================
echo   ElectroLab 3D: Fuerza y Campo Electrico Interactivo
echo ============================================================
echo.
echo  Iniciando configuracion automatica...
echo.

:: Detectar ejecutable de Python
set PYTHON_CMD=
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
) else (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] No se encontro Python instalado en el sistema.
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detectado mediante: %PYTHON_CMD%

:: Intentar crear e instalar en entorno virtual
if not exist ".venv" (
    echo [1/3] Creando entorno virtual aislado...
    %PYTHON_CMD% -m venv .venv
)

set RUNNER=
if exist ".venv\Scripts\python.exe" (
    set RUNNER=".venv\Scripts\python.exe"
) else (
    set RUNNER=%PYTHON_CMD%
)

echo [2/3] Instalando librerias requeridas...
%RUNNER% -m pip install -r requirements.txt --quiet

echo.
echo [3/3] Lanzando la aplicacion web...
echo.
echo Abre tu navegador en: http://localhost:8501
echo ============================================================
echo.

%RUNNER% -m streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo [REINTENTO] Probando ejecucion global directa...
    %PYTHON_CMD% -m streamlit run app.py
)

pause
