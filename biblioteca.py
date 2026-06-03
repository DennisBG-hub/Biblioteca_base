import sqlite3
from pathlib import Path

# CONFIGURACIÓN INICIAL Y RUTAS"""
RUTA_BD = Path(__file__).resolve().parent / "bd" / "biblioteca.db"
RUTA_BD.parent.mkdir(parents=True, exist_ok=True)

# Variables globales para mantener compatibilidad absoluta con tests antiguos
libros = []
bd = libros
usuarios = []
modo = "normal"
ultimo_error = ""


# ENTIDADES / CLASES

class Libro:
    """Clase que representa la entidad de un Libro (Fase 4)."""

    def __init__(self, titulo: str, autor: str, disponible: bool = True, id_libro: int = None):
        self.id = id_libro
        self.titulo = titulo
        self.autor = autor
        self.disponible = disponible


class Usuario:
    """Clase que representa la entidad de un Usuario (Fase 5)."""

    def __init__(self, nombre: str, apellidos: str, email: str, habilitado: bool = True, id_usuario: int = None):
        self.id = id_usuario
        self.nombre = nombre
        self.apellidos = apellidos
        self.email = email
        self.habilitado = habilitado

        # INICIALIZACIÓN DE TABLAS SQLITE


def inicializar_tablas():
    """Crea las tablas necesarias si no existen en la base de datos."""
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON")

        # Tabla de Libros (Fase 4)
        conexion.execute(""" CREATE TABLE IF NOT EXISTS libros
                         ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                            titulo TEXT NOT NULL,
                            autor TEXT NOT NULL,
                            disponible INTEGER DEFAULT 1 ) """)

        # Tabla de Usuarios (Fase 5)
        conexion.execute(""" CREATE TABLE IF NOT EXISTS usuarios
                         ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            apellidos TEXT NOT NULL,
                            email TEXT UNIQUE NOT NULL,
                            habilitado INTEGER DEFAULT 1 ) """)

        conexion.execute(""" CREATE TABLE IF NOT EXISTS prestamos
                         ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                             libro_id INTEGER NOT NULL,
                             usuario_id INTEGER NOT NULL,
                             FOREIGN KEY ( libro_id ) REFERENCES libros ( id ),
                             FOREIGN KEY ( usuario_id ) REFERENCES usuarios ( id ))""")

        # Tabla de Logs (Fase 7)
        conexion.execute(""" CREATE TABLE IF NOT EXISTS logs
                         ( id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                             accion TEXT NOT NULL,
                             fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP )""")

        conexion.commit()

# Forzar la creación de las tablas al importar el módulo
inicializar_tablas()


# MÉTODOS CRUD - LIBROS


def agregar_libro(titulo: str, autor: str) -> None:
    """Añade un libro a la base de datos de manera persistente."""
    global ultimo_error
    try:
        with sqlite3.connect(RUTA_BD) as conexion:
            conexion.execute(
                "INSERT INTO libros (titulo, autor, disponible) VALUES (?, ?, 1)",
                (titulo, autor)
            )
            conexion.commit()
        ultimo_error = ""
    except sqlite3.Error as e:
        ultimo_error = f"Error de BD: {str(e)}"


def remove_libro(id_libro: int) -> bool:
    """Elimina un libro del catálogo por su identificador ID."""
    global ultimo_error
    try:
        with sqlite3.connect(RUTA_BD) as conexion:
            cursor = conexion.execute("DELETE FROM libros WHERE id = ?", (id_libro,))
            conexion.commit()
            if cursor.rowcount > 0:
                ultimo_error = ""
                return True
            else:
                ultimo_error = "Libro no encontrado"
                return False
    except sqlite3.Error as e:
        ultimo_error = f"Error de BD: {str(e)}"
        return False


def buscar_libro(titulo: str) -> dict | None:
    """Busca un libro por su título exacto (Retorna un diccionario)."""
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute(
            "SELECT id, titulo, autor, disponible FROM libros WHERE titulo = ?",
            (titulo,)
        )
        fila = cursor.fetchone()
    if fila:
        return {
            "id": fila[0],
            "titulo": fila[1],
            "autor": fila[2],
            "disponible": bool(fila[3])
        }
    return None


def mostrar_libros() -> None:
    """Muestra la lista completa de libros en consola."""
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT titulo, autor, disponible FROM libros")
        filas = cursor.fetchall()
    if not filas:
        print("No hay libros")
        return
    for fila in filas:
        estado = "Disponible" if fila[2] == 1 else "Prestado"
        print(f"{fila[0]} - {fila[1]} - {estado}")

        # GESTIÓN DE ACCIONES (PRÉSTAMOS)


def prestar_libro(titulo: str) -> str:
    """Cambia el estado del libro a prestado en la base de datos."""
    global ultimo_error
    libro = buscar_libro(titulo)
    if not libro:
        ultimo_error = "Libro no encontrado"
        return "Libro no encontrado"
    if not libro["disponible"]:
        ultimo_error = "Libro no disponible"
        return "Libro no disponible"
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("UPDATE libros SET disponible = 0 WHERE id = ?", (libro["id"],))
        conexion.commit()
    ultimo_error = ""
    return "Libro prestado"


def devolver_libro(*datos) -> str:
    """Devuelve un libro prestado.

    Puede recibir el titulo del libro, para mantener compatibilidad con
    tests anteriores, o libro_id y usuario_id para la Fase 6.
    """
    global ultimo_error
    if len(datos) == 2:
        libro_id = datos[0]
        usuario_id = datos[1]

        inicializar_tablas()

        with sqlite3.connect(RUTA_BD) as conexion:
            conexion.execute("PRAGMA foreign_keys = ON")
            prestamo = conexion.execute(
                """
                SELECT id
                FROM prestamos
                WHERE libro_id = ?
                  AND usuario_id = ?
                """,
                (libro_id, usuario_id),
            ).fetchone()

            if prestamo is None:
                ultimo_error = "Prestamo no encontrado"
                return "Prestamo no encontrado"

            conexion.execute(
                "UPDATE libros SET disponible = 1 WHERE id = ?",
                (libro_id,),
            )
            conexion.execute(
                "DELETE FROM prestamos WHERE id = ?",
                (prestamo[0],),
            )
            conexion.commit()

        ultimo_error = ""
        return "Libro devuelto"

    if len(datos) != 1:
        raise TypeError("devolver_libro necesita titulo o libro_id y usuario_id")

    titulo = datos[0]
    libro = buscar_libro(titulo)
    if not libro:
        ultimo_error = "Libro no encontrado"
        return "Libro no encontrado"
    if libro["disponible"]:
        ultimo_error = "Libro ya disponible"
        return "Libro ya disponible"
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("UPDATE libros SET disponible = 1 WHERE id = ?", (libro["id"],))
        conexion.commit()
    ultimo_error = ""
    return "Libro devuelto"

    # BÚSQUEDAS AVANZADAS REQUERIDAS (FASE 4)


def buscar_por_autor(autor: str) -> list:
    """Busca libros usando coincidencia parcial por nombre de autor (LIKE)."""
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT id, titulo, autor, disponible FROM libros WHERE autor LIKE ?",
                                  (f"%{autor}%",))
        filas = cursor.fetchall()
    return [{"id": f[0], "titulo": f[1], "autor": f[2], "disponible": bool(f[3])} for f in filas]


def buscar_por_disponibilidad(disponible: bool) -> list:
    """Filtra los libros según su estado de disponibilidad actual."""
    val = 1 if disponible else 0
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT id, titulo, autor, disponible FROM libros WHERE disponible = ?", (val,))
        filas = cursor.fetchall()
    return [{"id": f[0], "titulo": f[1], "autor": f[2], "disponible": bool(f[3])} for f in filas]

    # MÉTODOS CRUD - USUARIOS (PARA FASE 5)


def add_usuario(usuario: Usuario) -> None:
    global ultimo_error
    try:
        with sqlite3.connect(RUTA_BD) as conexion:
            conexion.execute(
                "INSERT INTO usuarios (nombre, apellidos, email, habilitado) VALUES (?, ?, ?, ?)",
                (usuario.nombre, usuario.apellidos, usuario.email, 1 if usuario.habilitado else 0)
            )
            conexion.commit()
        ultimo_error = ""
    except sqlite3.IntegrityError:
        ultimo_error = "El email ya se encuentra registrado"
    except sqlite3.Error as e:
        ultimo_error = f"Error de BD: {str(e)}"


def remove_usuario(id_usuario: int) -> bool:
    global ultimo_error
    try:
        with sqlite3.connect(RUTA_BD) as conexion:
            cursor = conexion.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
            conexion.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        ultimo_error = f"Error de BD: {str(e)}"
        return False


def get_usuario(id_usuario: int) -> dict | None:
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT id, nombre, apellidos, email, habilitado FROM usuarios WHERE id = ?",
                                  (id_usuario,))
        fila = cursor.fetchone()
    if fila:
        return {"id": fila[0], "nombre": fila[1], "apellidos": fila[2], "email": fila[3], "habilitado": bool(fila[4])}
    return None


def list_usuarios() -> list:
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT id, nombre, apellidos, email, habilitado FROM usuarios")
        filas = cursor.fetchall()
    return [{"id": f[0], "nombre": f[1], "apellidos": f[2], "email": f[3], "habilitado": bool(f[4])} for f in filas]


def habilita_usuario(id_usuario: int) -> bool:
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("UPDATE usuarios SET habilitado = 1 WHERE id = ?", (id_usuario,))
        conexion.commit()
    return cursor.rowcount > 0


def deshabilita_usuario(id_usuario: int) -> bool:
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("UPDATE usuarios SET habilitado = 0 WHERE id = ?", (id_usuario,))
        conexion.commit()
    return cursor.rowcount > 0


def buscar_usuario_por_email(email: str) -> dict | None:
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT id, nombre, apellidos, email, habilitado FROM usuarios WHERE email = ?",
                                  (email,))
        fila = cursor.fetchone()
    if fila:
        return {"id": fila[0], "nombre": fila[1], "apellidos": fila[2], "email": fila[3], "habilitado": bool(fila[4])}
    return None

    # ==========================================
    # FASE 8 - INTEGRACIÓN TOTAL
    # ==========================================


def operar(accion: str, datos: dict = None):
    """
    Punto de entrada único para operar el sistema de la biblioteca.
    Dirige la petición a la función correspondiente según la 'accion'.

    :param accion: El nombre de la operación a realizar (ej: 'agregar_libro').
    :param datos: Diccionario con los parámetros necesarios para la operación.
    """
    global ultimo_error
    if datos is None:
        datos = {}

    try:
        # ---- OPERACIONES DE LIBROS ----
        if accion == "agregar_libro":
            return agregar_libro(datos["titulo"], datos["autor"])

        elif accion == "remove_libro":
            return remove_libro(datos["id"])

        elif accion == "buscar_libro":
            return buscar_libro(datos["titulo"])

        elif accion == "mostrar_libros":
            return mostrar_libros()

        elif accion == "buscar_por_autor":
            return buscar_por_autor(datos["autor"])

        elif accion == "buscar_por_disponibilidad":
            return buscar_por_disponibilidad(datos["disponible"])

        # ---- OPERACIONES DE USUARIOS ----
        elif accion == "add_usuario":
            # Instanciamos el objeto Usuario a partir de los datos
            nuevo_usuario = Usuario(
                nombre=datos["nombre"],
                apellidos=datos["apellidos"],
                email=datos["email"],
                habilitado=datos.get("habilitado", True)
            )
            return add_usuario(nuevo_usuario)

        elif accion == "remove_usuario":
            return remove_usuario(datos["id"])

        elif accion == "get_usuario":
            return get_usuario(datos["id"])

        elif accion == "list_usuarios":
            return list_usuarios()

        elif accion == "habilita_usuario":
            return habilita_usuario(datos["id"])

        elif accion == "deshabilita_usuario":
            return deshabilita_usuario(datos["id"])

        # ---- OPERACIONES DE PRÉSTAMOS ----
        elif accion == "prestar_libro":
            # Según tu código actual, prestar_libro recibe un título
            return prestar_libro(datos["titulo"])

        elif accion == "devolver_libro":
            # Tu código soporta devolver por título o por (libro_id, usuario_id)
            if "libro_id" in datos and "usuario_id" in datos:
                return devolver_libro(datos["libro_id"], datos["usuario_id"])
            else:
                return devolver_libro(datos["titulo"])

        # ---- ACCIÓN NO RECONOCIDA ----
        else:
            ultimo_error = f"Acción '{accion}' no reconocida por el sistema."
            return None

    except KeyError as e:
        ultimo_error = f"Error en '{accion}': Falta el dato obligatorio {str(e)}."
        return None
    except Exception as e:
        ultimo_error = f"Error inesperado en '{accion}': {str(e)}"
        return None

def registrar_log(mensaje: str):
    """Inserta una línea de texto en la tabla de logs."""
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("INSERT INTO logs (accion) VALUES (?)", (mensaje,))
        conexion.commit()