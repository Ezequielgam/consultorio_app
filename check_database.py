# check_database.py
from database.connection import DatabaseConnection


def verificar_base_datos():
    print("🔍 Verificando conexión a la base de datos...")

    db = DatabaseConnection()
    connection = db.connect()

    if connection:
        print("✅ Conexión exitosa!")

        # Verificar tablas
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()

        print(f"📊 Tablas encontradas: {len(tablas)}")
        for tabla in tablas:
            print(f"   - {tabla[0]}")

        # Verificar datos de ejemplo
        cursor.execute("SELECT COUNT(*) FROM Doctor")
        doctores = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Paciente")
        pacientes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Turno")
        turnos = cursor.fetchone()[0]

        print(f"👨‍⚕️ Doctores: {doctores}")
        print(f"👥 Pacientes: {pacientes}")
        print(f"📅 Turnos: {turnos}")

        db.disconnect()
    else:
        print("❌ No se pudo conectar a la base de datos")


if __name__ == "__main__":
    verificar_base_datos()
