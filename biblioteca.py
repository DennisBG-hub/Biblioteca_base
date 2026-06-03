import sqlite3
from pathlib import Path

RUTA_BD = Path(__file__).resolve().parent / "bd" / "biblioteca.db"
RUTA_BD.parent.mkdir(parents=True, exist_ok=True)

def inicializar_tablas():
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.execute("CREATE TABLE IF NOT EXISTS libros (id INTEGER PRIMARY KEY, titulo TEXT, autor TEXT, disponible INTEGER DEFAULT 1)")
        conexion.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nombre TEXT, apellidos TEXT, email TEXT UNIQUE, habilitado INTEGER DEFAULT 1)")
        conexion.execute("CREATE TABLE IF NOT EXISTS prestamos (id_prestamo INTEGER PRIMARY KEY AUTOINCREMENT, id_libro INTEGER, id_usuario INTEGER, fecha_prestamo TEXT, fecha_devolucion TEXT, FOREIGN KEY(id_libro) REFERENCES libros(id), FOREIGN KEY(id_usuario) REFERENCES usuarios(id))")
        conexion.execute("CREATE TABLE IF NOT EXISTS logs (id_log INTEGER PRIMARY KEY AUTOINCREMENT, accion TEXT, fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conexion.commit()

inicializar_tablas()

def prestar_libro(id_libro, id_usuario, fecha):
    with sqlite3.connect(RUTA_BD) as conexion:
        # Obtenemos nombres para el log
        usuario = conexion.execute("SELECT nombre FROM usuarios WHERE id = ?", (id_usuario,)).fetchone()[0]
        libro = conexion.execute("SELECT titulo FROM libros WHERE id = ?", (id_libro,)).fetchone()[0]

        conexion.execute("INSERT INTO prestamos (id_libro, id_usuario, fecha_prestamo) VALUES (?, ?, ?)", (id_libro, id_usuario, fecha))
        conexion.execute("UPDATE libros SET disponible = 0 WHERE id = ?", (id_libro,))

        mensaje = f"Usuario {usuario} ha prestado Libro {libro}"
        conexion.execute("INSERT INTO logs (accion) VALUES (?)", (mensaje,))
        conexion.commit()
    return True

def devolver_libro(id_libro, fecha_devolucion):
    with sqlite3.connect(RUTA_BD) as conexion:
        # Obtenemos nombre para el log
        usuario = conexion.execute("SELECT u.nombre FROM usuarios u JOIN prestamos p ON u.id = p.id_usuario WHERE p.id_libro = ? AND p.fecha_devolucion IS NULL", (id_libro,)).fetchone()[0]
        libro = conexion.execute("SELECT titulo FROM libros WHERE id = ?", (id_libro,)).fetchone()[0]

        conexion.execute("UPDATE prestamos SET fecha_devolucion = ? WHERE id_libro = ? AND fecha_devolucion IS NULL", (fecha_devolucion, id_libro))
        conexion.execute("UPDATE libros SET disponible = 1 WHERE id = ?", (id_libro,))

        mensaje = f"Usuario {usuario} ha devuelto Libro {libro}"
        conexion.execute("INSERT INTO logs (accion) VALUES (?)", (mensaje,))
        conexion.commit()
    return True


def operar(accion, datos):
    if accion == "prestar":
        return prestar_libro(datos['id_libro'], datos['id_usuario'], datos['fecha'])

    elif accion == "devolver":
        # Nota: Aquí pasamos los datos necesarios para la devolución
        return devolver_libro(datos['id_libro'], datos['fecha_devolucion'])

    else:
        raise ValueError(f"Acción '{accion}' no reconocida")