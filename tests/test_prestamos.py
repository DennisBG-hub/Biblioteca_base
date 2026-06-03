import sqlite3
import unittest

import biblioteca


class TestPrestamos(unittest.TestCase):
    def setUp(self):
        biblioteca.inicializar_tablas()

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            conexion.execute("PRAGMA foreign_keys = ON")
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS prestamos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    libro_id INTEGER NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (libro_id) REFERENCES libros(id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            # (OPCIONAL PARA FASE 7): Crear la tabla de logs si aún no está en biblioteca.py
            # conexion.execute("""
            #     CREATE TABLE IF NOT EXISTS logs (
            #         id INTEGER PRIMARY KEY AUTOINCREMENT,
            #         accion TEXT NOT NULL
            #     )
            # """)

            conexion.execute("DELETE FROM prestamos")
            conexion.execute("DELETE FROM usuarios")
            conexion.execute("DELETE FROM libros")
            # conexion.execute("DELETE FROM logs") # Si implementas logs
            conexion.commit()

    def test_devolver_libro_por_ids_marca_libro_disponible_y_borra_prestamo(self):
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            libro_id = conexion.execute(
                "INSERT INTO libros (titulo, autor, disponible) VALUES (?, ?, 0)",
                ("Nada", "Carmen Laforet"),
            ).lastrowid
            usuario_id = conexion.execute(
                """
                INSERT INTO usuarios (nombre, apellidos, email, habilitado)
                VALUES (?, ?, ?, 1)
                """,
                ("Ana", "Garcia", "ana@email.com"),
            ).lastrowid
            conexion.execute(
                "INSERT INTO prestamos (libro_id, usuario_id) VALUES (?, ?)",
                (libro_id, usuario_id),
            )
            conexion.commit()

        resultado = biblioteca.devolver_libro(libro_id, usuario_id)

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            disponible = conexion.execute(
                "SELECT disponible FROM libros WHERE id = ?",
                (libro_id,),
            ).fetchone()[0]
            total_prestamos = conexion.execute(
                "SELECT COUNT(*) FROM prestamos"
            ).fetchone()[0]

        self.assertEqual(resultado, "Libro devuelto")
        self.assertEqual(disponible, 1)
        self.assertEqual(total_prestamos, 0)

    def test_devolver_libro_por_ids_devuelve_error_si_no_hay_prestamo(self):
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            libro_id = conexion.execute(
                "INSERT INTO libros (titulo, autor, disponible) VALUES (?, ?, 0)",
                ("Nada", "Carmen Laforet"),
            ).lastrowid
            usuario_id = conexion.execute(
                """
                INSERT INTO usuarios (nombre, apellidos, email, habilitado)
                VALUES (?, ?, ?, 1)
                """,
                ("Ana", "Garcia", "ana@email.com"),
            ).lastrowid
            conexion.commit()

        resultado = biblioteca.devolver_libro(libro_id, usuario_id)

        self.assertEqual(resultado, "Prestamo no encontrado")
        self.assertEqual(biblioteca.ultimo_error, "Prestamo no encontrado")

    def test_devolver_libro_con_exito(self):
        """Verifica que un libro prestado vuelve a estar disponible tras devolverlo."""
        # 1. Setup: Forzamos la creación del libro, el usuario y el préstamo en la BD
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            libro_id = conexion.execute(
                "INSERT INTO libros (titulo, autor, disponible) VALUES (?, ?, 0)",
                ("Cien años de soledad", "Gabriel García Márquez"),
            ).lastrowid

            usuario_id = conexion.execute(
                "INSERT INTO usuarios (nombre, apellidos, email, habilitado) VALUES (?, ?, ?, 1)",
                ("Juan", "Perez", "juan@test.com"),
            ).lastrowid

            conexion.execute(
                "INSERT INTO prestamos (libro_id, usuario_id) VALUES (?, ?)",
                (libro_id, usuario_id),
            )
            conexion.commit()

        # 2. Ejecución: Llamamos a la función
        resultado = biblioteca.devolver_libro(libro_id, usuario_id)
        self.assertEqual(resultado, "Libro devuelto")

        # 3. Aserciones: Comprobamos el resultado y (futuro) el log
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            # Comprobar que vuelve a estar disponible
            cursor = conexion.execute("SELECT disponible FROM libros WHERE id = ?", (libro_id,))
            self.assertEqual(cursor.fetchone()[0], 1)

            # ---------------------------------------------------------
            # CÓMO PROBAR LA FASE 7 CUANDO LA IMPLEMENTES:
            # Una vez modifiques biblioteca.py para que guarde logs,
            # descomenta estas líneas para comprobar que el test pasa.
            # ---------------------------------------------------------
            # cursor_log = conexion.execute("SELECT accion FROM logs")
            # logs_guardados = [fila[0] for fila in cursor_log.fetchall()]
            # self.assertTrue(
            #     any("ha devuelto" in log for log in logs_guardados),
            #     "No se encontró el registro de la devolución en los logs"
            # )


if __name__ == "__main__":
    unittest.main()