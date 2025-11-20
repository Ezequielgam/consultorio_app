@echo off
TITLE Instalador del Sistema de Consultorio Médico
echo ================================================
echo   Instalador de dependencias - Python
echo ================================================
echo.

REM Volver a carpeta raíz del proyecto
cd ..

REM Verificar Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python no está instalado. Instálalo antes de continuar.
    pause
    exit /b
)

echo ✔ Python detectado.

REM Crear entorno virtual
echo.
echo Creando entorno virtual...
python -m venv venv

REM Activar entorno
call venv\Scripts\activate.bat

echo Instalando librerías desde requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ================================================
echo   Instalación completada correctamente
echo   Para iniciar el sistema, ejecuta:
echo   scripts\run.bat
echo ================================================
pause
