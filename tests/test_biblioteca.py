import unittest

import biblioteca


class TestBiblioteca(unittest.TestCase):
    def setUp(self):
        biblioteca.libros.clear()
        biblioteca.ultimo_error = ""

    def test_agregar_libro_guarda_titulo_autor_y_estado_disponible(self):
        biblioteca.agregar_libro("El Quijote", "Miguel de Cervantes")

        self.assertEqual(len(biblioteca.libros), 1)
        self.assertEqual(biblioteca.libros[0]["titulo"], "El Quijote")
        self.assertEqual(biblioteca.libros[0]["autor"], "Miguel de Cervantes")
        self.assertTrue(biblioteca.libros[0]["disponible"])

    def test_buscar_libro_devuelve_el_libro_si_existe(self):
        biblioteca.agregar_libro("Nada", "Carmen Laforet")

        libro = biblioteca.buscar_libro("Nada")

        self.assertIsNotNone(libro)
        self.assertEqual(libro["titulo"], "Nada")
        self.assertEqual(libro["autor"], "Carmen Laforet")

    def test_buscar_libro_devuelve_none_si_no_existe(self):
        biblioteca.agregar_libro("La colmena", "Camilo Jose Cela")

        libro = biblioteca.buscar_libro("Libro inexistente")

        self.assertIsNone(libro)

    def test_prestar_libro_cambia_estado_si_existe_y_esta_disponible(self):
        biblioteca.agregar_libro("Nada", "Carmen Laforet")

        resultado = biblioteca.prestar_libro("Nada")

        self.assertEqual(resultado, "Libro prestado")
        self.assertFalse(biblioteca.libros[0]["disponible"])

    def test_prestar_libro_devuelve_error_si_no_existe(self):
        resultado = biblioteca.prestar_libro("Libro inexistente")

        self.assertEqual(resultado, "Libro no encontrado")
        self.assertEqual(biblioteca.ultimo_error, "Libro no encontrado")

    def test_prestar_libro_devuelve_error_si_ya_esta_prestado(self):
        biblioteca.agregar_libro("El camino", "Miguel Delibes")
        biblioteca.prestar_libro("El camino")

        resultado = biblioteca.prestar_libro("El camino")

        self.assertEqual(resultado, "Libro no disponible")
        self.assertEqual(biblioteca.ultimo_error, "Libro no disponible")

    def test_devolver_libro_cambia_estado_si_estaba_prestado(self):
        biblioteca.agregar_libro("La colmena", "Camilo Jose Cela")
        biblioteca.prestar_libro("La colmena")

        resultado = biblioteca.devolver_libro("La colmena")

        self.assertEqual(resultado, "Libro devuelto")
        self.assertTrue(biblioteca.libros[0]["disponible"])

    def test_devolver_libro_devuelve_error_si_no_existe(self):
        resultado = biblioteca.devolver_libro("Libro inexistente")

        self.assertEqual(resultado, "Libro no encontrado")
        self.assertEqual(biblioteca.ultimo_error, "Libro no encontrado")

    def test_devolver_libro_devuelve_error_si_ya_estaba_disponible(self):
        biblioteca.agregar_libro("Marina", "Carlos Ruiz Zafon")

        resultado = biblioteca.devolver_libro("Marina")

        self.assertEqual(resultado, "Libro ya disponible")
        self.assertEqual(biblioteca.ultimo_error, "Libro ya disponible")

    def test_agregar_libro_con_titulo_vacio_no_debe_guardar_libro(self):
        with self.assertRaises(ValueError):
            biblioteca.agregar_libro("", "Autor valido")

        self.assertEqual(len(biblioteca.libros), 0)

    def test_agregar_libro_con_autor_vacio_no_debe_guardar_libro(self):
        with self.assertRaises(ValueError):
            biblioteca.agregar_libro("Titulo valido", "")

        self.assertEqual(len(biblioteca.libros), 0)


if __name__ == "__main__":
    unittest.main()
