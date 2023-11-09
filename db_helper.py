import mysql.connector

# Define the database connection pool
db_config = {
    "host": "database-3.cpmztxgjgvr8.sa-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "alonso46",
    "database": "bd_chatbot"
}


db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool",
    pool_size=5,  # Adjust the pool size as needed
    **db_config
)

def obtener_datos_usuarios(usuario: str, contrasena: str):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                consulta = f"SELECT count(*) FROM usuarios WHERE nombre = '{usuario}' AND contrasena = '{contrasena}'"
                cursor.execute(consulta)
                contador = cursor.fetchone()[0]
                return contador
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()

    return 0

def obtener_rol_usuario(username: str):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                consulta = f"SELECT rol FROM usuarios WHERE nombre = '{username}'"
                cursor.execute(consulta)
                rol = cursor.fetchone()
                return rol[0] if rol else None
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()

    return None

def obtener_id_usuario(username: str):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                consulta = f"SELECT id FROM usuarios WHERE nombre = '{username}'"
                cursor.execute(consulta)
                id = cursor.fetchone()
                return id[0] if id else None
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()

    return None

def obtener_usuarios():
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                consulta = "SELECT nombre, contrasena, rol FROM usuarios"
                cursor.execute(consulta)
                usuarios = [{"nombre": fila[0], "contrasena": fila[1], "rol": fila[2]} for fila in cursor.fetchall()]
                return usuarios
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()

    return []

def eliminar_usuario(nombre_usuario: str):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                # Realizar la sentencia SQL para eliminar el usuario
                consulta = f"DELETE FROM usuarios WHERE nombre = '{nombre_usuario}'"
                cursor.execute(consulta)
                connection.commit()
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
    finally:
        if connection.is_connected():
            connection.close()

def registrar_usuario(nombre: str, contrasena: str, rol: str):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                # Verificar si el usuario ya existe
                consulta_existencia = f"SELECT count(*) FROM usuarios WHERE nombre = '{nombre}'"
                cursor.execute(consulta_existencia)
                contador_existencia = cursor.fetchone()[0]

                if contador_existencia > 0:
                    # El usuario ya existe
                    raise ValueError(f"El usuario '{nombre}' ya existe en la base de datos")

                # Insertar nuevo usuario
                consulta_registro = f"INSERT INTO usuarios (nombre, contrasena, rol) VALUES ('{nombre}', '{contrasena}', '{rol}')"
                cursor.execute(consulta_registro)
                connection.commit()

    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        raise  # Re-levanta la excepción para que pueda ser manejada en el código que llama a esta función

    finally:
        if connection.is_connected():
            connection.close()

def editar_usuario(nombre_usuario: str, nuevo_nombre: str, nueva_contrasena: str, nuevo_rol: str):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                # Verificar si el usuario existe
                consulta_existencia = f"SELECT count(*) FROM usuarios WHERE nombre = '{nombre_usuario}'"
                cursor.execute(consulta_existencia)
                contador_existencia = cursor.fetchone()[0]

                if contador_existencia == 0:
                    # El usuario no existe
                    raise ValueError(f"El usuario '{nombre_usuario}' no existe en la base de datos")

                # Realizar la sentencia SQL para actualizar el usuario
                consulta_actualizacion = f"UPDATE usuarios SET nombre = '{nuevo_nombre}', contrasena = '{nueva_contrasena}', rol = '{nuevo_rol}' WHERE nombre = '{nombre_usuario}'"
                cursor.execute(consulta_actualizacion)
                connection.commit()

    except Exception as e:
        print(f"Error al editar usuario: {e}")
        raise  # Re-levanta la excepción para que pueda ser manejada en el código que llama a esta función

    finally:
        if connection.is_connected():
            connection.close()


def actualizar_notas_usuario(id_usuario: int, nota_ansiedad: str, nota_depresion: str, nota_tecnicas: str, nota_sintomas_ansiedad: str, nota_sintomas_depresion: str):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                # Verificar si el usuario existe
                consulta_existencia = f"SELECT count(*) FROM usuarios WHERE ID = {id_usuario}"
                cursor.execute(consulta_existencia)
                contador_existencia = cursor.fetchone()[0]

                if contador_existencia == 0:
                    # El usuario no existe
                    raise ValueError(f"El usuario con ID {id_usuario} no existe en la base de datos")

                # Realizar la sentencia SQL para actualizar las notas
                consulta_actualizacion = f"UPDATE NOTAS SET NOTA_ANSIEDAD = '{nota_ansiedad}', NOTA_DEPRESION = '{nota_depresion}', NOTA_TECNICAS = '{nota_tecnicas}', nota_sintomas_ansiedad = '{nota_sintomas_ansiedad}', nota_sintomas_depresion = '{nota_sintomas_depresion}' WHERE ID_USUARIO = {id_usuario}"
                cursor.execute(consulta_actualizacion)
                connection.commit()

    except Exception as e:
        print(f"Error al actualizar notas: {e}")
        raise  # Re-levanta la excepción para que pueda ser manejada en el código que llama a esta función

    finally:
        if connection.is_connected():
            connection.close()

def obtener_notas_usuario(id_usuario: int):
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                # Consultar las notas actuales del usuario
                consulta = f"SELECT NOTA_ANSIEDAD, NOTA_DEPRESION, NOTA_TECNICAS, nota_sintomas_ansiedad, nota_sintomas_depresion FROM NOTAS WHERE ID_USUARIO = {id_usuario}"
                cursor.execute(consulta)
                notas = cursor.fetchone()

                # Retornar un diccionario con las notas actuales
                return {
                    "nota_ansiedad": notas[0] if notas else "",
                    "nota_depresion": notas[1] if notas else "",
                    "nota_tecnicas": notas[2] if notas else "",
                    "nota_sintomas_ansiedad": notas[3] if notas else "",
                    "nota_sintomas_depresion": notas[4] if notas else ""
                }

    except Exception as e:
        print(f"Error al obtener notas del usuario: {e}")
    finally:
        if connection.is_connected():
            connection.close()

    return {"nota_ansiedad": "", "nota_depresion": "", "nota_tecnicas": "", "nota_sintomas_ansiedad": "", "nota_sintomas_depresion": ""}

def obtener_notas_usuarios_2():
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            with connection.cursor() as cursor:
                # Realizar la consulta SQL con COALESCE para manejar valores nulos
                consulta = """
                    SELECT 
                        usuarios.nombre AS nombre_usuario, 
                        COALESCE(NOTAS.NOTA_ANSIEDAD, '') AS nota_ansiedad,
                        COALESCE(NOTAS.NOTA_DEPRESION, '') AS nota_depresion,
                        COALESCE(NOTAS.NOTA_TECNICAS, '') AS nota_tecnicas,
                        COALESCE(NOTAS.nota_sintomas_ansiedad, '') AS nota_sintomas_ansiedad,
                        COALESCE(NOTAS.nota_sintomas_depresion, '') AS nota_sintomas_depresion
                    FROM NOTAS
                    JOIN usuarios ON NOTAS.id_usuario = usuarios.id;
                """
                cursor.execute(consulta)

                # Obtener todos los resultados
                resultados = cursor.fetchall()

                # Mapear los resultados a una lista de diccionarios
                notas_usuarios = []
                for resultado in resultados:
                    notas_usuarios.append({
                        "nombre_usuario": resultado[0],
                        "nota_ansiedad": resultado[1],
                        "nota_depresion": resultado[2],
                        "nota_tecnicas": resultado[3],
                        "nota_sintomas_ansiedad": resultado[4],
                        "nota_sintomas_depresion": resultado[5]
                    })

                return notas_usuarios

    except Exception as e:
        print(f"Error al obtener notas de usuarios: {e}")
    finally:
        if connection.is_connected():
            connection.close()

    return []

