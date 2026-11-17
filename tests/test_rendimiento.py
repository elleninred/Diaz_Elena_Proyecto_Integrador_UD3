"""Diagnóstico de consultas: evidencia del problema N+1 y de su corrección.

Cada prueba cuenta las consultas SELECT realmente enviadas a PostgreSQL con el
evento ``before_cursor_execute`` y compara la carga perezosa (sin optimizar)
con los repositorios (con ``joinedload`` / ``selectinload``).

Ejecutar con ``pytest -q -s tests/test_rendimiento.py`` para ver las cifras.
"""
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import event, select

from app.modelos.autor import Autor
from app.modelos.ejemplar import Ejemplar
from app.modelos.libro import Libro
from app.modelos.prestamo import Prestamo
from app.modelos.socio import Socio
from app.repositorios.autores import AutorRepositorio
from app.repositorios.libros import LibroRepositorio
from app.repositorios.prestamos import PrestamoRepositorio
from app.dto.libros import FiltroLibros

N = 5  # número de autores / préstamos de cada escenario


@contextmanager
def contar_consultas(engine):
    """Cuenta las consultas SELECT ejecutadas dentro del bloque."""
    sentencias: list[str] = []

    def _registrar(conn, cursor, statement, parameters, context, executemany):
        # Se ignoran SAVEPOINT/RELEASE del fixture de aislamiento: solo cuentan los SELECT.
        if statement.lstrip().upper().startswith("SELECT"):
            sentencias.append(statement)

    event.listen(engine, "before_cursor_execute", _registrar)
    try:
        yield sentencias
    finally:
        event.remove(engine, "before_cursor_execute", _registrar)


def _informar(titulo: str, antes: int, despues: int) -> None:
    print(f"\n[N+1] {titulo}: antes = {antes} consultas | después = {despues} consultas")


@pytest.fixture
def datos_n_mas_1(sesion_test):
    """N autores con 2 libros cada uno y N préstamos con 2 ejemplares cada uno."""
    with sesion_test() as sesion:
        socios = []
        for i in range(N):
            autor = Autor(nombre=f"Autor{i}", apellidos=f"Apellido{i}")
            sesion.add(autor)
            sesion.flush()
            libros = [
                Libro(
                    isbn=f"N1-{i}-{j}",
                    titulo=f"Libro {i}-{j}",
                    precio=Decimal("10.00"),
                    id_autor=autor.id_autor,
                    activo=True,
                )
                for j in range(2)
            ]
            sesion.add_all(libros)
            sesion.flush()

            socio = Socio(
                dni=f"N1DNI{i}",
                nombre=f"Socio{i}",
                apellidos="Prueba",
                email=f"socio{i}@example.com",
                telefono="600000000",
                fecha_alta=datetime.now(),
                activo=True,
            )
            sesion.add(socio)
            sesion.flush()
            socios.append(socio)

            ejemplares = [
                Ejemplar(
                    id_libro=libro.id_libro,
                    codigo_inventario=900000 + i * 10 + k,
                    ubicacion="Sala",
                    estado="PRESTADO",
                    fecha_alta=datetime.now(),
                )
                for k, libro in enumerate(libros)
            ]
            sesion.add_all(ejemplares)
            sesion.flush()

            prestamo = Prestamo(
                id_socio=socio.id_socio,
                fecha_prestamo=date.today(),
                fecha_limite=date.today(),
            )
            prestamo.ejemplares.extend(ejemplares)
            sesion.add(prestamo)
        sesion.commit()


def test_n_mas_1_autores_con_libros(sesion_test, engine_test, datos_n_mas_1):
    # ANTES: carga perezosa -> 1 consulta de autores + 1 por cada autor.
    with sesion_test() as sesion, contar_consultas(engine_test) as consultas:
        for autor in sesion.scalars(select(Autor)).all():
            _ = [libro.titulo for libro in autor.libros]
        antes = len(consultas)

    # DESPUÉS: selectinload -> 1 consulta de autores + 1 agrupada de libros.
    with sesion_test() as sesion, contar_consultas(engine_test) as consultas:
        for autor in AutorRepositorio(sesion).listar_con_libros():
            _ = [libro.titulo for libro in autor.libros]
        despues = len(consultas)

    _informar("Autores con sus libros", antes, despues)
    assert antes == 1 + N
    assert despues == 2


def test_n_mas_1_libros_con_autor(sesion_test, engine_test, datos_n_mas_1):
    filtro = FiltroLibros(tamano=100)

    # ANTES: 1 consulta de libros + 1 por cada autor distinto.
    with sesion_test() as sesion, contar_consultas(engine_test) as consultas:
        for libro in sesion.scalars(select(Libro).order_by(Libro.id_libro)).all():
            _ = libro.autor.nombre
        antes = len(consultas)

    # DESPUÉS: joinedload -> una única consulta con JOIN.
    with sesion_test() as sesion, contar_consultas(engine_test) as consultas:
        for libro in LibroRepositorio(sesion).buscar_con_filtros(filtro):
            _ = libro.autor.nombre
        despues = len(consultas)

    _informar("Libros con su autor", antes, despues)
    assert antes == 1 + N
    assert despues == 1


def test_n_mas_1_prestamos_con_socio_y_ejemplares(sesion_test, engine_test, datos_n_mas_1):
    # ANTES: 1 consulta de préstamos + 1 por socio + 1 por colección de ejemplares.
    with sesion_test() as sesion, contar_consultas(engine_test) as consultas:
        abiertos = sesion.scalars(
            select(Prestamo).where(Prestamo.fecha_devolucion.is_(None))
        ).all()
        for prestamo in abiertos:
            _ = prestamo.socio.nombre
            _ = [e.id_ejemplar for e in prestamo.ejemplares]
        antes = len(consultas)

    # DESPUÉS: joinedload(socio) + selectinload(ejemplares) -> 2 consultas.
    with sesion_test() as sesion, contar_consultas(engine_test) as consultas:
        for prestamo in PrestamoRepositorio(sesion).listar_abiertos():
            _ = prestamo.socio.nombre
            _ = [e.id_ejemplar for e in prestamo.ejemplares]
        despues = len(consultas)

    _informar("Préstamos con socio y ejemplares", antes, despues)
    assert antes == 1 + 2 * N
    assert despues == 2
