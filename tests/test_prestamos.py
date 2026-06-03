import unittest
import sqlite3
import biblioteca

class TestPrestamos(unittest.TestCase):
    def setUp(self):
        """Prepara la base de datos e inserta datos limpios antes de cada test."""
        biblioteca.inicializar_tablas()
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            conexion.execute("DELETE FROM logs")
            conexion.execute("DELETE FROM prestamos")
            conexion.execute("DELETE FROM libros")
            conexion.execute("DELETE FROM usuarios")
            conexion.execute("INSERT INTO libros (id, titulo, autor, disponible) VALUES (1, 'Libro de Prueba', 'Autor', 1)")
            conexion.execute("INSERT INTO usuarios (id, nombre, apellidos, email) VALUES (1, 'Juan', 'Pérez', 'juan@email.com')")
            conexion.commit()

    # TESTS FASE 8: INTEGRACIÓN TOTAL (operar)

    def test_prestar_libro_con_exito(self):
        datos = {'id_libro': 1, 'id_usuario': 1, 'fecha': "2026-06-03"}
        resultado = biblioteca.operar("prestar", datos)
        self.assertTrue(resultado)

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT disponible FROM libros WHERE id = 1")
            self.assertEqual(cursor.fetchone()[0], 0)

    def test_devolver_libro_con_exito(self):
        biblioteca.operar("prestar", {'id_libro': 1, 'id_usuario': 1, 'fecha': "2026-06-03"})
        resultado = biblioteca.operar("devolver", {'id_libro': 1, 'fecha_devolucion': "2026-06-10"})
        self.assertTrue(resultado)

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT disponible FROM libros WHERE id = 1")
            self.assertEqual(cursor.fetchone()[0], 1)

    def test_log_registro_al_prestar(self):
        biblioteca.operar("prestar", {'id_libro': 1, 'id_usuario': 1, 'fecha': "2026-06-03"})

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT accion FROM logs ORDER BY id_log DESC LIMIT 1")
            log_guardado = cursor.fetchone()
            self.assertIsNotNone(log_guardado)
            self.assertEqual(log_guardado[0], "Usuario Juan ha prestado Libro Libro de Prueba")

    def test_log_registro_al_devolver(self):
        biblioteca.operar("prestar", {'id_libro': 1, 'id_usuario': 1, 'fecha': "2026-06-03"})
        biblioteca.operar("devolver", {'id_libro': 1, 'fecha_devolucion': "2026-06-10"})

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT accion FROM logs ORDER BY id_log DESC LIMIT 1")
            log_guardado = cursor.fetchone()
            self.assertIsNotNone(log_guardado)
            self.assertEqual(log_guardado[0], "Usuario Juan ha devuelto Libro Libro de Prueba")

if __name__ == '__main__':
    unittest.main()