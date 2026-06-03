import unittest
import sqlite3
import biblioteca


class TestUsuarios(unittest.TestCase):
    def setUp(self):
        """Limpia la tabla de usuarios antes de cada test."""
        biblioteca.inicializar_tablas()
        biblioteca.usuarios.clear()

        with sqlite3.connect(biblioteca.RUTA_BD) as conexion:
            conexion.execute("DELETE FROM usuarios")
            conexion.commit()

    def test_add_y_get_usuario_correctamente(self):
        # Corrección: Pasamos los datos en el orden correcto y sin los ':'
        nuevo_usuario = biblioteca.Usuario("Juan", "Pérez", "juan@email.com")
        biblioteca.add_usuario(nuevo_usuario)

        # Lo buscamos por email para verificar que se guardó en la BD
        usuario_bd = biblioteca.buscar_usuario_por_email("juan@email.com")

        self.assertIsNotNone(usuario_bd)
        self.assertEqual(usuario_bd["nombre"], "Juan")
        self.assertEqual(usuario_bd["apellidos"], "Pérez")
        self.assertTrue(usuario_bd["habilitado"])

    def test_deshabilitar_usuario(self):
        # Corrección: Datos limpios para el segundo test
        nuevo_usuario = biblioteca.Usuario("Ana", "Gómez", "ana@email.com")
        biblioteca.add_usuario(nuevo_usuario)

        usuario_bd = biblioteca.buscar_usuario_por_email("ana@email.com")
        id_usuario = usuario_bd["id"]

        # Lo deshabilitamos usando tu método
        resultado = biblioteca.deshabilita_usuario(id_usuario)
        self.assertTrue(resultado)

        # Comprobamos que el estado en la BD ha cambiado a False
        usuario_actualizado = biblioteca.get_usuario(id_usuario)
        self.assertFalse(usuario_actualizado["habilitado"])


if __name__ == "__main__":
    unittest.main()