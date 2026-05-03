# Guia para alumnos: fork, clone y trabajo con GitHub

Esta guia explica como crear una copia propia del proyecto del profesor y
trabajar sin modificar el repositorio original.

## 1. Conceptos importantes

El repositorio del profesor es el proyecto base.

Cada alumno debe crear su propia copia usando un `fork`.

Despues, cada alumno trabajara en su repositorio personal y subira ahi sus
commits, ramas, tests y cambios.

## 2. Crear un fork del repositorio del profesor

1. Entrar en GitHub.
2. Abrir el repositorio del profesor.
3. Pulsar el boton `Fork`.
4. Elegir la cuenta personal del alumno.
5. Crear el fork.

Al terminar, el alumno tendra un repositorio propio con una URL parecida a:

```text
https://github.com/USUARIO_ALUMNO/Biblioteca_base
```

Este repositorio pertenece al alumno. El profesor no se modifica cuando el
alumno trabaja en su fork.

## 3. Clonar el fork en el ordenador

El alumno debe clonar su propio fork, no el repositorio del profesor.

Ejemplo:

```bash
git clone https://github.com/USUARIO_ALUMNO/Biblioteca_base.git
cd Biblioteca_base
```

En PyCharm tambien se puede hacer desde:

```text
File > New > Project from Version Control
```

Despues se pega la URL del fork del alumno.

## 4. Configurar el repositorio original como upstream

Una vez clonado el fork, hay que guardar la URL del repositorio del profesor
como `upstream`.

Dentro de la carpeta del proyecto:

```bash
git remote add upstream https://github.com/USUARIO_PROFESOR/Biblioteca_base.git
```

Para comprobar que esta bien configurado:

```bash
git remote -v
```

Debe aparecer algo parecido a:

```text
origin    https://github.com/USUARIO_ALUMNO/Biblioteca_base.git
upstream  https://github.com/USUARIO_PROFESOR/Biblioteca_base.git
```

Significado:

- `origin`: repositorio del alumno.
- `upstream`: repositorio original del profesor.

## 5. Crear una rama antes de trabajar

No se debe trabajar directamente en `main`.

Para cada fase o tarea se crea una rama:

```bash
git checkout -b feature/setup
```

Otros ejemplos:

```bash
git checkout -b feature/testing
git checkout -b feature/refactor
git checkout -b feature/libros
git checkout -b feature/usuarios
```

## 6. Hacer commits frecuentes

Despues de cada cambio pequeno:

```bash
git status
git add .
git commit -m "mensaje claro y concreto"
```

Ejemplos de mensajes:

```bash
git commit -m "F1: analisis inicial del codigo"
git commit -m "F2: tests para prestamo de libros"
git commit -m "Refactor: renombra variables confusas"
```

## 7. Subir cambios al fork del alumno

La primera vez que se sube una rama:

```bash
git push -u origin feature/setup
```

Las siguientes veces:

```bash
git push
```

Los cambios se suben al repositorio del alumno, no al del profesor.

## 8. Recibir cambios nuevos del profesor

Si el profesor modifica el proyecto base, el alumno puede traer esos cambios
desde `upstream`.

Primero hay que ir a `main`:

```bash
git checkout main
```

Despues traer los cambios del profesor:

```bash
git pull upstream main
```

Y subir el `main` actualizado al fork del alumno:

```bash
git push origin main
```

## 9. Llevar los cambios nuevos a una rama de trabajo

Si el alumno esta trabajando en una rama, debe actualizarla con los cambios de
`main`.

Ejemplo:

```bash
git checkout feature/testing
git merge main
```

Si aparecen conflictos, hay que resolverlos, ejecutar tests y hacer commit.

```bash
git status
git add .
git commit -m "Resuelve conflictos con cambios del profesor"
```

## 10. Ejecutar tests antes de subir

Antes de hacer `push`, se deben ejecutar los tests.

En Windows, desde la raiz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Si Python esta configurado globalmente:

```bash
python -m unittest discover -s tests
```

## 11. Entregar el trabajo al profesor

Cada alumno debe enviar al profesor la URL de su fork.

Ejemplo:

```text
https://github.com/USUARIO_ALUMNO/Biblioteca_base
```

Si el repositorio es privado, el alumno debe anadir al profesor como
colaborador:

```text
Settings > Collaborators > Add people
```

## 12. Resumen del flujo habitual

```bash
git checkout main
git pull upstream main
git push origin main

git checkout -b feature/nueva-tarea

# trabajar

git status
git add .
git commit -m "mensaje claro"
git push -u origin feature/nueva-tarea
```

## 13. Errores comunes

- Clonar el repositorio del profesor en lugar del fork del alumno.
- Trabajar directamente en `main`.
- Hacer un unico commit al final.
- No ejecutar tests antes de subir.
- No hacer `pull upstream main` cuando el profesor publica cambios.
- Resolver conflictos sin comprobar que los tests siguen pasando.

## 14. Regla principal

Cada alumno trabaja en su fork.

El repositorio del profesor se usa como referencia y fuente de actualizaciones,
pero no se modifica directamente.
