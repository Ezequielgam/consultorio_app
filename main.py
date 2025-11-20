import tkinter as tk
from tkinter import ttk, messagebox

from database.connection import DatabaseConnection

# Importar módulos
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

        # Manejar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Conectar a la base de datos
        self.db = DatabaseConnection()
        self.conn = self.db.connect()

        if not self.conn:
            messagebox.showerror(
                "Error de Conexión",
                "No se pudo conectar a la base de datos.\n\n"
                "• Verifica que MySQL esté en ejecución\n"
                "• Que la base 'consultorioMedico' exista\n"
                "• Revisá usuario y contraseña en database/connection.py",
            )
            root.destroy()
            return

        # Construir interfaz
        self.create_main_frame()

        print(f"✅ Aplicación iniciada para {nombre_completo} ({rol})")

    def create_main_frame(self):

        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            # Módulos base
            self.pacientes_module = PacientesModule(self.notebook, self.conn)
            self.turnos_module = TurnosModule(self.notebook, self.conn)

            self.notebook.add(self.pacientes_module.frame, text="👥 Pacientes")
            self.notebook.add(self.turnos_module.frame, text="📅 Turnos")

            # Módulos por rol
            if self.rol == "Administrador":
                self.doctores_module = DoctoresModule(self.notebook, self.conn)
                self.usuarios_module = UsuariosModule(self.notebook, self.conn)
                self.facturacion_module = FacturacionModule(self.notebook, self.conn)
                self.ficha_medica_module = FichaMedicaModule(self.notebook, self.conn)

                self.notebook.add(self.doctores_module.frame, text="👨‍⚕️ Doctores")
                self.notebook.add(self.usuarios_module.frame, text="👤 Usuarios")
                self.notebook.add(self.facturacion_module.frame, text="💰 Facturación")
                self.notebook.add(self.ficha_medica_module.frame, text="📋 Ficha Médica")

            elif self.rol == "Cardiólogo":
                self.ficha_medica_module = FichaMedicaModule(self.notebook, self.conn)
                self.notebook.add(self.ficha_medica_module.frame, text="📋 Ficha Médica")

            elif self.rol == "Secretaria":
                self.facturacion_module = FacturacionModule(self.notebook, self.conn)
                self.notebook.add(self.facturacion_module.frame, text="💰 Facturación")

            print("✅ Módulos cargados correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar módulos:\n{str(e)}")
            self.root.destroy()

    def on_closing(self):
        """Cerrar aplicación correctamente"""
        if self.db:
            self.db.disconnect()
        print("👋 Aplicación cerrada")
        self.root.destroy()


def iniciar_aplicacion_principal(user_id, username, rol, nombre_completo):
    """Función llamada luego de login exitoso"""
    root = tk.Tk()
    app = ConsultorioApp(root, user_id, username, rol, nombre_completo)
    root.mainloop()


if __name__ == "__main__":

    from modules.login import LoginWindow

    def on_login_success(user_id, username, rol, nombre_completo):
        print("🎉 Login exitoso, iniciando sistema...")
        login_root.destroy()
        iniciar_aplicacion_principal(user_id, username, rol, nombre_completo)

    # Crear ventana login
    login_root = tk.Tk()
    login_app = LoginWindow(login_root, on_login_success)

    # Conectar BD solo para login
    db = DatabaseConnection()
    conn = db.connect()

    if conn:
        login_app.set_connection(conn)
        print("🔌 Conexión establecida para login")
        login_root.mainloop()
    else:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos")
        login_root.destroy()
