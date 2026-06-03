import unittest
import sqlite3
import biblioteca

class TestPrestamos(unittest.TestCase):
    def setUp(self):
        """Prepara la base de datos e inserta datos limpios antes de cada test."""
        biblioteca.inicializar_tablas()
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            # Limpiamos todas las tablas implicadas para evitar residuos de ejecuciones anteriores
            conexion.execute("DELETE FROM logs")
            conexion.execute("DELETE FROM prestamos")
            conexion.execute("DELETE FROM libros")
            conexion.execute("DELETE FROM usuarios")

            # Insertamos datos estáticos de prueba con IDs fijos (= 1) para los asserts
            conexion.execute("INSERT INTO libros (id, titulo, autor, disponible) VALUES (1, 'Libro de Prueba', 'Autor', 1)")
            conexion.execute("INSERT INTO usuarios (id, nombre, apellidos, email) VALUES (1, 'Juan', 'Pérez', 'juan@email.com')")
            conexion.commit()


    # TESTS FASE 6: PRÉSTAMOS Y DEVOLUCIONES


    def test_prestar_libro_con_exito(self):
        """Verifica que un libro disponible cambia correctamente su estado a prestado."""
        resultado = biblioteca.prestar_libro(1, 1, "2026-06-03")
        self.assertTrue(resultado)

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT disponible FROM libros WHERE id = 1")
            self.assertEqual(cursor.fetchone()[0], 0)

    def test_devolver_libro_con_exito(self):
        """Verifica que un libro prestado vuelve a estar disponible al devolverse."""
        # Escenario previo obligatorio: el libro debe estar prestado primero
        biblioteca.prestar_libro(1, 1, "2026-06-03")

        resultado = biblioteca.devolver_libro(1, "2026-06-10")
        self.assertTrue(resultado)

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT disponible FROM libros WHERE id = 1")
            self.assertEqual(cursor.fetchone()[0], 1)


    # TESTS FASE 7: REGISTRO DE LOGS (NUEVOS)


    def test_log_registro_al_prestar(self):
        """TU TEST: Verifica que al realizar un préstamo se guarda el log exacto en la BD."""
        biblioteca.prestar_libro(1, 1, "2026-06-03")

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT accion FROM logs ORDER BY id_log DESC LIMIT 1")
            log_guardado = cursor.fetchone()
            self.assertIsNotNone(log_guardado, "No se ha insertado ningún log en la base de datos")
            self.assertEqual(log_guardado[0], "Usuario Juan ha prestado Libro Libro de Prueba")

    def test_log_registro_al_devolver(self):
        """TEST DE DENNIS: Verifica que al procesar una devolución se guarda el log de cierre."""
        biblioteca.prestar_libro(1, 1, "2026-06-03")
        biblioteca.devolver_libro(1, "2026-06-10")

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT accion FROM logs ORDER BY id_log DESC LIMIT 1")
            log_guardado = cursor.fetchone()
            self.assertIsNotNone(log_guardado, "No se ha insertado el log de la devolución")
            self.assertEqual(log_guardado[0], "Usuario Juan ha devuelto Libro Libro de Prueba")

if __name__ == '__main__':
    unittest.main()