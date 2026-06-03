import sqlite3
from pathlib import Path


                #CONFIGURACIÓN INICIAL Y RUTAS"""
RUTA_BD = Path(__file__).resolve().parent / "bd" / "biblioteca.db"
RUTA_BD.parent.mkdir(parents=True, exist_ok=True)

# Variables globales para mantener compatibilidad absoluta con tests antiguos
libros = []
bd = libros
usuarios = []
modo = "normal"
ultimo_error = ""


                #ENTIDADES / CLASES

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


                #INICIALIZACIÓN DE TABLAS SQLITE



def inicializar_tablas():
    """Crea las tablas necesarias si no existen en la base de datos."""
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON")

        # Tabla de Libros (Fase 4)
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                disponible INTEGER DEFAULT 1
            )
        """)

        # Tabla de Usuarios (Fase 5) - ¡ASEGÚRATE DE QUE ESTO ESTÉ AQUÍ!
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                habilitado INTEGER DEFAULT 1
            )
        """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS prestamos (
                id_prestamo INTEGER PRIMARY KEY AUTOINCREMENT,
                id_libro INTEGER NOT NULL,
                id_usuario INTEGER NOT NULL,
                fecha_prestamo TEXT NOT NULL,
                fecha_devolucion TEXT,
                FOREIGN KEY (id_libro) REFERENCES libros (id),
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
            )
        """)

        conexion.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                        accion TEXT NOT NULL,
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

        conexion.commit()


# Forzar la creación de las tablas al importar el módulo
inicializar_tablas()


                #MÉTODOS CRUD - LIBROS


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

                #GESTIÓN DE ACCIONES (PRÉSTAMOS)

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

def devolver_libro(titulo: str) -> str:
    """Cambia el estado del libro a disponible en la base de datos."""
    global ultimo_error
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

            #BÚSQUEDAS AVANZADAS REQUERIDAS (FASE 4)


def buscar_por_autor(autor: str) -> list:
    """Busca libros usando coincidencia parcial por nombre de autor (LIKE)."""
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT id, titulo, autor, disponible FROM libros WHERE autor LIKE ?", (f"%{autor}%",))
        filas = cursor.fetchall()
    return [{"id": f[0], "titulo": f[1], "autor": f[2], "disponible": bool(f[3])} for f in filas]

def buscar_por_disponibilidad(disponible: bool) -> list:
    """Filtra los libros según su estado de disponibilidad actual."""
    val = 1 if disponible else 0
    with sqlite3.connect(RUTA_BD) as conexion:
        cursor = conexion.execute("SELECT id, titulo, autor, disponible FROM libros WHERE disponible = ?", (val,))
        filas = cursor.fetchall()
    return [{"id": f[0], "titulo": f[1], "autor": f[2], "disponible": bool(f[3])} for f in filas]



        #MÉTODOS CRUD - USUARIOS (PARA FASE 5)


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
        cursor = conexion.execute("SELECT id, nombre, apellidos, email, habilitado FROM usuarios WHERE id = ?", (id_usuario,))
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
        cursor = conexion.execute("SELECT id, nombre, apellidos, email, habilitado FROM usuarios WHERE email = ?", (email,))
        fila = cursor.fetchone()
    if fila:
        return {"id": fila[0], "nombre": fila[1], "apellidos": fila[2], "email": fila[3], "habilitado": bool(fila[4])}
    return None



def prestar_libro(id_libro: int, id_usuario: int, fecha: str):
    with sqlite3.connect(RUTA_BD) as conexion:
        # ... (Tu código anterior que comprueba disponibilidad) ...

        # 1. Sacar el nombre del usuario y título del libro para el log
        cursor_u = conexion.execute("SELECT nombre FROM usuarios WHERE id = ?", (id_usuario,))
        nombre_usuario = cursor_u.fetchone()[0]

        cursor_l = conexion.execute("SELECT titulo FROM libros WHERE id = ?", (id_libro,))
        titulo_libro = cursor_l.fetchone()[0]

        # 2. Registrar el préstamo (Tu código de antes)
        conexion.execute("""
            INSERT INTO prestamos (id_libro, id_usuario, fecha_prestamo)
            VALUES (?, ?, ?)
        """, (id_libro, id_usuario, fecha))

        conexion.execute("UPDATE libros SET disponible = 0 WHERE id = ?", (id_libro,))

        # 3. GUARDAR EL LOG (Requisito Fase 7)
        mensaje_log = f"Usuario {nombre_usuario} ha prestado Libro {titulo_libro}"
        conexion.execute("INSERT INTO logs (accion) VALUES (?)", (mensaje_log,))

        conexion.commit()
        return True

def registrar_log(mensaje: str):
    """Inserta una línea de texto en la tabla de logs."""
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("INSERT INTO logs (accion) VALUES (?)", (mensaje,))
        conexion.commit()