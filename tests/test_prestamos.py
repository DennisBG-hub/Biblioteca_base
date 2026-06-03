import unittest
import sqlite3
import biblioteca

class TestPrestamos(unittest.TestCase):
    def setUp(self):
        """Prepara la base de datos e inserta datos limpios antes de cada test."""
        biblioteca.inicializar_tablas()
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            # Limpiamos las tablas para que no se acumulen datos viejos
            conexion.execute("DELETE FROM prestamos")
            conexion.execute("DELETE FROM libros")
            conexion.execute("DELETE FROM usuarios")

            # Insertamos los datos necesarios para tu prueba (ID 1)
            conexion.execute("INSERT INTO libros (id, titulo, autor, disponible) VALUES (1, 'Libro de Prueba', 'Autor', 1)")
            conexion.execute("INSERT INTO usuarios (id, nombre, apellidos, email) VALUES (1, 'Juan', 'Pérez', 'juan@email.com')")
            conexion.commit()

    def test_prestar_libro_con_exito(self):
        """Verifica que un libro disponible pasa a estar prestado."""
        resultado = biblioteca.prestar_libro(1, 1, "2026-06-03")
        self.assertTrue(resultado)

        # Comprobar en la base de datos que ya no está disponible
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            cursor = conexion.execute("SELECT disponible FROM libros WHERE id = 1")
            self.assertEqual(cursor.fetchone()[0], 0)

if __name__ == '__main__':
    unittest.main()