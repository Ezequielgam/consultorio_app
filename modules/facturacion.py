# modules/facturacion.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from database.queries import FacturacionQueries


class FacturacionModule:
    def __init__(self, parent, connection):
        self.connection = connection
        self.queries = FacturacionQueries(connection)

        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.load_facturas()

    def create_widgets(self):
        # Frame de filtros
        filter_frame = ttk.LabelFrame(self.frame, text="Filtros de Facturación")
        filter_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(filter_frame, text="Desde:").grid(row=0, column=0, padx=5, pady=5)
        self.fecha_desde = ttk.Entry(filter_frame, width=12)
        self.fecha_desde.grid(row=0, column=1, padx=5, pady=5)
        self.fecha_desde.insert(0, "2025-01-01")

        ttk.Label(filter_frame, text="Hasta:").grid(row=0, column=2, padx=5, pady=5)
        self.fecha_hasta = ttk.Entry(filter_frame, width=12)
        self.fecha_hasta.grid(row=0, column=3, padx=5, pady=5)
        self.fecha_hasta.insert(0, "2025-12-31")

        ttk.Button(filter_frame, text="Filtrar", command=self.filtrar_facturas).grid(
            row=0, column=4, padx=5, pady=5
        )
        ttk.Button(filter_frame, text="Mostrar Todas", command=self.load_facturas).grid(
            row=0, column=5, padx=5, pady=5
        )

        # Treeview para mostrar facturas
        columns = (
            "ID",
            "Turno ID",
            "Fecha",
            "Monto",
            "Paciente",
            "Doctor",
            "Tipo",
            "Pagado",
        )
        self.tree = ttk.Treeview(
            self.frame, columns=columns, show="headings", height=15
        )

        # Configurar columnas
        column_widths = {
            "ID": 50,
            "Turno ID": 70,
            "Fecha": 100,
            "Monto": 80,
            "Paciente": 150,
            "Doctor": 150,
            "Tipo": 100,
            "Pagado": 80,
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

        ttk.Button(button_frame, text="Nueva Factura", command=self.nueva_factura).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Editar", command=self.editar_factura).pack(
            side="left", padx=5
        )
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_factura).pack(
            side="left", padx=5
        )
        ttk.Button(
            button_frame, text="Marcar como Pagada", command=self.marcar_pagada
        ).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self.load_facturas).pack(
            side="left", padx=5
        )

    def load_facturas(self):
        """Cargar facturas en el treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            facturas = self.queries.obtener_facturas()
            for factura in facturas:
                # Formatear datos para mostrar
                factura_formateada = (
                    factura[0],  # ID
                    factura[1],  # Turno ID
                    factura[2],  # Fecha
                    f"${factura[3]:.2f}",  # Monto
                    factura[6],  # Paciente
                    factura[7],  # Doctor
                    factura[8],  # Tipo
                    "Sí" if factura[5] else "No",  # Pagado
                )
                self.tree.insert("", "end", values=factura_formateada)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar facturas: {str(e)}")

    def filtrar_facturas(self):
        """Filtrar facturas por fecha"""
        fecha_desde = self.fecha_desde.get()
        fecha_hasta = self.fecha_hasta.get()

        # Por simplicidad, recargamos todas y filtramos en memoria
        self.load_facturas()

        # Filtro en memoria por fecha
        for item in self.tree.get_children():
            valores = self.tree.item(item)["values"]
            fecha_factura = valores[2]  # La fecha está en el índice 2
            if fecha_factura < fecha_desde or fecha_factura > fecha_hasta:
                self.tree.detach(item)

    def nueva_factura(self):
        self.abrir_formulario_factura()

    def editar_factura(self):
        selected = self.tree.selection()
        if selected:
            factura_id = self.tree.item(selected[0])["values"][0]
            self.abrir_formulario_factura(factura_id)
        else:
            messagebox.showwarning("Advertencia", "Seleccione una factura para editar")

    def eliminar_factura(self):
        selected = self.tree.selection()
        if selected:
            factura_id = self.tree.item(selected[0])["values"][0]
            if messagebox.askyesno(
                "Confirmar", "¿Está seguro de eliminar esta factura?"
            ):
                try:
                    success, message = self.queries.eliminar_factura(factura_id)
                    if success:
                        messagebox.showinfo("Éxito", message)
                        self.load_facturas()
                    else:
                        messagebox.showerror("Error", message)
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Error al eliminar factura: {str(e)}"
                    )
        else:
            messagebox.showwarning(
                "Advertencia", "Seleccione una factura para eliminar"
            )

    def marcar_pagada(self):
        selected = self.tree.selection()
        if selected:
            factura_id = self.tree.item(selected[0])["values"][0]
            try:
                if self.queries.marcar_como_pagada(factura_id):
                    messagebox.showinfo("Éxito", "Factura marcada como pagada")
                    self.load_facturas()
                else:
                    messagebox.showerror(
                        "Error", "No se pudo marcar la factura como pagada"
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar factura: {str(e)}")
        else:
            messagebox.showwarning(
                "Advertencia", "Seleccione una factura para marcar como pagada"
            )

    def abrir_formulario_factura(self, factura_id=None):
        formulario = tk.Toplevel(self.frame)
        formulario.title("Nueva Factura" if factura_id is None else "Editar Factura")
        formulario.geometry("500x400")
        formulario.transient(self.frame)
        formulario.grab_set()

        # Obtener turnos sin facturar
        try:
            if factura_id is None:
                turnos = self.queries.obtener_turnos_sin_facturar()
            else:
                # Para edición, obtener todos los turnos
                from database.queries import TurnosQueries

                turnos_queries = TurnosQueries(self.connection)
                turnos = turnos_queries.obtener_turnos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar turnos: {str(e)}")
            formulario.destroy()
            return

        # Campos del formulario
        ttk.Label(formulario, text="Turno:*").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        turno_combo = ttk.Combobox(
            formulario,
            values=[f"{t[0]} - {t[3]} con {t[4]}" for t in turnos],
            state="readonly",
            width=40,
        )
        turno_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Fecha Emisión:*").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        fecha_emision_entry = ttk.Entry(formulario)
        fecha_emision_entry.grid(row=1, column=1, padx=5, pady=5)
        fecha_emision_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        ttk.Label(formulario, text="Monto:*").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        monto_entry = ttk.Entry(formulario)
        monto_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(formulario, text="Observaciones:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        observaciones_text = tk.Text(formulario, height=4, width=30)
        observaciones_text.grid(row=3, column=1, padx=5, pady=5)

        pagado_var = tk.BooleanVar()
        ttk.Checkbutton(formulario, text="Pagado", variable=pagado_var).grid(
            row=4, column=1, sticky="w", padx=5, pady=5
        )

        # Cargar datos existentes si estamos editando
        if factura_id is not None:
            try:
                factura = self.queries.obtener_factura_por_id(factura_id)
                if factura:
                    # Buscar el turno en la lista
                    for t in turnos:
                        if t[0] == factura[1]:
                            turno_combo.set(f"{t[0]} - {t[3]} con {t[4]}")
                            break

                    fecha_emision_entry.delete(0, tk.END)
                    fecha_emision_entry.insert(0, factura[2].strftime("%Y-%m-%d"))

                    monto_entry.insert(0, str(factura[3]))

                    observaciones_text.insert("1.0", factura[4] or "")

                    pagado_var.set(factura[5])
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar factura: {str(e)}")

        def guardar():
            # Validaciones
            if not turno_combo.get():
                messagebox.showerror("Error", "Debe seleccionar un turno")
                return

            if not fecha_emision_entry.get() or not monto_entry.get():
                messagebox.showerror("Error", "Fecha y Monto son obligatorios")
                return

            # Obtener ID del turno
            try:
                turno_id = int(turno_combo.get().split(" - ")[0])
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Error al obtener ID del turno")
                return

            # Validar fecha
            try:
                fecha_emision = fecha_emision_entry.get()
                datetime.strptime(fecha_emision, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Formato de fecha incorrecto. Use YYYY-MM-DD"
                )
                return

            # Validar monto
            try:
                monto = float(monto_entry.get())
                if monto < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error", "El monto debe ser un número válido y positivo"
                )
                return

            observaciones = observaciones_text.get("1.0", tk.END).strip()
            pagado = pagado_var.get()

            datos = (turno_id, fecha_emision, monto, observaciones, pagado)

            try:
                if factura_id is None:
                    # Nueva factura
                    nuevo_id = self.queries.insertar_factura(datos)
                    messagebox.showinfo("Éxito", f"Factura creada con ID: {nuevo_id}")
                else:
                    # Editar factura existente
                    if self.queries.actualizar_factura(factura_id, datos):
                        messagebox.showinfo(
                            "Éxito", "Factura actualizada correctamente"
                        )
                    else:
                        messagebox.showerror(
                            "Error", "No se pudo actualizar la factura"
                        )

                formulario.destroy()
                self.load_facturas()

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar factura: {str(e)}")

        # Botones del formulario
        button_frame = ttk.Frame(formulario)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Guardar", command=guardar).pack(
            side="left", padx=10
        )
        ttk.Button(button_frame, text="Cancelar", command=formulario.destroy).pack(
            side="left", padx=10
        )
