# check_pacientes.py
from database.connection import DatabaseConnection
from database.queries import PacientesQueries


def verificar_estructura_pacientes():
    print("🔍 Verificando estructura de datos de pacientes...")

    db = DatabaseConnection()
    connection = db.connect()

    if not connection:
        print("❌ No se pudo conectar a la base de datos")
        return

    queries = PacientesQueries(connection)

    try:
        # Verificar la consulta obtener_pacientes
        print("\n📋 Verificando obtener_pacientes():")
        pacientes = queries.obtener_pacientes()

        if pacientes:
            print(f"Se encontraron {len(pacientes)} pacientes")
            print(f"Estructura del primer paciente: {pacientes[0]}")
            print(f"Número de columnas: {len(pacientes[0])}")

            # Mostrar todas las columnas del primer paciente
            for i, valor in enumerate(pacientes[0]):
                print(f"  Columna {i}: {valor} (tipo: {type(valor)})")
        else:
            print("No se encontraron pacientes")

    except Exception as e:
        print(f"❌ Error al verificar pacientes: {e}")

    try:
        # Verificar la consulta obtener_obras_sociales
        print("\n🏥 Verificando obtener_obras_sociales():")
        obras_sociales = queries.obtener_obras_sociales()

        if obras_sociales:
            print(f"Se encontraron {len(obras_sociales)} obras sociales")
            print(f"Estructura: {obras_sociales[0]}")
        else:
            print("No se encontraron obras sociales")

    except Exception as e:
        print(f"❌ Error al verificar obras sociales: {e}")

    db.disconnect()


if __name__ == "__main__":
    verificar_estructura_pacientes()
