# modules/ficha_medica.py
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
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar fichas médicas: {str(e)}")

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

    def abrir_formulario_ficha(self, ficha_id=None):
        formulario = tk.Toplevel(self.frame)
        formulario.title(
            "Nueva Ficha Médica" if ficha_id is None else "Editar Ficha Médica"
        )
        formulario.geometry("600x500")
        formulario.transient(self.frame)
        formulario.grab_set()

        # Obtener datos para combobox
        try:
            from database.queries import PacientesQueries, DoctoresQueries

            pacientes_queries = PacientesQueries(self.connection)
            doctores_queries = DoctoresQueries(self.connection)

            if ficha_id is None:
                pacientes = self.queries.obtener_pacientes_sin_ficha()
            else:
                pacientes = pacientes_queries.obtener_pacientes_para_combo()

            doctores = doctores_queries.obtener_doctores_para_combo()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            formulario.destroy()
            return

        # Campos del formulario
        ttk.Label(formulario, text="Paciente:*").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        paciente_combo = ttk.Combobox(
            formulario, values=[f"{p[0]} - {p[1]}" for p in pacientes], state="readonly"
        )
        paciente_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Doctor:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        doctor_combo = ttk.Combobox(
            formulario,
            values=["0 - No asignado"] + [f"{d[0]} - {d[1]}" for d in doctores],
            state="readonly",
        )
        doctor_combo.grid(row=1, column=1, padx=5, pady=5)
        doctor_combo.set("0 - No asignado")

        ttk.Label(formulario, text="Fecha Apertura:*").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        fecha_apertura_entry = ttk.Entry(formulario)
        fecha_apertura_entry.grid(row=2, column=1, padx=5, pady=5)
        fecha_apertura_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        ttk.Label(formulario, text="Grupo Sanguíneo:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        grupo_sanguineo_entry = ttk.Entry(formulario)
        grupo_sanguineo_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Alergias:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        alergias_text = tk.Text(formulario, height=3, width=30)
        alergias_text.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Antecedentes Personales:").grid(
            row=5, column=0, padx=5, pady=5, sticky="e"
        )
        antecedentes_personales_text = tk.Text(formulario, height=3, width=30)
        antecedentes_personales_text.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Antecedentes Familiares:").grid(
            row=6, column=0, padx=5, pady=5, sticky="e"
        )
        antecedentes_familiares_text = tk.Text(formulario, height=3, width=30)
        antecedentes_familiares_text.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Medicación Actual:").grid(
            row=7, column=0, padx=5, pady=5, sticky="e"
        )
        medicacion_actual_text = tk.Text(formulario, height=3, width=30)
        medicacion_actual_text.grid(row=7, column=1, padx=5, pady=5)

        # Cargar datos existentes si estamos editando
        if ficha_id is not None:
            try:
                ficha = self.queries.obtener_ficha_medica_por_id(ficha_id)
                if ficha:
                    # Buscar el paciente en la lista
                    for p in pacientes:
                        if p[0] == ficha[1]:
                            paciente_combo.set(f"{p[0]} - {p[1]}")
                            break

                    # Buscar el doctor en la lista
                    if ficha[2]:  # id_doctor
                        for d in doctores:
                            if d[0] == ficha[2]:
                                doctor_combo.set(f"{d[0]} - {d[1]}")
                                break
                    else:
                        doctor_combo.set("0 - No asignado")

                    fecha_apertura_entry.delete(0, tk.END)
                    fecha_apertura_entry.insert(0, ficha[3].strftime("%Y-%m-%d"))

                    grupo_sanguineo_entry.insert(0, ficha[4] or "")

                    alergias_text.insert("1.0", ficha[5] or "")
                    antecedentes_personales_text.insert("1.0", ficha[6] or "")
                    antecedentes_familiares_text.insert("1.0", ficha[7] or "")
                    medicacion_actual_text.insert("1.0", ficha[8] or "")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar ficha médica: {str(e)}")

        def guardar():
            # Validaciones
            if not paciente_combo.get() or not fecha_apertura_entry.get():
                messagebox.showerror(
                    "Error", "Paciente y Fecha Apertura son obligatorios"
                )
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
                fecha_apertura = fecha_apertura_entry.get()
                datetime.strptime(fecha_apertura, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fecha incorrecto. Use YYYY-MM-DD"
                )
                return

            # Recoger datos de los campos de texto
            grupo_sanguineo = grupo_sanguineo_entry.get()
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
        detalles = tk.Toplevel(self.frame)
        detalles.title("Detalles de Ficha Médica")
        detalles.geometry("500x400")
        detalles.transient(self.frame)
        detalles.grab_set()

        try:
            ficha = self.queries.obtener_ficha_medica_por_id(ficha_id)
            if not ficha:
                messagebox.showerror("Error", "No se encontró la ficha médica")
                detalles.destroy()
                return

            # Obtener información del paciente y doctor
            from database.queries import PacientesQueries, DoctoresQueries

            pacientes_queries = PacientesQueries(self.connection)
            doctores_queries = DoctoresQueries(self.connection)

            paciente = pacientes_queries.obtener_paciente_por_id(ficha[1])
            doctor = (
                doctores_queries.obtener_doctor_por_id(ficha[2]) if ficha[2] else None
            )

            # Mostrar información
            info_frame = ttk.Frame(detalles, padding="20")
            info_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(
                info_frame, text="Detalles de Ficha Médica", font=("Arial", 14, "bold")
            ).pack(pady=10)

            # Información básica
            ttk.Label(
                info_frame,
                text=f"Paciente: {paciente[2]}, {paciente[3]}",
                font=("Arial", 10, "bold"),
            ).pack(anchor="w", pady=5)

            if doctor:
                ttk.Label(info_frame, text=f"Doctor: {doctor[3]}, {doctor[4]}").pack(
                    anchor="w", pady=2
                )

            ttk.Label(info_frame, text=f"Fecha Apertura: {ficha[3]}").pack(
                anchor="w", pady=2
            )
            ttk.Label(
                info_frame, text=f"Grupo Sanguíneo: {ficha[4] or 'No especificado'}"
            ).pack(anchor="w", pady=2)

            # Información médica en frames separados
            ttk.Separator(info_frame, orient="horizontal").pack(fill="x", pady=10)

            # Alergias
            alergias_frame = ttk.LabelFrame(info_frame, text="Alergias")
            alergias_frame.pack(fill="x", pady=5)
            alergias_text = tk.Text(alergias_frame, height=3, width=50)
            alergias_text.pack(padx=5, pady=5)
            alergias_text.insert("1.0", ficha[5] or "No especificadas")
            alergias_text.config(state=tk.DISABLED)

            # Antecedentes Personales
            antecedentes_personales_frame = ttk.LabelFrame(
                info_frame, text="Antecedentes Personales"
            )
            antecedentes_personales_frame.pack(fill="x", pady=5)
            antecedentes_personales_text = tk.Text(
                antecedentes_personales_frame, height=3, width=50
            )
            antecedentes_personales_text.pack(padx=5, pady=5)
            antecedentes_personales_text.insert("1.0", ficha[6] or "No especificados")
            antecedentes_personales_text.config(state=tk.DISABLED)

            # Antecedentes Familiares
            antecedentes_familiares_frame = ttk.LabelFrame(
                info_frame, text="Antecedentes Familiares"
            )
            antecedentes_familiares_frame.pack(fill="x", pady=5)
            antecedentes_familiares_text = tk.Text(
                antecedentes_familiares_frame, height=3, width=50
            )
            antecedentes_familiares_text.pack(padx=5, pady=5)
            antecedentes_familiares_text.insert("1.0", ficha[7] or "No especificados")
            antecedentes_familiares_text.config(state=tk.DISABLED)

            # Medicación Actual
            medicacion_frame = ttk.LabelFrame(info_frame, text="Medicación Actual")
            medicacion_frame.pack(fill="x", pady=5)
            medicacion_text = tk.Text(medicacion_frame, height=3, width=50)
            medicacion_text.pack(padx=5, pady=5)
            medicacion_text.insert("1.0", ficha[8] or "No especificada")
            medicacion_text.config(state=tk.DISABLED)

            ttk.Button(info_frame, text="Cerrar", command=detalles.destroy).pack(
                pady=10
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
            detalles.destroy()
