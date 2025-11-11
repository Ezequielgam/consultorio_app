import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from database.queries import FichaMedicaQueries

# Nota: requiere que en database/queries.py importes/definas las clases:
# ConsultaMedicaQueries, RecetaMedicaQueries, EstudioMedicoQueries
# (abajo te doy el archivo de queries si prefieres agregarlo separado)


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
                    if paciente.lower() in (ficha[2] or "").lower():
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
                        # ficha[3] expected to be a date object or string
                        try:
                            fecha_val = ficha[3]
                            if isinstance(fecha_val, str):
                                fecha_var.set(fecha_val)
                            else:
                                fecha_var.set(fecha_val.strftime("%Y-%m-%d"))
                            print(f"✅ Fecha cargada: {ficha[3]}")
                        except Exception:
                            fecha_var.set(str(ficha[3]))

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

        # ... (el resto del guardar queda exactamente como antes) ...
        # para no repetir mucho código en este mensaje, lo dejé igual que tu versión original.
        # Asegurate que el bloque guardar() y botones estén completos en tu archivo final.

    def abrir_detalles_ficha(self, ficha_id):
        """
        Ventana emergente que muestra la ficha médica completa de un paciente:
         - Pestaña Consultas Médicas (lista y creación)
         - Pestaña Recetas Médicas (por consulta)
         - Pestaña Estudios Médicos (por consulta)
        """
        detalles = tk.Toplevel(self.frame)
        detalles.title("Ficha Médica Completa")
        detalles.geometry("900x600")
        detalles.transient(self.frame)
        detalles.grab_set()

        # Notebook con pestañas
        notebook = ttk.Notebook(detalles)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            from database.queries import (
                ConsultaMedicaQueries,
                RecetaMedicaQueries,
                EstudioMedicoQueries,
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar las consultas específicas: {e}",
            )
            detalles.destroy()
            return

        consulta_q = ConsultaMedicaQueries(self.connection)
        receta_q = RecetaMedicaQueries(self.connection)
        estudio_q = EstudioMedicoQueries(self.connection)

        # ================= CONSULTAS MÉDICAS =================
        # ---------- PESTAÑA: CONSULTAS MÉDICAS ----------
        consultas_frame = ttk.Frame(notebook)
        notebook.add(consultas_frame, text="🩺 Consultas Médicas")

        cols = ("ID", "Fecha", "Diagnóstico", "Tratamiento")
        tree_consultas = ttk.Treeview(
            consultas_frame, columns=cols, show="headings", height=12
        )
        for c in cols:
            tree_consultas.heading(c, text=c)
            tree_consultas.column(c, width=200 if c != "ID" else 60)
        tree_consultas.pack(fill="both", expand=True, pady=10, padx=10, side="top")

        bottom_consultas = ttk.Frame(consultas_frame)
        bottom_consultas.pack(fill="x", padx=10, pady=5, side="bottom")

        selected_consulta = tk.IntVar(value=0)

        def cargar_consultas():
            """Carga todas las consultas existentes de esta ficha médica"""
            for item in tree_consultas.get_children():
                tree_consultas.delete(item)
            try:
                consultas = consulta_q.obtener_consultas_por_ficha(ficha_id)
                if consultas:
                    for c in consultas:
                        tree_consultas.insert(
                            "",
                            "end",
                            values=(
                                c[0],
                                c[1].strftime("%Y-%m-%d") if c[1] else "",
                                c[2] or "",
                                c[3] or "",
                            ),
                        )
                else:
                    print("⚠️ No hay consultas para esta ficha médica")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar consultas: {e}")

        def nueva_consulta():
            self.abrir_formulario_consulta(
                ficha_id,
                consulta_q,
                refresh_callback=cargar_consultas,
                parent=detalles,
            )

        def editar_consulta():
            selected = tree_consultas.selection()
            if not selected:
                messagebox.showwarning(
                    "Atención", "Seleccione una consulta para editar."
                )
                return
            consulta_id = tree_consultas.item(selected[0])["values"][0]

            # Reusar formulario con mode=editar
            self.abrir_formulario_consulta(
                ficha_id,
                consulta_q,
                consulta_id=consulta_id,
                refresh_callback=cargar_consultas,
                parent=detalles,
            )

        def eliminar_consulta():
            selected = tree_consultas.selection()
            if not selected:
                messagebox.showwarning(
                    "Atención", "Seleccione una consulta para eliminar."
                )
                return
            consulta_id = tree_consultas.item(selected[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar esta consulta médica?"):
                try:
                    ok = consulta_q.eliminar_consulta(consulta_id)
                    if ok:
                        cargar_consultas()
                        messagebox.showinfo("Éxito", "Consulta eliminada.")
                    else:
                        messagebox.showerror(
                            "Error", "No se pudo eliminar la consulta."
                        )
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")

        ttk.Button(bottom_consultas, text="Nueva", command=nueva_consulta).pack(
            side="left", padx=5
        )
        ttk.Button(bottom_consultas, text="Editar", command=editar_consulta).pack(
            side="left", padx=5
        )
        ttk.Button(bottom_consultas, text="Eliminar", command=eliminar_consulta).pack(
            side="left", padx=5
        )

        # ---------- PESTAÑA: RECETAS ----------
        recetas_frame = ttk.Frame(notebook)
        notebook.add(recetas_frame, text="💊 Recetas Médicas")

        cols_r = ("ID", "Medicamento", "Dosis", "Frecuencia", "Duración")
        tree_recetas = ttk.Treeview(
            recetas_frame, columns=cols_r, show="headings", height=12
        )
        for c in cols_r:
            tree_recetas.heading(c, text=c)
            tree_recetas.column(c, width=150 if c != "ID" else 60)
        tree_recetas.pack(fill="both", expand=True, pady=10, padx=10)

        bottom_recetas = ttk.Frame(recetas_frame)
        bottom_recetas.pack(fill="x", padx=10, pady=5)

        def cargar_recetas(consulta_id):
            for i in tree_recetas.get_children():
                tree_recetas.delete(i)
            try:
                recetas = receta_q.obtener_recetas_por_consulta(consulta_id)
                for r in recetas:
                    tree_recetas.insert("", "end", values=r)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar recetas: {e}")

        def nueva_receta():
            cid = selected_consulta.get()
            if not cid:
                messagebox.showwarning("Atención", "Seleccione una consulta primero.")
                return
            win = tk.Toplevel(detalles)
            win.title("Nueva Receta Médica")
            win.geometry("420x300")
            win.transient(detalles)
            win.grab_set()

            med = tk.StringVar()
            dosis = tk.StringVar()
            frec = tk.StringVar()
            dur = tk.StringVar()

            frm = ttk.Frame(win, padding=10)
            frm.pack(fill="both", expand=True)
            ttk.Label(frm, text="Medicamento:").grid(row=0, column=0, sticky="w")
            ttk.Entry(frm, textvariable=med).grid(row=0, column=1, sticky="ew")
            ttk.Label(frm, text="Dosis:").grid(row=1, column=0, sticky="w")
            ttk.Entry(frm, textvariable=dosis).grid(row=1, column=1, sticky="ew")
            ttk.Label(frm, text="Frecuencia:").grid(row=2, column=0, sticky="w")
            ttk.Entry(frm, textvariable=frec).grid(row=2, column=1, sticky="ew")
            ttk.Label(frm, text="Duración:").grid(row=3, column=0, sticky="w")
            ttk.Entry(frm, textvariable=dur).grid(row=3, column=1, sticky="ew")

            frm.columnconfigure(1, weight=1)

            def guardar_receta():
                try:
                    receta_q.insertar_receta(
                        (cid, med.get(), dosis.get(), frec.get(), dur.get())
                    )
                    cargar_recetas(cid)
                    win.destroy()
                    messagebox.showinfo("Éxito", "Receta agregada correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar: {e}")

            ttk.Button(win, text="Guardar", command=guardar_receta).pack(pady=8)
            ttk.Button(win, text="Cancelar", command=win.destroy).pack()

        def eliminar_receta():
            selected = tree_recetas.selection()
            if not selected:
                messagebox.showwarning(
                    "Atención", "Seleccione una receta para eliminar."
                )
                return
            rec_id = tree_recetas.item(selected[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar esta receta?"):
                try:
                    ok = receta_q.eliminar_receta(rec_id)
                    if ok:
                        cargar_recetas(selected_consulta.get())
                        messagebox.showinfo("Éxito", "Receta eliminada.")
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar la receta.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")

        ttk.Button(bottom_recetas, text="Agregar", command=nueva_receta).pack(
            side="left", padx=5
        )
        ttk.Button(bottom_recetas, text="Eliminar", command=eliminar_receta).pack(
            side="left", padx=5
        )

        # ---------- PESTAÑA: ESTUDIOS ----------
        estudios_frame = ttk.Frame(notebook)
        notebook.add(estudios_frame, text="🧪 Estudios Médicos")

        cols_e = ("ID", "Tipo Estudio", "Fecha", "Resultados")
        tree_estudios = ttk.Treeview(
            estudios_frame, columns=cols_e, show="headings", height=12
        )
        for c in cols_e:
            tree_estudios.heading(c, text=c)
            tree_estudios.column(c, width=180 if c != "ID" else 60)
        tree_estudios.pack(fill="both", expand=True, pady=10, padx=10)

        bottom_estudios = ttk.Frame(estudios_frame)
        bottom_estudios.pack(fill="x", padx=10, pady=5)

        def nuevo_estudio():
            cid = selected_consulta.get()
            if not cid:
                messagebox.showwarning(
                    "Atención", "Debe seleccionar una consulta primero"
                )
                return

            win = tk.Toplevel(detalles)
            win.title("Nuevo Estudio Médico")
            win.geometry("520x400")
            win.transient(detalles)
            win.grab_set()

            tipo = tk.StringVar()
            fecha = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

            frm = ttk.Frame(win, padding=15)
            frm.pack(fill="both", expand=True)

            ttk.Label(frm, text="Tipo de Estudio:").grid(
                row=0, column=0, sticky="w", pady=5
            )
            ttk.Entry(frm, textvariable=tipo).grid(row=0, column=1, sticky="ew", pady=5)

            ttk.Label(frm, text="Fecha (YYYY-MM-DD):").grid(
                row=1, column=0, sticky="w", pady=5
            )
            ttk.Entry(frm, textvariable=fecha).grid(
                row=1, column=1, sticky="ew", pady=5
            )

            ttk.Label(frm, text="Resultados:").grid(
                row=2, column=0, sticky="nw", pady=5
            )
            resultados = tk.Text(frm, height=6, width=50)
            resultados.grid(row=2, column=1, sticky="nsew", pady=5)

            frm.columnconfigure(1, weight=1)
            frm.rowconfigure(2, weight=1)

            # --- Frame inferior con botones ---
            button_frame = ttk.Frame(win)
            button_frame.pack(fill="x", pady=10)

            def guardar_estudio():
                try:
                    estudio_q.insertar_estudio(
                        (
                            cid,
                            tipo.get(),
                            fecha.get(),
                            resultados.get("1.0", tk.END).strip(),
                        )
                    )
                    cargar_estudios(cid)
                    win.destroy()
                    messagebox.showinfo("Éxito", "Estudio guardado correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar el estudio: {e}")

            ttk.Button(button_frame, text="Guardar", command=guardar_estudio).pack(
                side="left", padx=10
            )
            ttk.Button(button_frame, text="Cancelar", command=win.destroy).pack(
                side="left", padx=10
            )

        def cargar_estudios(consulta_id):
            for i in tree_estudios.get_children():
                tree_estudios.delete(i)
            try:
                estudios = estudio_q.obtener_estudios_por_consulta(consulta_id)
                for e in estudios:
                    tree_estudios.insert("", "end", values=e)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar estudios: {e}")

        def eliminar_estudio():
            selected = tree_estudios.selection()
            if not selected:
                messagebox.showwarning(
                    "Atención", "Seleccione un estudio para eliminar."
                )
                return
            est_id = tree_estudios.item(selected[0])["values"][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar este estudio médico?"):
                try:
                    ok = estudio_q.eliminar_estudio(est_id)
                    if ok:
                        cargar_estudios(selected_consulta.get())
                        messagebox.showinfo("Éxito", "Estudio eliminado.")
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar el estudio.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo eliminar: {e}")

        ttk.Button(bottom_estudios, text="Agregar", command=nuevo_estudio).pack(
            side="left", padx=5
        )
        ttk.Button(bottom_estudios, text="Eliminar", command=eliminar_estudio).pack(
            side="left", padx=5
        )

        # Vincular selección de consulta
        def on_select_consulta(event):
            selected = tree_consultas.selection()
            if selected:
                consulta_id = tree_consultas.item(selected[0])["values"][0]
                selected_consulta.set(consulta_id)
                cargar_recetas(consulta_id)
                cargar_estudios(consulta_id)

        tree_consultas.bind("<<TreeviewSelect>>", on_select_consulta)

        # Cargar consultas al abrir la ventana
        cargar_consultas()

        footer = ttk.Frame(detalles)
        footer.pack(fill="x", padx=10, pady=8)
        ttk.Button(footer, text="Cerrar", command=detalles.destroy).pack(side="right")

    def abrir_formulario_consulta(
        self, ficha_id, consulta_q, consulta_id=None, refresh_callback=None, parent=None
    ):
        """Formulario para crear o editar una consulta médica"""
        win = tk.Toplevel(parent or self.frame)
        win.title("Editar Consulta" if consulta_id else "Nueva Consulta")
        win.geometry("520x480")
        win.transient(parent or self.frame)
        win.grab_set()

        fecha = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        diagnostico = tk.StringVar()
        tratamiento = tk.StringVar()

        frm = ttk.Frame(win, padding=10)
        frm.pack(fill="both", expand=True)

        # ---------- CAMPOS ----------
        ttk.Label(frm, text="Fecha:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=fecha).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frm, text="Diagnóstico:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=diagnostico).grid(
            row=1, column=1, sticky="ew", pady=4
        )

        ttk.Label(frm, text="Tratamiento:").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(frm, textvariable=tratamiento).grid(
            row=2, column=1, sticky="ew", pady=4
        )

        ttk.Label(frm, text="Observaciones:").grid(row=3, column=0, sticky="nw", pady=4)
        observaciones = tk.Text(frm, height=8, width=50)
        observaciones.grid(row=3, column=1, sticky="nsew", pady=4)

        # Expandir columna 1 (para que el Text se estire)
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(3, weight=1)

        # Si modo editar: cargar datos
        if consulta_id:
            try:
                consulta = consulta_q.obtener_consulta_por_id(consulta_id)
                if consulta:
                    # índices: id_consulta, id_ficha_medica, fecha_consulta, diagnostico, tratamiento, observaciones
                    if consulta[2]:
                        fecha.set(str(consulta[2])[:10])
                    diagnostico.set(consulta[3] or "")
                    tratamiento.set(consulta[4] or "")
                    if consulta[5]:
                        observaciones.insert("1.0", consulta[5])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la consulta: {e}")
                win.destroy()
                return

        # ---------- BOTONES ----------
        botones_frame = ttk.Frame(win)
        botones_frame.pack(fill="x", pady=10)

        def guardar():
            obs_text = observaciones.get("1.0", tk.END).strip()
            if consulta_id:
                # actualizar
                datos_upd = (
                    fecha.get(),
                    diagnostico.get(),
                    tratamiento.get(),
                    obs_text,
                )
                try:
                    ok = consulta_q.actualizar_consulta(consulta_id, datos_upd)
                    if ok:
                        if refresh_callback:
                            refresh_callback()
                        win.destroy()
                        messagebox.showinfo(
                            "Éxito", "Consulta actualizada correctamente."
                        )
                    else:
                        messagebox.showerror(
                            "Error", "No se pudo actualizar la consulta."
                        )
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo actualizar: {e}")
            else:
                # insertar
                datos_ins = (
                    ficha_id,
                    fecha.get(),
                    diagnostico.get(),
                    tratamiento.get(),
                    obs_text,
                )
                try:
                    nueva_id = consulta_q.insertar_consulta(datos_ins)
                    if nueva_id:
                        if refresh_callback:
                            refresh_callback()
                        win.destroy()
                        messagebox.showinfo("Éxito", "Consulta creada correctamente.")
                    else:
                        messagebox.showerror("Error", "No se pudo crear la consulta.")
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"No se pudo guardar la consulta: {e}"
                    )

        ttk.Button(botones_frame, text="Guardar", command=guardar).pack(
            side="left", padx=10
        )
        ttk.Button(botones_frame, text="Cancelar", command=win.destroy).pack(
            side="left", padx=10
        )

    # =========================
    # 🔹 CRUD: Recetas y Estudios (métodos auxiliares para uso general)
    # =========================
    def eliminar_receta(self, tree_recetas, receta_q, refresh_callback):
        selected = tree_recetas.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione una receta para eliminar.")
            return
        receta_id = tree_recetas.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmar", "¿Desea eliminar esta receta médica?"):
            try:
                ok = receta_q.eliminar_receta(receta_id)
                if ok:
                    refresh_callback()
                    messagebox.showinfo("Éxito", "Receta eliminada correctamente.")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la receta.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la receta: {e}")

    def eliminar_estudio(self, tree_estudios, estudio_q, refresh_callback):
        selected = tree_estudios.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un estudio para eliminar.")
            return
        estudio_id = tree_estudios.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmar", "¿Desea eliminar este estudio médico?"):
            try:
                ok = estudio_q.eliminar_estudio(estudio_id)
                if ok:
                    refresh_callback()
                    messagebox.showinfo("Éxito", "Estudio eliminado correctamente.")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el estudio.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el estudio: {e}")
