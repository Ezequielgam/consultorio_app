import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from database.queries import FichaMedicaQueries


class FichaMedicaModule:
    def __init__(self, parent, connection):
        self.connection = connection
        self.queries = FichaMedicaQueries(connection)

        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_fichas()

    def create_widgets(self):
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(self.frame, text="Búsqueda de Fichas Médicas")
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="Paciente:").grid(row=0, column=0, padx=5, pady=5)
        self.paciente_search = ttk.Entry(search_frame)
        self.paciente_search.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(search_frame, text="Buscar", command=self.buscar_ficha).grid(
            row=0, column=2, padx=5, pady=5
        )
        ttk.Button(search_frame, text="Mostrar Todas", command=self.load_fichas).grid(
            row=0, column=3, padx=5, pady=5
        )

        # Treeview para mostrar fichas médicas
        columns = (
            "ID",
            "Paciente ID",
            "Paciente",
            "Doctor",
            "Fecha Apertura",
            "Grupo Sanguíneo",
        )
        self.tree = ttk.Treeview(
            self.frame, columns=columns, show="headings", height=15
        )

        # Configurar columnas
        column_widths = {
            "ID": 50,
            "Paciente ID": 80,
            "Paciente": 150,
            "Doctor": 150,
            "Fecha Apertura": 100,
            "Grupo Sanguíneo": 100,
        }

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

        ttk.Button(button_frame, text="Nueva Ficha", command=self.nueva_ficha).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Editar", command=self.editar_ficha).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_ficha).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Ver Detalles", command=self.ver_detalles).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Actualizar", command=self.load_fichas).pack(
            side="left", padx=5
        )

    def load_fichas(self):
        """Cargar fichas médicas en el treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            fichas = self.queries.obtener_fichas_medicas()
            for ficha in fichas:
                self.tree.insert("", "end", values=ficha)
            print(f"✅ Cargadas {len(fichas)} fichas médicas")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar fichas médicas: {str(e)}")
            print(f"❌ Error cargando fichas: {e}")

    def buscar_ficha(self):
        paciente = self.paciente_search.get()
        if paciente:
            for item in self.tree.get_children():
                self.tree.delete(item)

            try:
                fichas = self.queries.obtener_fichas_medicas()
                for ficha in fichas:
                    if (
                        paciente.lower() in ficha[2].lower()
                    ):  # Buscar en nombre del paciente
                        self.tree.insert("", "end", values=ficha)
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar ficha: {str(e)}")

    def nueva_ficha(self):
        self.abrir_formulario_ficha()

    def editar_ficha(self):
        selected = self.tree.selection()
        if selected:
            ficha_id = self.tree.item(selected[0])["values"][0]
            print(f"🔍 Editando ficha ID: {ficha_id}")
            self.abrir_formulario_ficha(ficha_id)
        else:
            messagebox.showwarning("Advertencia", "Seleccione una ficha para editar")

    def eliminar_ficha(self):
        selected = self.tree.selection()
        if selected:
            ficha_id = self.tree.item(selected[0])["values"][0]
            if messagebox.askyesno(
                "Confirmar", "¿Está seguro de eliminar esta ficha médica?"
            ):
                try:
                    success, message = self.queries.eliminar_ficha_medica(ficha_id)
                    if success:
                        messagebox.showinfo("Éxito", message)
                        self.load_fichas()
                    else:
                        messagebox.showerror("Error", message)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar ficha: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Seleccione una ficha para eliminar")

    def ver_detalles(self):
        selected = self.tree.selection()
        if selected:
            ficha_id = self.tree.item(selected[0])["values"][0]
            self.abrir_detalles_ficha(ficha_id)
        else:
            messagebox.showwarning(
                "Advertencia", "Seleccione una ficha para ver detalles"
            )

    def obtener_datos_formulario(self, ficha_id=None):
        """Obtener pacientes y doctores para el formulario con manejo de errores"""
        try:
            from database.queries import PacientesQueries, DoctoresQueries

            pacientes_queries = PacientesQueries(self.connection)
            doctores_queries = DoctoresQueries(self.connection)

            if ficha_id is None:
                # Para nueva ficha, solo pacientes sin ficha
                pacientes = self.queries.obtener_pacientes_sin_ficha()
                print(f"📝 Nuevas fichas - {len(pacientes)} pacientes sin ficha")
            else:
                # Para edición, todos los pacientes
                pacientes = pacientes_queries.obtener_pacientes_para_combo()
                print(f"📝 Editando ficha - {len(pacientes)} pacientes disponibles")

            doctores = doctores_queries.obtener_doctores_para_combo()
            print(f"👨‍⚕️ {len(doctores)} doctores disponibles")

            return pacientes, doctores

        except Exception as e:
            print(f"❌ Error obteniendo datos para formulario: {e}")
            raise e

    def abrir_formulario_ficha(self, ficha_id=None):
        formulario = tk.Toplevel(self.frame)
        formulario.title(
            "Nueva Ficha Médica" if ficha_id is None else "Editar Ficha Médica"
        )
        formulario.geometry("600x500")
        formulario.transient(self.frame)
        formulario.grab_set()

        try:
            pacientes, doctores = self.obtener_datos_formulario(ficha_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            formulario.destroy()
            return

        # Variables para almacenar datos
        paciente_var = tk.StringVar()
        doctor_var = tk.StringVar()
        fecha_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        grupo_sanguineo_var = tk.StringVar()

        # Campos del formulario
        ttk.Label(formulario, text="Paciente:*").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        paciente_combo = ttk.Combobox(
            formulario,
            values=[f"{p[0]} - {p[1]}" for p in pacientes],
            state="readonly",
            textvariable=paciente_var,
        )
        paciente_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(formulario, text="Doctor:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        doctor_combo = ttk.Combobox(
            formulario,
            values=["0 - No asignado"] + [f"{d[0]} - {d[1]}" for d in doctores],
            state="readonly",
            textvariable=doctor_var,
        )
        doctor_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        doctor_combo.set("0 - No asignado")

        ttk.Label(formulario, text="Fecha Apertura:*").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        fecha_entry = ttk.Entry(formulario, textvariable=fecha_var)
        fecha_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(formulario, text="Grupo Sanguíneo:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        grupo_sanguineo_entry = ttk.Entry(formulario, textvariable=grupo_sanguineo_var)
        grupo_sanguineo_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(formulario, text="Alergias:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        alergias_text = tk.Text(formulario, height=3, width=30)
        alergias_text.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(formulario, text="Antecedentes Personales:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )
        antecedentes_personales_text = tk.Text(formulario, height=3, width=30)
        antecedentes_personales_text.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(formulario, text="Antecedentes Familiares:").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        antecedentes_familiares_text = tk.Text(formulario, height=3, width=30)
        antecedentes_familiares_text.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(formulario, text="Medicación Actual:").grid(
            row=7, column=0, padx=5, pady=5, sticky="e"
        )
        medicacion_actual_text = tk.Text(formulario, height=3, width=30)
        medicacion_actual_text.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        # Configurar grid para que se expanda
        formulario.columnconfigure(1, weight=1)
        formulario.rowconfigure(8, weight=1)

        # Cargar datos existentes si estamos editando
        if ficha_id is not None:
            try:
                print(f"🔍 Cargando datos de ficha ID: {ficha_id}")
                ficha = self.queries.obtener_ficha_medica_por_id(ficha_id)

                if ficha:
                    print(f"✅ Ficha encontrada: {ficha}")

                    # Buscar y seleccionar paciente
                    paciente_encontrado = False
                    for p in pacientes:
                        if p[0] == ficha[1]:  # ficha[1] = id_paciente
                            paciente_combo.set(f"{p[0]} - {p[1]}")
                            paciente_encontrado = True
                            print(f"✅ Paciente seleccionado: {p[1]}")
                            break

                    if not paciente_encontrado:
                        print("⚠️ No se encontró el paciente en la lista")

                    # Buscar y seleccionar doctor
                    if ficha[2]:  # ficha[2] = id_doctor
                        doctor_encontrado = False
                        for d in doctores:
                            if d[0] == ficha[2]:
                                doctor_combo.set(f"{d[0]} - {d[1]}")
                                doctor_encontrado = True
                                print(f"✅ Doctor seleccionado: {d[1]}")
                                break
                        if not doctor_encontrado:
                            doctor_combo.set("0 - No asignado")
                            print("⚠️ No se encontró el doctor en la lista")
                    else:
                        doctor_combo.set("0 - No asignado")

                    # Fecha de apertura
                    if ficha[3]:
                        fecha_var.set(ficha[3].strftime("%Y-%m-%d"))
                        print(f"✅ Fecha cargada: {ficha[3]}")

                    # Grupo sanguíneo
                    if ficha[4]:
                        grupo_sanguineo_var.set(ficha[4])
                        print(f"✅ Grupo sanguíneo cargado: {ficha[4]}")

                    # Campos de texto
                    if ficha[5]:  # Alergias
                        alergias_text.insert("1.0", ficha[5])
                    if ficha[6]:  # Antecedentes personales
                        antecedentes_personales_text.insert("1.0", ficha[6])
                    if ficha[7]:  # Antecedentes familiares
                        antecedentes_familiares_text.insert("1.0", ficha[7])
                    if ficha[8]:  # Medicación actual
                        medicacion_actual_text.insert("1.0", ficha[8])

                    print("✅ Todos los datos cargados en el formulario")

                else:
                    messagebox.showerror("Error", "No se encontró la ficha médica")
                    formulario.destroy()
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar ficha médica: {str(e)}")
                print(f"❌ Error cargando ficha: {e}")
                formulario.destroy()
                return

        def guardar():
            # Validaciones
            if not paciente_combo.get():
                messagebox.showerror("Error", "Debe seleccionar un paciente")
                return

            if not fecha_entry.get():
                messagebox.showerror("Error", "La fecha de apertura es obligatoria")
                return

            # Obtener ID del paciente
            try:
                paciente_id = int(paciente_combo.get().split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Error al obtener ID del paciente")
                return

            # Obtener ID del doctor
            doctor_str = doctor_combo.get()
            id_doctor = None
            if doctor_str and doctor_str != "0 - No asignado":
                try:
                    id_doctor = int(doctor_str.split(" - ")[0])
                except (ValueError, IndexError):
                    pass

            # Validar fecha
            try:
                fecha_apertura = fecha_var.get()
                datetime.strptime(fecha_apertura, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fecha incorrecto. Use YYYY-MM-DD"
                )
                return

            # Recoger datos
            grupo_sanguineo = grupo_sanguineo_var.get()
            alergias = alergias_text.get("1.0", tk.END).strip()
            antecedentes_personales = antecedentes_personales_text.get(
                "1.0", tk.END
            ).strip()
            antecedentes_familiares = antecedentes_familiares_text.get(
                "1.0", tk.END
            ).strip()
            medicacion_actual = medicacion_actual_text.get("1.0", tk.END).strip()

            datos = (
                paciente_id,
                id_doctor,
                fecha_apertura,
                grupo_sanguineo or None,
                alergias or None,
                antecedentes_personales or None,
                antecedentes_familiares or None,
                medicacion_actual or None,
            )

            try:
                if ficha_id is None:
                    # Nueva ficha
                    nuevo_id = self.queries.insertar_ficha_medica(datos)
                    messagebox.showinfo(
                        "Éxito", f"Ficha médica creada con ID: {nuevo_id}"
                    )
                else:
                    # Editar ficha existente
                    if self.queries.actualizar_ficha_medica(ficha_id, datos):
                        messagebox.showinfo(
                            "Éxito", "Ficha médica actualizada correctamente"
                        )
                    else:
                        messagebox.showerror(
                            "Error", "No se pudo actualizar la ficha médica"
                        )

                formulario.destroy()
                self.load_fichas()

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error al guardar ficha médica: {str(e)}"
                )
                print(f"❌ Error guardando ficha: {e}")

        # Botones del formulario
        button_frame = ttk.Frame(formulario)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Guardar", command=guardar).pack(
            side="left", padx=10
        )
        ttk.Button(button_frame, text="Cancelar", command=formulario.destroy).pack(
            side="left", padx=10
        )

    def abrir_detalles_ficha(self, ficha_id):
        # Implementación de detalles (puedes mantener la anterior)
        detalles = tk.Toplevel(self.frame)
        detalles.title("Detalles de Ficha Médica")
        detalles.geometry("500x400")

        ttk.Label(
            detalles,
            text=f"Detalles de Ficha ID: {ficha_id}",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)
        ttk.Label(detalles, text="Funcionalidad en desarrollo").pack(pady=20)
        ttk.Button(detalles, text="Cerrar", command=detalles.destroy).pack(pady=10)
