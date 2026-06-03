import unittest
import sqlite3
import biblioteca


class TestBiblioteca(unittest.TestCase):
    def setUp(self):
        """Limpia la tabla de libros de la base de datos antes de cada test."""
        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            conexion.execute("DELETE FROM libros")
            conexion.commit()

    def test_agregar_libro_guarda_titulo_autor_y_estado_disponible(self):

        # 1. Añadimos el libro
        biblioteca.agregar_libro("El Quijote", "Miguel de Cervantes")



        # 2. Consultamos la base de datos para ver si se guardó correctamente
        libro_guardado = biblioteca.buscar_libro("El Quijote")

        # 3. Comprobaciones reales sobre la base de datos persistente
        self.assertIsNotNone(libro_guardado)
        self.assertEqual(libro_guardado["titulo"], "El Quijote")
        self.assertEqual(libro_guardado["autor"], "Miguel de Cervantes")
        self.assertTrue(libro_guardado["disponible"])

    def test_prestar_libro_cambia_estado_si_existe_y_esta_disponible(self):
        biblioteca.agregar_libro("Nada", "Carmen Laforet")

        resultado = biblioteca.prestar_libro("Nada")

        self.assertEqual(resultado, "Libro prestado")

        # Consultamos la base de datos para verificar que cambió el estado a False (prestado)
        libro_guardado = biblioteca.buscar_libro("Nada")
        self.assertFalse(libro_guardado["disponible"])

    def test_devolver_libro_cambia_estado_si_estaba_prestado(self):
        biblioteca.agregar_libro("La colmena", "Camilo Jose Cela")
        biblioteca.prestar_libro("La colmena")

        resultado = biblioteca.devolver_libro("La colmena")

        self.assertEqual(resultado, "Libro devuelto")

        # Consultamos la base de datos para verificar que volvió a estar disponible (True)
        libro_guardado = biblioteca.buscar_libro("La colmena")
        self.assertTrue(libro_guardado["disponible"])


if __name__ == "__main__":
    unittest.main()