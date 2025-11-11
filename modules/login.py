import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import LoginQueries


def verificar_usuario(self, usuario, password):
    query = """
    SELECT u.nombre_usuario, r.nombre_rol, d.id_doctor
    FROM Usuario u
    JOIN Rol r ON u.id_rol = r.id_rol
    LEFT JOIN Doctor d ON u.id_doctor = d.id_doctor
    WHERE u.nombre_usuario = %s AND u.contrasena = SHA2(%s, 256)
    """


class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.queries = None

        self.root.title("Sistema de Consultorio Médico - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.center_window()

        # Configurar el protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.salir)

        self.create_widgets()

    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def set_connection(self, connection):
        self.queries = LoginQueries(connection)
        print("✅ Conexión configurada en Login")

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame, text="Consultorio Médico", font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)

        subtitle_label = ttk.Label(
            main_frame, text="Sistema de Gestión - Cardiología", font=("Arial", 12)
        )
        subtitle_label.pack(pady=5)

        # Frame de credenciales
        cred_frame = ttk.LabelFrame(main_frame, text="Ingreso al Sistema", padding="15")
        cred_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        ttk.Label(cred_frame, text="Usuario:").grid(
            row=0, column=0, padx=5, pady=10, sticky="e"
        )
        self.usuario_entry = ttk.Entry(cred_frame, width=20)
        self.usuario_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ttk.Label(cred_frame, text="Contraseña:").grid(
            row=1, column=0, padx=5, pady=10, sticky="e"
        )
        self.password_entry = ttk.Entry(cred_frame, show="*", width=20)
        self.password_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Configurar el grid para que la columna 1 se expanda
        cred_frame.columnconfigure(1, weight=1)

        # Frame de botones
        button_frame = ttk.Frame(cred_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Ingresar", command=self.verificar_login).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Button(button_frame, text="Salir", command=self.salir).pack(
            side=tk.LEFT, padx=10
        )

        # Bind Enter para facilitar el login
        self.root.bind("<Return>", lambda event: self.verificar_login())

        # Focus en el campo de usuario
        self.usuario_entry.focus()

        print("✅ Interfaz de login creada")

    def verificar_login(self):
        if self.queries is None:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return

        usuario = self.usuario_entry.get()
        password = self.password_entry.get()

        if not usuario or not password:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return

        try:
            print(f"🔐 Verificando credenciales para: {usuario}")
            resultado = self.queries.verificar_usuario(usuario, password)
            if resultado:
                user_id, username, rol, nombre_completo = resultado
                print(
                    f"✅ Credenciales válidas. Rol: {rol}, Usuario: {nombre_completo}"
                )

                # Llamar al callback de éxito
                self.on_login_success(user_id, username, rol, nombre_completo)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
                print("❌ Credenciales inválidas")
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar credenciales: {str(e)}")
            print(f"❌ Error en verificación: {e}")

    def salir(self):
        """Salir de la aplicación"""
        print("👋 Saliendo del sistema...")
        self.root.quit()
        self.root.destroy()
