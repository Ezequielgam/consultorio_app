# modules/usuarios.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import UsuariosQueries


class UsuariosModule:
    def __init__(self, parent, connection):
        self.connection = connection
        self.queries = UsuariosQueries(connection)

        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_usuarios()

    def create_widgets(self):
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(self.frame, text="Búsqueda de Usuarios")
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="Usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.usuario_search = ttk.Entry(search_frame)
        self.usuario_search.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(search_frame, text="Buscar", command=self.buscar_usuario).grid(
            row=0, column=2, padx=5, pady=5
        )
        ttk.Button(search_frame, text="Mostrar Todos", command=self.load_usuarios).grid(
            row=0, column=3, padx=5, pady=5
        )

        # Treeview para mostrar usuarios
        columns = ("ID", "Usuario", "Rol", "Doctor Asignado")
        self.tree = ttk.Treeview(
            self.frame, columns=columns, show="headings", height=15
        )

        # Configurar columnas
        column_widths = {"ID": 50, "Usuario": 150, "Rol": 120, "Doctor Asignado": 200}

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))

        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(
            self.frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", padx=5, pady=5)

        # Frame de botones
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(button_frame, text="Nuevo Usuario", command=self.nuevo_usuario).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Editar", command=self.editar_usuario).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_usuario).pack(
            side="left", padx=5
        )
        ttk.Button(
            button_frame, text="Cambiar Contraseña", command=self.cambiar_contrasena
        ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.load_usuarios).pack(
            side="left", padx=5
        )

    def load_usuarios(self):
        """Cargar usuarios en el treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            usuarios = self.queries.obtener_usuarios()
            for usuario in usuarios:
                self.tree.insert("", "end", values=usuario)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {str(e)}")

    def buscar_usuario(self):
        usuario = self.usuario_search.get()
        if usuario:
            for item in self.tree.get_children():
                self.tree.delete(item)

            try:
                usuarios = self.queries.obtener_usuarios()
                for user in usuarios:
                    if usuario.lower() in user[1].lower():
                        self.tree.insert("", "end", values=user)
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar usuario: {str(e)}")

    def nuevo_usuario(self):
        self.abrir_formulario_usuario()

    def editar_usuario(self):
        selected = self.tree.selection()
        if selected:
            usuario_id = self.tree.item(selected[0])["values"][0]
            self.abrir_formulario_usuario(usuario_id)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para editar")

    def eliminar_usuario(self):
        selected = self.tree.selection()
        if selected:
            usuario_id = self.tree.item(selected[0])["values"][0]
            nombre_usuario = self.tree.item(selected[0])["values"][1]

            if messagebox.askyesno(
                "Confirmar", f"¿Está seguro de eliminar al usuario '{nombre_usuario}'?"
            ):
                try:
                    success, message = self.queries.eliminar_usuario(usuario_id)
                    if success:
                        messagebox.showinfo("Éxito", message)
                        self.load_usuarios()
                    else:
                        messagebox.showerror("Error", message)
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Error al eliminar usuario: {str(e)}"
                    )
        else:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")

    def cambiar_contrasena(self):
        selected = self.tree.selection()
        if selected:
            usuario_id = self.tree.item(selected[0])["values"][0]
            nombre_usuario = self.tree.item(selected[0])["values"][1]
            self.abrir_formulario_contrasena(usuario_id, nombre_usuario)
        else:
            messagebox.showwarning(
                "Advertencia", "Seleccione un usuario para cambiar contraseña"
            )

    def abrir_formulario_usuario(self, usuario_id=None):
        formulario = tk.Toplevel(self.frame)
        formulario.title("Nuevo Usuario" if usuario_id is None else "Editar Usuario")
        formulario.geometry("400x300")
        formulario.transient(self.frame)
        formulario.grab_set()

        # Obtener datos para combobox
        try:
            roles = self.queries.obtener_roles()
            doctores = self.queries.obtener_doctores_para_combo()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            formulario.destroy()
            return

        # Campos del formulario
        ttk.Label(formulario, text="Nombre de Usuario:*").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        usuario_entry = ttk.Entry(formulario)
        usuario_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Contraseña:" + ("" if usuario_id else "*")).grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        password_entry = ttk.Entry(formulario, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(
            formulario, text="Confirmar Contraseña:" + ("" if usuario_id else "*")
        ).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        confirm_password_entry = ttk.Entry(formulario, show="*")
        confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Rol:*").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        rol_combo = ttk.Combobox(
            formulario, values=[f"{r[0]} - {r[1]}" for r in roles], state="readonly"
        )
        rol_combo.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Doctor Asignado:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        doctor_combo = ttk.Combobox(
            formulario,
            values=["0 - No asignado"] + [f"{d[0]} - {d[1]}" for d in doctores],
            state="readonly",
        )
        doctor_combo.grid(row=4, column=1, padx=5, pady=5)
        doctor_combo.set("0 - No asignado")

        # Cargar datos existentes si estamos editando
        if usuario_id is not None:
            try:
                usuario = self.queries.obtener_usuario_por_id(usuario_id)
                if usuario:
                    usuario_entry.insert(0, usuario[1] or "")

                    for r in roles:
                        if r[0] == usuario[2]:
                            rol_combo.set(f"{r[0]} - {r[1]}")
                            break

                    if usuario[3]:  # id_doctor
                        for d in doctores:
                            if d[0] == usuario[3]:
                                doctor_combo.set(f"{d[0]} - {d[1]}")
                                break
                    else:
                        doctor_combo.set("0 - No asignado")
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error al cargar datos del usuario: {str(e)}"
                )

        def guardar():
            # Validaciones
            if not usuario_entry.get():
                messagebox.showerror("Error", "El nombre de usuario es obligatorio")
                return

            if not rol_combo.get():
                messagebox.showerror("Error", "Debe seleccionar un rol")
                return

            # Validar contraseña para nuevo usuario
            if usuario_id is None:
                if not password_entry.get():
                    messagebox.showerror(
                        "Error", "La contraseña es obligatoria para nuevo usuario"
                    )
                    return
                if password_entry.get() != confirm_password_entry.get():
                    messagebox.showerror("Error", "Las contraseñas no coinciden")
                    return

            # Verificar nombre de usuario único
            if self.queries.verificar_nombre_usuario(usuario_entry.get(), usuario_id):
                messagebox.showerror("Error", "El nombre de usuario ya existe")
                return

            # Obtener IDs
            try:
                rol_id = int(rol_combo.get().split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Error al obtener ID del rol")
                return

            doctor_str = doctor_combo.get()
            id_doctor = None
            if doctor_str and doctor_str != "0 - No asignado":
                try:
                    id_doctor = int(doctor_str.split(" - ")[0])
                except (ValueError, IndexError):
                    pass

            try:
                if usuario_id is None:
                    # Nuevo usuario
                    datos = (
                        usuario_entry.get(),
                        password_entry.get(),
                        rol_id,
                        id_doctor,
                    )
                    nuevo_id = self.queries.insertar_usuario(datos)
                    messagebox.showinfo("Éxito", f"Usuario creado con ID: {nuevo_id}")
                else:
                    # Editar usuario existente
                    datos = (usuario_entry.get(), rol_id, id_doctor)
                    if self.queries.actualizar_usuario(usuario_id, datos):
                        messagebox.showinfo(
                            "Éxito", "Usuario actualizado correctamente"
                        )

                    # Si se proporcionó nueva contraseña, actualizarla
                    if password_entry.get():
                        if password_entry.get() != confirm_password_entry.get():
                            messagebox.showerror(
                                "Error", "Las contraseñas no coinciden"
                            )
                            return
                        self.queries.actualizar_contrasena(
                            usuario_id, password_entry.get()
                        )
                        messagebox.showinfo(
                            "Éxito", "Usuario y contraseña actualizados correctamente"
                        )

                formulario.destroy()
                self.load_usuarios()

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar usuario: {str(e)}")

        # Botones del formulario
        button_frame = ttk.Frame(formulario)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Guardar", command=guardar).pack(
            side="left", padx=10
        )
        ttk.Button(button_frame, text="Cancelar", command=formulario.destroy).pack(
            side="left", padx=10
        )

    def abrir_formulario_contrasena(self, usuario_id, nombre_usuario):
        formulario = tk.Toplevel(self.frame)
        formulario.title(f"Cambiar Contraseña - {nombre_usuario}")
        formulario.geometry("300x200")
        formulario.transient(self.frame)
        formulario.grab_set()

        ttk.Label(
            formulario, text=f"Usuario: {nombre_usuario}", font=("Arial", 10, "bold")
        ).pack(pady=10)

        ttk.Label(formulario, text="Nueva Contraseña:*").pack(pady=5)
        nueva_password_entry = ttk.Entry(formulario, show="*")
        nueva_password_entry.pack(pady=5)

        ttk.Label(formulario, text="Confirmar Contraseña:*").pack(pady=5)
        confirm_password_entry = ttk.Entry(formulario, show="*")
        confirm_password_entry.pack(pady=5)

        def guardar_contrasena():
            nueva_password = nueva_password_entry.get()
            confirm_password = confirm_password_entry.get()

            if not nueva_password:
                messagebox.showerror("Error", "La nueva contraseña es obligatoria")
                return

            if nueva_password != confirm_password:
                messagebox.showerror("Error", "Las contraseñas no coinciden")
                return

            try:
                if self.queries.actualizar_contrasena(usuario_id, nueva_password):
                    messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
                    formulario.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la contraseña")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cambiar contraseña: {str(e)}")

        ttk.Button(
            formulario, text="Cambiar Contraseña", command=guardar_contrasena
        ).pack(pady=20)
