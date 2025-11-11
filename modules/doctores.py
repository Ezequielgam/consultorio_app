import tkinter as tk
from tkinter import ttk, messagebox
from database import queries


class DoctoresModule:
    def __init__(self, parent, connection):
        self.connection = connection
        self.queries = queries.DoctoresQueries(connection)
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_doctores()

    def create_widgets(self):
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(self.frame, text="Búsqueda de Doctores")
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="DNI:").grid(row=0, column=0, padx=5, pady=5)
        self.dni_search = ttk.Entry(search_frame)
        self.dni_search.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(search_frame, text="Apellido:").grid(row=0, column=2, padx=5, pady=5)
        self.apellido_search = ttk.Entry(search_frame)
        self.apellido_search.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(
            search_frame, text="Buscar por DNI", command=self.buscar_por_dni
        ).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(
            search_frame, text="Buscar por Apellido", command=self.buscar_por_apellido
        ).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(search_frame, text="Mostrar Todos", command=self.load_doctores).grid(
            row=0, column=6, padx=5, pady=5
        )

        # Treeview para mostrar doctores
        columns = (
            "ID",
            "DNI",
            "Matrícula",
            "Apellido",
            "Nombre",
            "Teléfono",
            "Email",
            "Especialidad",
        )
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")

        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame de botones
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(button_frame, text="Nuevo Doctor", command=self.nuevo_doctor).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Editar Doctor", command=self.editar_doctor).pack(
            side="left", padx=5
        )
        ttk.Button(
            button_frame, text="Eliminar Doctor", command=self.eliminar_doctor
        ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.load_doctores).pack(
            side="left", padx=5
        )

    def load_doctores(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        doctores = self.queries.obtener_doctores()
        for doctor in doctores:
            self.tree.insert("", "end", values=doctor)

    def buscar_por_dni(self):
        dni = self.dni_search.get()
        if dni:
            for item in self.tree.get_children():
                self.tree.delete(item)

            doctores = self.queries.buscar_doctor_por_dni(dni)
            for doctor in doctores:
                self.tree.insert("", "end", values=doctor)

    def buscar_por_apellido(self):
        apellido = self.apellido_search.get()
        if apellido:
            for item in self.tree.get_children():
                self.tree.delete(item)

            doctores = self.queries.buscar_doctor_por_apellido(apellido)
            for doctor in doctores:
                self.tree.insert("", "end", values=doctor)

    def nuevo_doctor(self):
        self.abrir_formulario_doctor()

    def editar_doctor(self):
        selected = self.tree.selection()
        if selected:
            doctor_id = self.tree.item(selected[0])["values"][0]
            self.abrir_formulario_doctor(doctor_id)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un doctor para editar")

    def eliminar_doctor(self):
        selected = self.tree.selection()
        if selected:
            doctor_id = self.tree.item(selected[0])["values"][0]
            if messagebox.askyesno(
                "Confirmar", "¿Está seguro de eliminar este doctor?"
            ):
                success, message = self.queries.eliminar_doctor(doctor_id)
                if success:
                    messagebox.showinfo("Éxito", message)
                    self.load_doctores()
                else:
                    messagebox.showerror("Error", message)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un doctor para eliminar")

    def abrir_formulario_doctor(self, doctor_id=None):
        formulario = tk.Toplevel(self.frame)
        formulario.title("Nuevo Doctor" if doctor_id is None else "Editar Doctor")
        formulario.geometry("400x300")
        formulario.transient(self.frame)
        formulario.grab_set()

        # Campos del formulario
        ttk.Label(formulario, text="DNI:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        dni_entry = ttk.Entry(formulario)
        dni_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Matrícula:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        matricula_entry = ttk.Entry(formulario)
        matricula_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Apellido:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        apellido_entry = ttk.Entry(formulario)
        apellido_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Nombre:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        nombre_entry = ttk.Entry(formulario)
        nombre_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Teléfono:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        telefono_entry = ttk.Entry(formulario)
        telefono_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Email:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )
        email_entry = ttk.Entry(formulario)
        email_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Especialidad:").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        especialidad_entry = ttk.Entry(formulario)
        especialidad_entry.grid(row=6, column=1, padx=5, pady=5)
        especialidad_entry.insert(0, "Cardiología")

        if doctor_id is not None:
            # Cargar datos existentes
            doctor = self.queries.obtener_doctor_por_id(doctor_id)
            if doctor:
                dni_entry.insert(0, doctor[1])
                matricula_entry.insert(0, doctor[2])
                apellido_entry.insert(0, doctor[3])
                nombre_entry.insert(0, doctor[4])
                telefono_entry.insert(0, doctor[5] or "")
                email_entry.insert(0, doctor[6] or "")
                especialidad_entry.delete(0, tk.END)
                especialidad_entry.insert(0, doctor[7] or "Cardiología")

        def guardar():
            dni = dni_entry.get()
            matricula = matricula_entry.get()
            apellido = apellido_entry.get()
            nombre = nombre_entry.get()
            telefono = telefono_entry.get()
            email = email_entry.get()
            especialidad = especialidad_entry.get()

            if not dni or not matricula or not apellido or not nombre:
                messagebox.showerror(
                    "Error", ("DNI, Matrícula, Apellido y Nombre son " "obligatorios")
                )
                return

            datos = (dni, matricula, apellido, nombre, telefono, email, especialidad)

            try:
                if doctor_id is None:
                    nuevo_id = self.queries.insertar_doctor(datos)
                    messagebox.showinfo("Éxito", f"Doctor agregado con ID: {nuevo_id}")
                else:
                    if self.queries.actualizar_doctor(doctor_id, datos):
                        messagebox.showinfo("Éxito", "Doctor actualizado correctamente")
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar el doctor")
                formulario.destroy()
                self.load_doctores()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ttk.Button(formulario, text="Guardar", command=guardar).grid(
            row=7, column=0, columnspan=2, pady=10
        )
