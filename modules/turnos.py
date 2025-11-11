import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from database.queries import TurnosQueries, DoctoresQueries, PacientesQueries


class TurnosModule:
    def __init__(self, parent, connection):
        self.connection = connection
        self.queries = TurnosQueries(connection)
        self.doctores_queries = DoctoresQueries(connection)
        self.pacientes_queries = PacientesQueries(connection)

        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_todos_turnos()  # Cambiado: cargar todos los turnos por defecto

    def create_widgets(self):
        # Frame de búsqueda y filtros
        filter_frame = ttk.LabelFrame(self.frame, text="Filtros de Turnos")
        filter_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(filter_frame, text="Desde:").grid(row=0, column=0, padx=5, pady=5)
        self.fecha_desde = ttk.Entry(filter_frame)
        self.fecha_desde.grid(row=0, column=1, padx=5, pady=5)
        self.fecha_desde.insert(0, "2025-01-01")  # Cambiado: fecha inicial más amplia

        ttk.Label(filter_frame, text="Hasta:").grid(row=0, column=2, padx=5, pady=5)
        self.fecha_hasta = ttk.Entry(filter_frame)
        self.fecha_hasta.grid(row=0, column=3, padx=5, pady=5)
        self.fecha_hasta.insert(0, "2025-12-31")  # Cambiado: fecha final más amplia

        ttk.Button(
            filter_frame, text="Filtrar por Fecha", command=self.filtrar_por_fecha
        ).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(
            filter_frame, text="Mostrar Próximos", command=self.load_turnos_proximos
        ).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(
            filter_frame, text="Mostrar Todos", command=self.load_todos_turnos
        ).grid(
            row=0, column=6, padx=5, pady=5
        )  # Nuevo: botón para mostrar todos

        # Treeview para mostrar turnos
        columns = (
            "ID",
            "Fecha",
            "Hora",
            "Paciente ID",
            "Paciente",
            "Doctor ID",
            "Doctor",
            "Motivo",
            "Tipo",
        )
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")

        # Configurar columnas
        column_widths = {
            "ID": 50,
            "Fecha": 100,
            "Hora": 80,
            "Paciente ID": 80,
            "Paciente": 150,
            "Doctor ID": 80,
            "Doctor": 150,
            "Motivo": 200,
            "Tipo": 100,
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))

        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame de botones
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(button_frame, text="Nuevo Turno", command=self.nuevo_turno).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Editar Turno", command=self.editar_turno).pack(
            side="left", padx=5
        )
        ttk.Button(
            button_frame, text="Eliminar Turno", command=self.eliminar_turno
        ).pack(side="left", padx=5)
        ttk.Button(
            button_frame, text="Actualizar", command=self.load_todos_turnos
        ).pack(
            side="left", padx=5
        )  # Cambiado: actualizar muestra todos

    def load_todos_turnos(self):
        """Cargar TODOS los turnos sin filtrar"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener todos los turnos sin filtros de fecha
        # Si no tienes un método para obtener todos, usamos obtener_turnos sin parámetros
        try:
            turnos = self.queries.obtener_turnos()
        except:
            # Si falla, intentamos con fechas muy amplias
            turnos = self.queries.obtener_turnos("2000-01-01", "2030-12-31")

        if turnos:
            for turno in turnos:
                self.tree.insert("", "end", values=turno)
            print(f"✅ Cargados {len(turnos)} turnos")
        else:
            print("ℹ️ No se encontraron turnos en la base de datos")

    def load_turnos_proximos(self):
        """Cargar solo turnos futuros"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        turnos = self.queries.obtener_turnos_proximos()

        if turnos:
            for turno in turnos:
                self.tree.insert("", "end", values=turno)
            print(f"✅ Cargados {len(turnos)} turnos próximos")
        else:
            print("ℹ️ No se encontraron turnos próximos")

    def filtrar_por_fecha(self):
        """Filtrar turnos por rango de fechas"""
        fecha_desde = self.fecha_desde.get()
        fecha_hasta = self.fecha_hasta.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        turnos = self.queries.obtener_turnos(fecha_desde, fecha_hasta)

        if turnos:
            for turno in turnos:
                self.tree.insert("", "end", values=turno)
            print(
                f"✅ Cargados {len(turnos)} turnos entre {fecha_desde} y {fecha_hasta}"
            )
        else:
            print(f"ℹ️ No se encontraron turnos entre {fecha_desde} y {fecha_hasta}")

    def nuevo_turno(self):
        self.abrir_formulario_turno()

    def editar_turno(self):
        selected = self.tree.selection()
        if selected:
            turno_id = self.tree.item(selected[0])["values"][0]
            self.abrir_formulario_turno(turno_id)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un turno para editar")

    def eliminar_turno(self):
        selected = self.tree.selection()
        if selected:
            turno_id = self.tree.item(selected[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este turno?"):
                success, message = self.queries.eliminar_turno(turno_id)
                if success:
                    messagebox.showinfo("Éxito", message)
                    self.load_todos_turnos()  # Cambiado: recargar todos los turnos
                else:
                    messagebox.showerror("Error", message)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un turno para eliminar")

    def abrir_formulario_turno(self, turno_id=None):
        formulario = tk.Toplevel(self.frame)
        formulario.title("Nuevo Turno" if turno_id is None else "Editar Turno")
        formulario.geometry("500x400")
        formulario.transient(self.frame.winfo_toplevel())
        formulario.grab_set()

        # Obtener listas de pacientes y doctores
        try:
            # Pacientes: intentar método específico para combo, si no existe, intentar métodos alternativos
            try:
                pacientes = self.pacientes_queries.obtener_pacientes_para_combo()
            except AttributeError:
                if hasattr(self.pacientes_queries, "obtener_pacientes"):
                    pacientes = self.pacientes_queries.obtener_pacientes()
                elif hasattr(self.pacientes_queries, "listar_pacientes"):
                    pacientes = self.pacientes_queries.listar_pacientes()
                else:
                    raise AttributeError(
                        "No se encontró un método válido en PacientesQueries para obtener la lista de pacientes"
                    )

            # Doctores: idem para doctores
            try:
                doctores = self.doctores_queries.obtener_doctores_para_combo()
            except AttributeError:
                if hasattr(self.doctores_queries, "obtener_doctores"):
                    doctores = self.doctores_queries.obtener_doctores()
                elif hasattr(self.doctores_queries, "listar_doctores"):
                    doctores = self.doctores_queries.listar_doctores()
                else:
                    raise AttributeError(
                        "No se encontró un método válido en DoctoresQueries para obtener la lista de doctores"
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            formulario.destroy()
            return

        # Campos del formulario
        ttk.Label(formulario, text="Paciente:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        paciente_combo = ttk.Combobox(
            formulario,
            values=[f"{p[0]} - {p[1]}" for p in pacientes],
            state="readonly",
            width=40,
        )
        paciente_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Doctor:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        doctor_combo = ttk.Combobox(
            formulario,
            values=[f"{d[0]} - {d[1]}" for d in doctores],
            state="readonly",
            width=40,
        )
        doctor_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Fecha (YYYY-MM-DD):").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        fecha_entry = ttk.Entry(formulario)
        fecha_entry.grid(row=2, column=1, padx=5, pady=5)
        fecha_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        ttk.Label(formulario, text="Hora (HH:MM):").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        hora_entry = ttk.Entry(formulario)
        hora_entry.grid(row=3, column=1, padx=5, pady=5)
        hora_entry.insert(0, "09:00")

        ttk.Label(formulario, text="Motivo de Consulta:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        motivo_text = tk.Text(formulario, height=5, width=30)
        motivo_text.grid(row=4, column=1, padx=5, pady=5)

        es_particular = tk.BooleanVar()
        ttk.Checkbutton(formulario, text="Es Particular", variable=es_particular).grid(
            row=5, column=1, sticky="w", padx=5, pady=5
        )

        if turno_id is not None:
            # Cargar datos existentes
            try:
                turno = self.queries.obtener_turno_por_id(turno_id)
                if turno:
                    # Buscar el paciente y doctor en las listas
                    for p in pacientes:
                        if p[0] == turno[1]:
                            paciente_combo.set(f"{p[0]} - {p[1]}")
                            break
                    for d in doctores:
                        if d[0] == turno[2]:
                            doctor_combo.set(f"{d[0]} - {d[1]}")
                            break

                    # Formatear fecha y hora
                    fecha_entry.delete(0, tk.END)
                    fecha_entry.insert(
                        0, turno[3].strftime("%Y-%m-%d") if turno[3] else ""
                    )

                    hora_entry.delete(0, tk.END)
                    if turno[4]:
                        # Convertir tiempo a string (HH:MM)
                        hora_str = str(turno[4])
                        if len(hora_str) >= 5:  # Formato HH:MM:SS
                            hora_str = hora_str[:5]  # Tomar solo HH:MM
                        hora_entry.insert(0, hora_str)

                    motivo_text.delete("1.0", tk.END)
                    motivo_text.insert("1.0", turno[5] or "")
                    es_particular.set(turno[6] if turno[6] is not None else False)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar turno: {str(e)}")

        def guardar():
            # Obtener IDs de paciente y doctor
            paciente_str = paciente_combo.get()
            doctor_str = doctor_combo.get()
            if not paciente_str or not doctor_str:
                messagebox.showerror("Error", "Debe seleccionar paciente y doctor")
                return

            try:
                paciente_id = int(paciente_str.split(" - ")[0])
                doctor_id = int(doctor_str.split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror(
                    "Error", "Error al obtener ID de paciente o doctor"
                )
                return

            fecha = fecha_entry.get()
            hora = hora_entry.get()
            motivo = motivo_text.get("1.0", tk.END).strip()
            particular = es_particular.get()

            # Validar fecha y hora
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
                # Asegurar formato HH:MM:SS
                if ":" in hora and len(hora.split(":")) >= 2:
                    if len(hora.split(":")) == 2:
                        hora = hora + ":00"  # Agregar segundos si no están
                else:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Formato de fecha u hora incorrecto\nFecha: YYYY-MM-DD\nHora: HH:MM",
                )
                return

            # Verificar disponibilidad (solo para nuevo turno)
            if turno_id is None:
                try:
                    if not self.queries.verificar_disponibilidad(
                        doctor_id, fecha, hora
                    ):
                        messagebox.showerror(
                            "Error", "El doctor ya tiene un turno en esa fecha y hora"
                        )
                        return
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Error al verificar disponibilidad: {str(e)}"
                    )
                    return

            datos = (paciente_id, doctor_id, fecha, hora, motivo, particular)

            try:
                if turno_id is None:
                    nuevo_id = self.queries.insertar_turno(datos)
                    messagebox.showinfo("Éxito", f"Turno agregado con ID: {nuevo_id}")
                else:
                    if self.queries.actualizar_turno(turno_id, datos):
                        messagebox.showinfo("Éxito", "Turno actualizado correctamente")
                    else:
                        messagebox.showerror("Error", "No se pudo actualizar el turno")
                formulario.destroy()
                self.load_todos_turnos()  # Recargar la lista de turnos
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        ttk.Button(formulario, text="Guardar", command=guardar).grid(
            row=6, column=0, columnspan=2, pady=10
        )
