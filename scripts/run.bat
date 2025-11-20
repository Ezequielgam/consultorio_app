@echo off
TITLE Consultorio Médico - Ejecutar Sistema
echo ================================================
echo   Iniciando Sistema de Gestión - Consultorio Médico
echo ================================================
echo.

REM Volver a carpeta raíz del proyecto
cd ..

REM Verificar entorno virtual
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo ❌ No se encontró el entorno virtual.
    echo Ejecutá primero: scripts\install.bat
    pause
    exit /b
)

echo ✔ Activando entorno virtual...
call venv\Scripts\activate.bat

echo ✔ Ejecutando sistema...
python main.py

echo.
echo ================================================
echo   El sistema se cerró correctamente.
echo ================================================
pause
