# modules/reportes.py
def generar_reporte_facturacion(self, fecha_inicio, fecha_fin):
    query = """
    SELECT os.nombre AS obra_social, SUM(f.monto) AS total_facturado,
           COUNT(f.id_factura) AS cantidad_facturas
    FROM Facturacion f
    JOIN Turno t ON t.id_turno = f.id_turno
    JOIN Paciente p ON p.id_paciente = t.id_paciente
    JOIN ObraSocial os ON os.id_obra_social = p.id_obra_social
    WHERE f.fecha_emision BETWEEN %s AND %s
    GROUP BY os.nombre
    """
