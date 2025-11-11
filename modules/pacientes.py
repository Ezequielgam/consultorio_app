# modules/pacientes.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import PacientesQueries


class PacientesModule:
    def __init__(self, parent, connection):
        self.connection = connection
        self.queries = PacientesQueries(connection)

        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_pacientes()

    def create_widgets(self):
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(self.frame, text="Búsqueda")
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="DNI:").grid(row=0, column=0, padx=5, pady=5)
        self.dni_search = ttk.Entry(search_frame)
        self.dni_search.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(search_frame, text="Buscar", command=self.buscar_paciente).grid(
            row=0, column=2, padx=5, pady=5
        )
        ttk.Button(
            search_frame, text="Mostrar Todos", command=self.load_pacientes
        ).grid(row=0, column=3, padx=5, pady=5)

        # Treeview para mostrar pacientes
        self.tree = ttk.Treeview(
            self.frame,
            columns=(
                "ID",
                "DNI",
                "Apellido",
                "Nombre",
                "Teléfono",
                "Email",
                "Obra Social",
            ),
            show="headings",
            height=15,
        )

        # Configurar columnas
        columns_config = {
            "ID": 50,
            "DNI": 100,
            "Apellido": 120,
            "Nombre": 120,
            "Teléfono": 100,
            "Email": 150,
            "Obra Social": 120,
        }

        for col, width in columns_config.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

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

        ttk.Button(
            button_frame, text="Nuevo Paciente", command=self.nuevo_paciente
        ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Editar", command=self.editar_paciente).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_paciente).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Actualizar", command=self.load_pacientes).pack(
            side="left", padx=5
        )

    def load_pacientes(self):
        """Cargar pacientes en el treeview con manejo seguro de índices"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            pacientes = self.queries.obtener_pacientes()
            for paciente in pacientes:
                # Manejar diferentes longitudes de tuplas de forma segura
                try:
                    # Verificar la longitud de la tupla y asignar valores por defecto
                    paciente_id = paciente[0] if len(paciente) > 0 else ""
                    dni = paciente[1] if len(paciente) > 1 else ""
                    apellido = paciente[2] if len(paciente) > 2 else ""
                    nombre = paciente[3] if len(paciente) > 3 else ""
                    telefono = paciente[4] if len(paciente) > 4 else ""
                    email = paciente[5] if len(paciente) > 5 else ""

                    # Para obra social, puede ser el índice 8 o 6 dependiendo de la consulta
                    obra_social = "Particular"
                    if len(paciente) > 8:
                        obra_social = paciente[8] or "Particular"
                    elif len(paciente) > 6:
                        # Si solo hay 7 columnas, la obra social podría estar en el índice 6
                        obra_social = paciente[6] or "Particular"

                    paciente_formateado = (
                        paciente_id,
                        dni,
                        apellido,
                        nombre,
                        telefono or "",
                        email or "",
                        obra_social,
                    )
                    self.tree.insert("", "end", values=paciente_formateado)

                except IndexError as ie:
                    print(f"Error de índice al procesar paciente: {ie}")
                    print(f"Tupla paciente: {paciente}")
                    continue

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pacientes: {str(e)}")
            print(f"Error completo: {e}")

    def buscar_paciente(self):
        dni = self.dni_search.get()
        if dni:
            for item in self.tree.get_children():
                self.tree.delete(item)

            try:
                pacientes = self.queries.buscar_paciente_por_dni(dni)
                for paciente in pacientes:
                    try:
                        paciente_id = paciente[0] if len(paciente) > 0 else ""
                        dni_val = paciente[1] if len(paciente) > 1 else ""
                        apellido = paciente[2] if len(paciente) > 2 else ""
                        nombre = paciente[3] if len(paciente) > 3 else ""
                        telefono = paciente[4] if len(paciente) > 4 else ""
                        email = paciente[5] if len(paciente) > 5 else ""

                        obra_social = "Particular"
                        if len(paciente) > 8:
                            obra_social = paciente[8] or "Particular"
                        elif len(paciente) > 6:
                            obra_social = paciente[6] or "Particular"

                        paciente_formateado = (
                            paciente_id,
                            dni_val,
                            apellido,
                            nombre,
                            telefono or "",
                            email or "",
                            obra_social,
                        )
                        self.tree.insert("", "end", values=paciente_formateado)
                    except IndexError as ie:
                        print(f"Error de índice al buscar paciente: {ie}")
                        continue
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar paciente: {str(e)}")

    def nuevo_paciente(self):
        self.abrir_formulario_paciente()

    def editar_paciente(self):
        selected = self.tree.selection()
        if selected:
            paciente_id = self.tree.item(selected[0])["values"][0]
            self.abrir_formulario_paciente(paciente_id)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un paciente para editar")

    def eliminar_paciente(self):
        selected = self.tree.selection()
        if selected:
            paciente_id = self.tree.item(selected[0])["values"][0]
            if messagebox.askyesno(
                "Confirmar", "¿Está seguro de eliminar este paciente?"
            ):
                try:
                    resultado = self.queries.eliminar_paciente(paciente_id)
                    if resultado:
                        messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
                        self.load_pacientes()
                    else:
                        messagebox.showerror(
                            "Error",
                            "No se pudo eliminar el paciente (posiblemente tiene turnos asignados)",
                        )
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Error al eliminar paciente: {str(e)}"
                    )
        else:
            messagebox.showwarning(
                "Advertencia", "Seleccione un paciente para eliminar"
            )

    def abrir_formulario_paciente(self, paciente_id=None):
        formulario = tk.Toplevel(self.frame)
        formulario.title("Nuevo Paciente" if paciente_id is None else "Editar Paciente")
        formulario.geometry("500x500")
        formulario.transient(self.frame)
        formulario.grab_set()

        # Obtener obras sociales para el combobox
        try:
            obras_sociales = self.queries.obtener_obras_sociales()
        except Exception as e:
            print(f"No se pudieron cargar las obras sociales: {str(e)}")
            obras_sociales = []

        # Campos del formulario
        ttk.Label(formulario, text="DNI:*").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        dni_entry = ttk.Entry(formulario)
        dni_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Apellido:*").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        apellido_entry = ttk.Entry(formulario)
        apellido_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Nombre:*").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        nombre_entry = ttk.Entry(formulario)
        nombre_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Teléfono:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        telefono_entry = ttk.Entry(formulario)
        telefono_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Email:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        email_entry = ttk.Entry(formulario)
        email_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Fecha Nacimiento:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )
        fecha_nac_entry = ttk.Entry(formulario)
        fecha_nac_entry.grid(row=5, column=1, padx=5, pady=5)
        fecha_nac_entry.insert(0, "YYYY-MM-DD")

        ttk.Label(formulario, text="Dirección:").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        direccion_entry = ttk.Entry(formulario)
        direccion_entry.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Obra Social:").grid(
            row=7, column=0, padx=5, pady=5, sticky="e"
        )
        obra_social_combo = ttk.Combobox(
            formulario,
            values=(
                [f"{os[0]} - {os[1]}" for os in obras_sociales]
                if obras_sociales
                else ["Particular"]
            ),
            state="readonly",
        )
        obra_social_combo.grid(row=7, column=1, padx=5, pady=5)
        if obras_sociales:
            obra_social_combo.set("Particular")

        # Cargar datos existentes si estamos editando
        if paciente_id is not None:
            try:
                paciente = self.queries.obtener_paciente_por_id(paciente_id)
                if paciente:
                    dni_entry.insert(0, paciente[1] or "")
                    apellido_entry.insert(0, paciente[2] or "")
                    nombre_entry.insert(0, paciente[3] or "")
                    telefono_entry.insert(0, paciente[4] or "")
                    email_entry.insert(0, paciente[5] or "")

                    if paciente[6]:  # Fecha de nacimiento
                        fecha_nac_entry.delete(0, tk.END)
                        fecha_nac_entry.insert(0, paciente[6].strftime("%Y-%m-%d"))

                    direccion_entry.insert(0, paciente[7] or "")

                    # Seleccionar obra social si existe
                    if paciente[8]:  # id_obra_social
                        for os in obras_sociales:
                            if os[0] == paciente[8]:
                                obra_social_combo.set(f"{os[0]} - {os[1]}")
                                break
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error al cargar datos del paciente: {str(e)}"
                )

        def guardar():
            # Validar campos obligatorios
            if (
                not dni_entry.get()
                or not apellido_entry.get()
                or not nombre_entry.get()
            ):
                messagebox.showerror("Error", "DNI, Apellido y Nombre son obligatorios")
                return

            # Validar DNI (solo números)
            try:
                int(dni_entry.get())
            except ValueError:
                messagebox.showerror("Error", "El DNI debe contener solo números")
                return

            # Validar fecha si se ingresó
            fecha_nac = fecha_nac_entry.get()
            if fecha_nac and fecha_nac != "YYYY-MM-DD":
                try:
                    datetime.strptime(fecha_nac, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(
                        "Error", "Formato de fecha incorrecto. Use YYYY-MM-DD"
                    )
                    return

            # Obtener ID de obra social
            obra_social_str = obra_social_combo.get()
            id_obra_social = None
            if obra_social_str and obra_social_str != "Particular":
                try:
                    id_obra_social = int(obra_social_str.split(" - ")[0])
                except (ValueError, IndexError):
                    pass

            # Preparar datos
            datos = (
                dni_entry.get(),
                apellido_entry.get(),
                nombre_entry.get(),
                telefono_entry.get() or None,
                email_entry.get() or None,
                fecha_nac if fecha_nac and fecha_nac != "YYYY-MM-DD" else None,
                direccion_entry.get() or None,
                id_obra_social,
            )

            try:
                if paciente_id is None:
                    # Insertar nuevo paciente
                    nuevo_id = self.queries.insertar_paciente(datos)
                    messagebox.showinfo(
                        "Éxito", f"Paciente agregado con ID: {nuevo_id}"
                    )
                else:
                    # Actualizar paciente existente
                    if self.queries.actualizar_paciente(paciente_id, datos):
                        messagebox.showinfo(
                            "Éxito", "Paciente actualizado correctamente"
                        )
                    else:
                        messagebox.showerror(
                            "Error", "No se pudo actualizar el paciente"
                        )

                formulario.destroy()
                self.load_pacientes()

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar paciente: {str(e)}")

        # Botones del formulario
        button_frame = ttk.Frame(formulario)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Guardar", command=guardar).pack(
            side="left", padx=10
        )
        ttk.Button(button_frame, text="Cancelar", command=formulario.destroy).pack(
            side="left", padx=10
        )
