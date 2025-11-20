import customtkinter as ctk
from tkinter import messagebox
from database.queries import LoginQueries


class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.queries = None

        # Configuración global de CustomTkinter
        ctk.set_appearance_mode("light")  # "dark", "system"
        ctk.set_default_color_theme("blue")

        self.root.title("Sistema de Consultorio Médico - Login")
        self.root.geometry("420x420")
        self.root.resizable(False, False)
        self.center_window()

        # Cierre correcto
        self.root.protocol("WM_DELETE_WINDOW", self.salir)

        self.create_widgets()

    # -----------------------------------------------------
    def center_window(self):
        """Centrar la ventana en pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # -----------------------------------------------------
    def set_connection(self, connection):
        """Configura la conexión a la BD."""
        self.queries = LoginQueries(connection)
        print("✅ Conexión configurada en login")

    # -----------------------------------------------------
    def create_widgets(self):
        """Interfaz visual con CustomTkinter."""

        # Contenedor estilo "card"
        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        ctk.CTkLabel(
            main_frame,
            text="Consultorio Médico",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(25, 5))

        # Subtítulo
        ctk.CTkLabel(
            main_frame,
            text="Sistema de Gestión - Cardiología",
            font=ctk.CTkFont(size=16),
        ).pack(pady=(0, 20))

        # -------------------------------
        # Campo Usuario
        ctk.CTkLabel(main_frame, text="Usuario:").pack(pady=(10, 0))

        self.usuario_entry = ctk.CTkEntry(
            main_frame, width=260, placeholder_text="Ingrese su usuario"
        )
        self.usuario_entry.pack(pady=5)

        # -------------------------------
        # Campo Contraseña
        ctk.CTkLabel(main_frame, text="Contraseña:").pack(pady=(10, 0))

        self.password_entry = ctk.CTkEntry(
            main_frame, width=260, placeholder_text="Ingrese su contraseña", show="*"
        )
        self.password_entry.pack(pady=5)

        # -------------------------------
        # Botón ingresar
        ctk.CTkButton(
            main_frame,
            text="Ingresar",
            width=200,
            command=self.verificar_login,
        ).pack(pady=(25, 10))

        # Botón salir
        ctk.CTkButton(
            main_frame,
            text="Salir",
            width=200,
            fg_color="#b12323",
            hover_color="#8a1b1b",
            command=self.salir,
        ).pack()

        # ENTER para iniciar sesión
        self.root.bind("<Return>", lambda event: self.verificar_login())

        self.usuario_entry.focus()

        print("🎨 Login creado con CustomTkinter")

    # -----------------------------------------------------
    def verificar_login(self):
        """Valida usuario + contraseña con la base de datos."""
        if self.queries is None:
            messagebox.showerror("Error", "No hay conexión a la BD")
            return

        usuario = self.usuario_entry.get()
        password = self.password_entry.get()

        if not usuario or not password:
            messagebox.showerror("Error", "Debe completar los campos.")
            return

        try:
            print(f"🔐 Verificando credenciales ({usuario})...")
            resultado = self.queries.verificar_usuario(usuario, password)

            if resultado:
                user_id, username, rol, nombre_completo = resultado
                print(f"✔ Login correcto: {nombre_completo} ({rol})")

                self.on_login_success(user_id, username, rol, nombre_completo)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        except Exception as e:
            messagebox.showerror("Error", f"Error en verificación:\n{str(e)}")
            print("❌ Error:", e)

    # -----------------------------------------------------
    def salir(self):
        print("👋 Cerrando aplicación...")
        self.root.destroy()
