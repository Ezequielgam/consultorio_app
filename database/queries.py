# database/queries.py
from mysql.connector import Error


class PacientesQueries:
    def __init__(self, connection):
        self.connection = connection

    def obtener_pacientes_para_combo(self):
        """Obtener pacientes para combobox (id, nombre_completo)"""
        query = """
        SELECT id_paciente, CONCAT(apellido, ', ', nombre) as nombre_completo
        FROM Paciente
        ORDER BY apellido, nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_pacientes(self):
        """Obtener todos los pacientes con información completa"""
        query = """
        SELECT p.id_paciente, p.dni, p.apellido, p.nombre, p.telefono, 
               p.correo_electronico, p.fecha_de_nacimiento, p.direccion,
               COALESCE(os.nombre, 'Particular') as obra_social
        FROM Paciente p
        LEFT JOIN ObraSocial os ON p.id_obra_social = os.id_obra_social
        ORDER BY p.apellido, p.nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_paciente_por_id(self, paciente_id):
        """Obtener un paciente específico por ID"""
        query = """
        SELECT id_paciente, dni, apellido, nombre, telefono, 
               correo_electronico, fecha_de_nacimiento, direccion, id_obra_social
        FROM Paciente
        WHERE id_paciente = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (paciente_id,))
        return cursor.fetchone()

    def buscar_paciente_por_dni(self, dni):
        """Buscar paciente por DNI"""
        query = """
        SELECT p.id_paciente, p.dni, p.apellido, p.nombre, p.telefono, 
               p.correo_electronico, p.fecha_de_nacimiento, p.direccion,
               COALESCE(os.nombre, 'Particular') as obra_social
        FROM Paciente p
        LEFT JOIN ObraSocial os ON p.id_obra_social = os.id_obra_social
        WHERE p.dni LIKE %s
        ORDER BY p.apellido, p.nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (f"%{dni}%",))
        return cursor.fetchall()

    def insertar_paciente(self, datos_paciente):
        """Insertar nuevo paciente"""
        query = """
        INSERT INTO Paciente (dni, apellido, nombre, telefono, correo_electronico, 
                         fecha_de_nacimiento, direccion, id_obra_social)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, datos_paciente)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e

    def actualizar_paciente(self, paciente_id, datos_paciente):
        """Actualizar paciente existente"""
        query = """
        UPDATE Paciente 
        SET dni = %s, apellido = %s, nombre = %s, telefono = %s, 
            correo_electronico = %s, fecha_de_nacimiento = %s, direccion = %s, id_obra_social = %s
        WHERE id_paciente = %s
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (*datos_paciente, paciente_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e

    def eliminar_paciente(self, paciente_id):
        """Eliminar paciente con verificación"""
        # Verificar si el paciente tiene turnos
        query_check = "SELECT COUNT(*) FROM Turno WHERE id_paciente = %s"
        cursor = self.connection.cursor()
        cursor.execute(query_check, (paciente_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False

        try:
            query_delete = "DELETE FROM Paciente WHERE id_paciente = %s"
            cursor.execute(query_delete, (paciente_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            return False

    def obtener_obras_sociales(self):
        """Obtener todas las obras sociales"""
        query = """
        SELECT id_obra_social, nombre
        FROM ObraSocial
        ORDER BY nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()


class TurnosQueries:
    def __init__(self, connection):
        self.connection = connection

    def obtener_turnos(self, fecha_desde=None, fecha_hasta=None):
        query = """
        SELECT t.id_turno, t.fecha, t.hora, 
               p.id_paciente, CONCAT(p.apellido, ', ', p.nombre) as paciente,
               d.id_doctor, CONCAT(d.apellido, ', ', d.nombre) as doctor,
               t.motivo_de_consulta, 
               CASE WHEN t.es_particular THEN 'Particular' ELSE 'Obra Social' END as tipo
        FROM Turno t
        JOIN Paciente p ON t.id_paciente = p.id_paciente
        JOIN Doctor d ON t.id_doctor = d.id_doctor
        WHERE 1=1
        """
        params = []
        if fecha_desde:
            query += " AND t.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND t.fecha <= %s"
            params.append(fecha_hasta)
        query += " ORDER BY t.fecha, t.hora"
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def obtener_turnos_proximos(self):
        query = """
        SELECT t.id_turno, t.fecha, t.hora, 
               p.id_paciente, CONCAT(p.apellido, ', ', p.nombre) as paciente,
               d.id_doctor, CONCAT(d.apellido, ', ', d.nombre) as doctor,
               t.motivo_de_consulta, 
               CASE WHEN t.es_particular THEN 'Particular' ELSE 'Obra Social' END as tipo
        FROM Turno t
        JOIN Paciente p ON t.id_paciente = p.id_paciente
        JOIN Doctor d ON t.id_doctor = d.id_doctor
        WHERE t.fecha >= CURDATE()
        ORDER BY t.fecha, t.hora
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_turno_por_id(self, turno_id):
        query = """
        SELECT id_turno, id_paciente, id_doctor, fecha, hora, motivo_de_consulta, es_particular
        FROM Turno
        WHERE id_turno = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (turno_id,))
        return cursor.fetchone()

    def insertar_turno(self, datos_turno):
        query = """
        INSERT INTO Turno (id_paciente, id_doctor, fecha, hora, motivo_de_consulta, es_particular)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, datos_turno)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e

    def actualizar_turno(self, turno_id, datos_turno):
        query = """
        UPDATE Turno 
        SET id_paciente = %s, id_doctor = %s, fecha = %s, hora = %s, 
            motivo_de_consulta = %s, es_particular = %s
        WHERE id_turno = %s
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (*datos_turno, turno_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e

    def eliminar_turno(self, turno_id):
        # Verificar si el turno tiene facturación
        query_check = "SELECT COUNT(*) FROM Facturacion WHERE id_turno = %s"
        cursor = self.connection.cursor()
        cursor.execute(query_check, (turno_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return (
                False,
                "No se puede eliminar el turno porque tiene facturación asociada",
            )

        try:
            query_delete = "DELETE FROM Turno WHERE id_turno = %s"
            cursor.execute(query_delete, (turno_id,))
            self.connection.commit()
            return True, "Turno eliminado correctamente"
        except Exception as e:
            self.connection.rollback()
            return False, f"Error al eliminar turno: {str(e)}"

    def verificar_disponibilidad(self, doctor_id, fecha, hora):
        query = """
        SELECT COUNT(*) 
        FROM Turno 
        WHERE id_doctor = %s AND fecha = %s AND hora = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (doctor_id, fecha, hora))
        count = cursor.fetchone()[0]
        return count == 0


class DoctoresQueries:
    def __init__(self, connection):
        self.connection = connection

    def obtener_doctores_para_combo(self):
        """Obtener doctores para combobox (id, nombre_completo)"""
        query = """
        SELECT id_doctor, CONCAT(apellido, ', ', nombre) as nombre_completo
        FROM Doctor
        ORDER BY apellido, nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_doctores(self):
        """Obtener todos los doctores"""
        query = """
        SELECT id_doctor, dni, matricula, apellido, nombre, telefono, 
               correo_electronico, especialidad
        FROM Doctor
        ORDER BY apellido, nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_doctor_por_id(self, doctor_id):
        """Obtener un doctor específico por ID"""
        query = """
        SELECT id_doctor, dni, matricula, apellido, nombre, telefono, 
               correo_electronico, especialidad
        FROM Doctor
        WHERE id_doctor = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (doctor_id,))
        return cursor.fetchone()

    def insertar_doctor(self, datos_doctor):
        """Insertar nuevo doctor"""
        query = """
        INSERT INTO Doctor (dni, matricula, apellido, nombre, telefono, 
                          correo_electronico, especialidad)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, datos_doctor)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e

    def actualizar_doctor(self, doctor_id, datos_doctor):
        """Actualizar doctor existente"""
        query = """
        UPDATE Doctor 
        SET dni = %s, matricula = %s, apellido = %s, nombre = %s, 
            telefono = %s, correo_electronico = %s, especialidad = %s
        WHERE id_doctor = %s
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (*datos_doctor, doctor_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e

    def eliminar_doctor(self, doctor_id):
        """Eliminar doctor con verificación"""
        # Verificar si el doctor tiene turnos
        query_check = "SELECT COUNT(*) FROM Turno WHERE id_doctor = %s"
        cursor = self.connection.cursor()
        cursor.execute(query_check, (doctor_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False, "No se puede eliminar el doctor porque tiene turnos asignados"

        try:
            query_delete = "DELETE FROM Doctor WHERE id_doctor = %s"
            cursor.execute(query_delete, (doctor_id,))
            self.connection.commit()
            return True, "Doctor eliminado correctamente"
        except Exception as e:
            self.connection.rollback()
            return False, f"Error al eliminar doctor: {str(e)}"


class LoginQueries:
    def __init__(self, connection):
        self.connection = connection

    def verificar_usuario(self, usuario, password):
        """Verificar credenciales de usuario"""
        query = """
        SELECT u.id_usuario, u.nombre_usuario, r.nombre_rol, 
               COALESCE(CONCAT(d.apellido, ', ', d.nombre), 'Sistema') as nombre_completo
        FROM Usuario u
        JOIN Rol r ON u.id_rol = r.id_rol
        LEFT JOIN Doctor d ON u.id_doctor = d.id_doctor
        WHERE u.nombre_usuario = %s AND u.contrasena = SHA2(%s, 256)
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (usuario, password))
        return cursor.fetchone()

    def obtener_roles(self):
        """Obtener todos los roles disponibles"""
        query = "SELECT id_rol, nombre_rol FROM Rol ORDER BY nombre_rol"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()


class UsuariosQueries:
    def __init__(self, connection):
        self.connection = connection

    def obtener_usuarios(self):
        """Obtener todos los usuarios con información de rol y doctor"""
        query = """
        SELECT u.id_usuario, u.nombre_usuario, r.nombre_rol, 
               COALESCE(CONCAT(d.apellido, ', ', d.nombre), 'No asignado') as doctor_asignado
        FROM Usuario u
        JOIN Rol r ON u.id_rol = r.id_rol
        LEFT JOIN Doctor d ON u.id_doctor = d.id_doctor
        ORDER BY u.nombre_usuario
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_usuario_por_id(self, usuario_id):
        """Obtener un usuario específico por ID"""
        query = """
        SELECT id_usuario, nombre_usuario, id_rol, id_doctor
        FROM Usuario
        WHERE id_usuario = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (usuario_id,))
        return cursor.fetchone()

    def insertar_usuario(self, datos_usuario):
        """Insertar nuevo usuario con contraseña encriptada"""
        query = """
        INSERT INTO Usuario (nombre_usuario, contrasena, id_rol, id_doctor)
        VALUES (%s, SHA2(%s, 256), %s, %s)
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, datos_usuario)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e

    def actualizar_usuario(self, usuario_id, datos_usuario):
        """Actualizar usuario existente"""
        query = """
        UPDATE Usuario 
        SET nombre_usuario = %s, id_rol = %s, id_doctor = %s
        WHERE id_usuario = %s
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (*datos_usuario, usuario_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e

    def actualizar_contrasena(self, usuario_id, nueva_contrasena):
        """Actualizar contraseña del usuario"""
        query = "UPDATE Usuario SET contrasena = SHA2(%s, 256) WHERE id_usuario = %s"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (nueva_contrasena, usuario_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e

    def eliminar_usuario(self, usuario_id):
        """Eliminar usuario"""
        try:
            query = "DELETE FROM Usuario WHERE id_usuario = %s"
            cursor = self.connection.cursor()
            cursor.execute(query, (usuario_id,))
            self.connection.commit()
            return True, "Usuario eliminado correctamente"
        except Exception as e:
            self.connection.rollback()
            return False, f"Error al eliminar usuario: {str(e)}"

    def obtener_roles(self):
        """Obtener todos los roles"""
        query = "SELECT id_rol, nombre_rol FROM Rol ORDER BY nombre_rol"
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_doctores_para_combo(self):
        """Obtener doctores para combobox"""
        query = """
        SELECT id_doctor, CONCAT(apellido, ', ', nombre) as nombre_completo
        FROM Doctor
        ORDER BY apellido, nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def verificar_nombre_usuario(self, nombre_usuario, exclude_id=None):
        """Verificar si el nombre de usuario ya existe"""
        if exclude_id:
            query = "SELECT COUNT(*) FROM Usuario WHERE nombre_usuario = %s AND id_usuario != %s"
            params = (nombre_usuario, exclude_id)
        else:
            query = "SELECT COUNT(*) FROM Usuario WHERE nombre_usuario = %s"
            params = (nombre_usuario,)

        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0] > 0


class FacturacionQueries:
    def __init__(self, connection):
        self.connection = connection

    def obtener_facturas(self):
        """Obtener todas las facturas con información relacionada"""
        query = """
        SELECT f.id_factura, t.id_turno, f.fecha_emision, f.monto, 
               f.observacion, f.pagado,
               CONCAT(p.apellido, ', ', p.nombre) as paciente,
               CONCAT(d.apellido, ', ', d.nombre) as doctor,
               CASE WHEN t.es_particular THEN 'Particular' ELSE os.nombre END as tipo_pago
        FROM Facturacion f
        JOIN Turno t ON f.id_turno = t.id_turno
        JOIN Paciente p ON t.id_paciente = p.id_paciente
        JOIN Doctor d ON t.id_doctor = d.id_doctor
        LEFT JOIN ObraSocial os ON p.id_obra_social = os.id_obra_social
        ORDER BY f.fecha_emision DESC
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_factura_por_id(self, factura_id):
        """Obtener una factura específica por ID"""
        query = """
        SELECT id_factura, id_turno, fecha_emision, monto, observacion, pagado
        FROM Facturacion
        WHERE id_factura = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (factura_id,))
        return cursor.fetchone()

    def obtener_turnos_sin_facturar(self):
        """Obtener turnos que no tienen factura asociada"""
        query = """
        SELECT t.id_turno, t.fecha, t.hora,
               CONCAT(p.apellido, ', ', p.nombre) as paciente,
               CONCAT(d.apellido, ', ', d.nombre) as doctor,
               CASE WHEN t.es_particular THEN 'Particular' ELSE os.nombre END as tipo
        FROM Turno t
        JOIN Paciente p ON t.id_paciente = p.id_paciente
        JOIN Doctor d ON t.id_doctor = d.id_doctor
        LEFT JOIN ObraSocial os ON p.id_obra_social = os.id_obra_social
        WHERE t.id_turno NOT IN (SELECT id_turno FROM Facturacion)
        ORDER BY t.fecha, t.hora
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def insertar_factura(self, datos_factura):
        """Insertar nueva factura"""
        query = """
        INSERT INTO Facturacion (id_turno, fecha_emision, monto, observacion, pagado)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, datos_factura)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e

    def actualizar_factura(self, factura_id, datos_factura):
        """Actualizar factura existente"""
        query = """
        UPDATE Facturacion 
        SET id_turno = %s, fecha_emision = %s, monto = %s, observacion = %s, pagado = %s
        WHERE id_factura = %s
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (*datos_factura, factura_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e

    def eliminar_factura(self, factura_id):
        """Eliminar factura"""
        try:
            query = "DELETE FROM Facturacion WHERE id_factura = %s"
            cursor = self.connection.cursor()
            cursor.execute(query, (factura_id,))
            self.connection.commit()
            return True, "Factura eliminada correctamente"
        except Exception as e:
            self.connection.rollback()
            return False, f"Error al eliminar factura: {str(e)}"

    def marcar_como_pagada(self, factura_id):
        """Marcar factura como pagada"""
        query = "UPDATE Facturacion SET pagado = TRUE WHERE id_factura = %s"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (factura_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e


class FichaMedicaQueries:
    def __init__(self, connection):
        self.connection = connection

    def obtener_fichas_medicas(self):
        """Obtener todas las fichas médicas con información de paciente y doctor"""
        query = """
        SELECT f.id_ficha_medica, p.id_paciente,
               CONCAT(p.apellido, ', ', p.nombre) as paciente,
               COALESCE(CONCAT(d.apellido, ', ', d.nombre), 'No asignado') as doctor,
               f.fecha_apertura, f.grupo_sanguineo
        FROM FichaMedica f
        JOIN Paciente p ON f.id_paciente = p.id_paciente
        LEFT JOIN Doctor d ON f.id_doctor = d.id_doctor
        ORDER BY f.fecha_apertura DESC
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def obtener_ficha_medica_por_id(self, ficha_id):
        """Obtener una ficha médica específica por ID"""
        query = """
        SELECT id_ficha_medica, id_paciente, id_doctor, fecha_apertura, 
               grupo_sanguineo, alergias, antecedentes_personales, 
               antecedentes_familiares, medicacion_actual
        FROM FichaMedica
        WHERE id_ficha_medica = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (ficha_id,))
        resultado = cursor.fetchone()
        print(f"🔍 Query ficha ID {ficha_id}: {resultado}")  # Debug
        return resultado

    def obtener_ficha_medica_por_paciente(self, paciente_id):
        """Obtener ficha médica por ID de paciente"""
        query = """
        SELECT id_ficha_medica, id_paciente, id_doctor, fecha_apertura, 
               grupo_sanguineo, alergias, antecedentes_personales, 
               antecedentes_familiares, medicacion_actual
        FROM FichaMedica
        WHERE id_paciente = %s
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (paciente_id,))
        return cursor.fetchone()

    def insertar_ficha_medica(self, datos_ficha):
        """Insertar nueva ficha médica"""
        query = """
        INSERT INTO FichaMedica (id_paciente, id_doctor, fecha_apertura, 
                         grupo_sanguineo, alergias, antecedentes_personales, 
                         antecedentes_familiares, medicacion_actual)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, datos_ficha)
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            raise e

    def actualizar_ficha_medica(self, ficha_id, datos_ficha):
        """Actualizar ficha médica existente"""
        query = """
        UPDATE FichaMedica 
        SET id_paciente = %s, id_doctor = %s, fecha_apertura = %s, 
            grupo_sanguineo = %s, alergias = %s, antecedentes_personales = %s, 
            antecedentes_familiares = %s, medicacion_actual = %s
        WHERE id_ficha_medica = %s
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (*datos_ficha, ficha_id))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.connection.rollback()
            raise e

    def eliminar_ficha_medica(self, ficha_id):
        """Eliminar ficha médica"""
        try:
            # Verificar si hay consultas asociadas
            query_check = (
                "SELECT COUNT(*) FROM ConsultaMedica WHERE id_ficha_medica = %s"
            )
            cursor = self.connection.cursor()
            cursor.execute(query_check, (ficha_id,))
            count = cursor.fetchone()[0]

            if count > 0:
                return (
                    False,
                    "No se puede eliminar la ficha médica porque tiene consultas asociadas",
                )

            query = "DELETE FROM FichaMedica WHERE id_ficha_medica = %s"
            cursor.execute(query, (ficha_id,))
            self.connection.commit()
            return True, "Ficha médica eliminada correctamente"
        except Exception as e:
            self.connection.rollback()
            return False, f"Error al eliminar ficha médica: {str(e)}"

    def obtener_pacientes_sin_ficha(self):
        """Obtener pacientes que no tienen ficha médica"""
        query = """
        SELECT p.id_paciente, CONCAT(p.apellido, ', ', p.nombre) as paciente
        FROM Paciente p
        WHERE p.id_paciente NOT IN (SELECT id_paciente FROM FichaMedica)
        ORDER BY p.apellido, p.nombre
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()


from mysql.connector import Error


class ConsultaMedicaQueries:
    def __init__(self, conn):
        self.conn = conn

    def obtener_consultas_por_ficha(self, ficha_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id_consulta, fecha_consulta, diagnostico, tratamiento
                FROM ConsultaMedica
                WHERE id_ficha_medica = %s
                ORDER BY fecha_consulta DESC
            """,
                (ficha_id,),
            )
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Error al obtener consultas: {e}")
            return []

    def insertar_consulta(self, datos):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO ConsultaMedica (id_ficha_medica, fecha_consulta, diagnostico, tratamiento, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """,
                datos,
            )
            self.conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"❌ Error al insertar consulta: {e}")
            self.conn.rollback()
            return None

    def obtener_consulta_por_id(self, consulta_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id_consulta, id_ficha_medica, fecha_consulta, diagnostico, tratamiento, observaciones
                FROM ConsultaMedica
                WHERE id_consulta = %s
            """,
                (consulta_id,),
            )
            return cursor.fetchone()
        except Error as e:
            print(f"❌ Error al obtener consulta por id: {e}")
            return None

    def actualizar_consulta(self, consulta_id, datos):
        # datos = (fecha, diagnostico, tratamiento, observaciones)
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE ConsultaMedica
                SET fecha_consulta = %s,
                    diagnostico = %s,
                    tratamiento = %s,
                    observaciones = %s
                WHERE id_consulta = %s
            """,
                (*datos, consulta_id),
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"❌ Error al actualizar consulta: {e}")
            self.conn.rollback()
            return False

    def eliminar_consulta(self, consulta_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM ConsultaMedica WHERE id_consulta = %s", (consulta_id,)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"❌ Error al eliminar consulta: {e}")
            self.conn.rollback()
            return False


class RecetaMedicaQueries:
    def __init__(self, conn):
        self.conn = conn

    def obtener_recetas_por_consulta(self, consulta_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id_receta, medicamento, dosis, frecuencia, duracion
                FROM RecetaMedica
                WHERE id_consulta = %s
                ORDER BY id_receta DESC
            """,
                (consulta_id,),
            )
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Error al obtener recetas: {e}")
            return []

    def insertar_receta(self, datos):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO RecetaMedica (id_consulta, medicamento, dosis, frecuencia, duracion)
                VALUES (%s, %s, %s, %s, %s)
            """,
                datos,
            )
            self.conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"❌ Error al insertar receta: {e}")
            self.conn.rollback()
            return None

    def obtener_receta_por_id(self, receta_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id_receta, id_consulta, medicamento, dosis, frecuencia, duracion
                FROM RecetaMedica
                WHERE id_receta = %s
            """,
                (receta_id,),
            )
            return cursor.fetchone()
        except Error as e:
            print(f"❌ Error al obtener receta por id: {e}")
            return None

    def actualizar_receta(self, receta_id, datos):
        # datos = (medicamento, dosis, frecuencia, duracion)
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE RecetaMedica
                SET medicamento=%s, dosis=%s, frecuencia=%s, duracion=%s
                WHERE id_receta = %s
            """,
                (*datos, receta_id),
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"❌ Error al actualizar receta: {e}")
            self.conn.rollback()
            return False

    def eliminar_receta(self, receta_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM RecetaMedica WHERE id_receta = %s", (receta_id,)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"❌ Error al eliminar receta: {e}")
            self.conn.rollback()
            return False


class EstudioMedicoQueries:
    def __init__(self, conn):
        self.conn = conn

    def obtener_estudios_por_consulta(self, consulta_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id_estudio, tipo_estudio, fecha_estudio, resultados
                FROM EstudioMedico
                WHERE id_consulta = %s
                ORDER BY fecha_estudio DESC
            """,
                (consulta_id,),
            )
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Error al obtener estudios: {e}")
            return []

    def insertar_estudio(self, datos):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO EstudioMedico (id_consulta, tipo_estudio, fecha_estudio, resultados)
                VALUES (%s, %s, %s, %s)
            """,
                datos,
            )
            self.conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"❌ Error al insertar estudio: {e}")
            self.conn.rollback()
            return None

    def obtener_estudio_por_id(self, estudio_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT id_estudio, id_consulta, tipo_estudio, fecha_estudio, resultados
                FROM EstudioMedico
                WHERE id_estudio = %s
            """,
                (estudio_id,),
            )
            return cursor.fetchone()
        except Error as e:
            print(f"❌ Error al obtener estudio por id: {e}")
            return None

    def actualizar_estudio(self, estudio_id, datos):
        # datos = (tipo_estudio, fecha_estudio, resultados)
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE EstudioMedico
                SET tipo_estudio=%s, fecha_estudio=%s, resultados=%s
                WHERE id_estudio = %s
            """,
                (*datos, estudio_id),
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"❌ Error al actualizar estudio: {e}")
            self.conn.rollback()
            return False

    def eliminar_estudio(self, estudio_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM EstudioMedico WHERE id_estudio = %s", (estudio_id,)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"❌ Error al eliminar estudio: {e}")
            self.conn.rollback()
            return False
