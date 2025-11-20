@echo off
TITLE Consultorio Médico - Eliminar Entorno Virtual
echo ================================================
echo     Eliminador del entorno virtual (venv)
echo ================================================
echo.

REM Volver a carpeta raíz del proyecto
cd ..

IF EXIST "venv" (
    echo ✔ Eliminando entorno virtual...
    rmdir /s /q venv
    echo ✔ Entorno virtual eliminado correctamente.
) ELSE (
    echo ℹ No existe la carpeta venv. Nada para eliminar.
)

echo.
echo Podés reinstalar dependencias con:
echo   scripts\install.bat
echo.
echo ================================================
pause
