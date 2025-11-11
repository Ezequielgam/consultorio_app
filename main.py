# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.connection import DatabaseConnection
from modules.doctores import DoctoresModule
from modules.pacientes import PacientesModule
from modules.turnos import TurnosModule
from modules.usuarios import UsuariosModule
from modules.facturacion import FacturacionModule
from modules.ficha_medica import FichaMedicaModule


class ConsultorioApp:
    def __init__(self, root, user_id, username, rol, nombre_completo):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.rol = rol
        self.nombre_completo = nombre_completo

        self.root.title(
            f"Sistema de Consultorio Médico - Cardiología - Usuario: {nombre_completo} ({rol})"
        )
        self.root.geometry("1200x700")

        # Configurar el protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Conectar a la base de datos
        self.db = DatabaseConnection()
        self.conn = self.db.connect()

        if not self.conn:
            messagebox.showerror(
                "Error de Conexión",
                "No se pudo conectar a la base de datos.\n\n"
                "Por favor verifica:\n"
                "• Que MySQL esté ejecutándose\n"
                "• Que la base de datos 'consultorioMedico' exista\n"
                "• El usuario y contraseña en database/connection.py",
            )
            self.root.destroy()
            return

        self.create_main_frame()
        print(f"✅ Aplicación principal iniciada para: {nombre_completo} ({rol})")

    def create_main_frame(self):
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            # Módulos básicos para todos los roles
            self.pacientes_module = PacientesModule(self.notebook, self.conn)
            self.turnos_module = TurnosModule(self.notebook, self.conn)

            # Agregar pestañas básicas
            self.notebook.add(self.pacientes_module.frame, text="👥 Pacientes")
            self.notebook.add(self.turnos_module.frame, text="📅 Turnos")

            # Módulos según el rol
            if self.rol == "Administrador":
                self.doctores_module = DoctoresModule(self.notebook, self.conn)
                self.usuarios_module = UsuariosModule(self.notebook, self.conn)
                self.facturacion_module = FacturacionModule(self.notebook, self.conn)
                self.ficha_medica_module = FichaMedicaModule(self.notebook, self.conn)

                self.notebook.add(self.doctores_module.frame, text="👨‍⚕️ Doctores")
                self.notebook.add(self.usuarios_module.frame, text="👤 Usuarios")
                self.notebook.add(self.facturacion_module.frame, text="💰 Facturación")
                self.notebook.add(
                    self.ficha_medica_module.frame, text="📋 Ficha Médica"
                )

            elif self.rol == "Cardiólogo":
                self.ficha_medica_module = FichaMedicaModule(self.notebook, self.conn)
                self.notebook.add(
                    self.ficha_medica_module.frame, text="📋 Ficha Médica"
                )

            elif self.rol == "Secretaria":
                self.facturacion_module = FacturacionModule(self.notebook, self.conn)
                self.notebook.add(self.facturacion_module.frame, text="💰 Facturación")

            print("✅ Módulos cargados correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los módulos: {str(e)}")
            self.root.destroy()

    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        if hasattr(self, "db"):
            self.db.disconnect()
        self.root.destroy()
        print("👋 Aplicación cerrada")


def iniciar_aplicacion_principal(user_id, username, rol, nombre_completo):
    """Función para iniciar la aplicación principal después del login"""
    root = tk.Tk()
    app = ConsultorioApp(root, user_id, username, rol, nombre_completo)
    root.mainloop()


if __name__ == "__main__":
    # Si se ejecuta directamente, iniciar con login
    from modules.login import LoginWindow

    def on_login_success(user_id, username, rol, nombre_completo):
        print(f"🎉 Login exitoso, iniciando aplicación principal...")
        login_root.destroy()  # Cerrar ventana de login
        iniciar_aplicacion_principal(user_id, username, rol, nombre_completo)

    # Crear ventana de login
    login_root = tk.Tk()
    login_app = LoginWindow(login_root, on_login_success)

    # Configurar la conexión para el login
    db = DatabaseConnection()
    conn = db.connect()
    if conn:
        login_app.set_connection(conn)
        print("🔌 Conexión establecida para login")
        login_root.mainloop()
    else:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos")
        login_root.quit()
