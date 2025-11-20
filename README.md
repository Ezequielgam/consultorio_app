# Sistema de Gestión para Consultorio Médico

**Versión:** v1.0  
**Autores:** Gamarro Claudio Ezequiel
**Instituto:** IES Alfredo Coviello – Tecnicatura Superior en Desarrollo de Software  
**Fecha:** noviembre 2025

---

## Resumen

Aplicación de escritorio en Python/Tkinter para la gestión completa de un consultorio médico: pacientes, turnos, fichas médicas (consultas/recetas/estudios), doctores, usuarios y facturación.

---

## Estructura del repositorio (recomendada)

/tu_proyecto/
├── main.py
├── requirements.txt
├── config.ini
├── README.md
├── modules/
├── database/
├── assets/
│ └── icon.ico
└── scripts/
├── install.bat
├── run.bat
└── uninstall.bat

yaml
Copiar código

---

## Requisitos previos (Windows)

- Python 3.10+ (recomendado)
- Git (opcional)
- MySQL (servidor) con la base de datos y tablas creadas
- (Para instalador) PyInstaller y Inno Setup (para crear `setup.exe`)

---

## Instalación rápida (usuario final)

1. Clonar el repo o copiar los archivos al equipo.
2. Abrir `scripts/install.bat` con doble clic — esto:
   - crea un entorno virtual `venv`
   - instala dependencias de `requirements.txt`
3. Configurar `config.ini` con los datos de conexión a la base de datos (host, user, pass, db).
4. Ejecutar `scripts/run.bat` para iniciar la aplicación.

---

## Instalación manual (línea de comandos)

```powershell
# Crear venv (desde la raíz del proyecto)
python -m venv venv
# Activar (Windows PowerShell)
venv\Scripts\Activate.ps1
# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
# Configurar config.ini
# Ejecutar
python main.py

```

Uso de scripts/

scripts/install.bat — crea venv e instala dependencias.

scripts/run.bat — activa venv y ejecuta main.py.

scripts/uninstall.bat — borra la carpeta venv.
