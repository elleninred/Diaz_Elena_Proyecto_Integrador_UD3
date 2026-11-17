from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.configuracion import obtener_url_bd_test
from app.modelos import Base
from app.modelos.autor import Autor
from app.modelos.ejemplar import Ejemplar
from app.modelos.libro import Libro
from app.modelos.socio import Socio
from app.unidad_trabajo import UnidadTrabajoSQLAlchemy


@pytest.fixture(scope="session")
def engine_test():
    engine = create_engine(obtener_url_bd_test())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def sesion_test(engine_test):
    """Envuelve cada prueba de integración en una transacción que hace rollback al final."""
    connection = engine_test.connect()
    transaction = connection.begin()
    SessionTest = sessionmaker(bind=connection, autoflush=True, expire_on_commit=False)
    session = SessionTest()

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield SessionTest

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def uow_integracion(sesion_test):
    return UnidadTrabajoSQLAlchemy(sesion_test)


@pytest.fixture
def datos_base_integracion(uow_integracion):
    with uow_integracion as uow:
        autor = Autor(nombre="Isabel", apellidos="Allende")
        uow.autores.añadir(autor)
        uow.flush()

        libro = Libro(
            isbn="978-8401352836",
            titulo="La casa de los espíritus",
            precio=Decimal("19.95"),
            id_autor=autor.id_autor,
            activo=True,
        )
        uow.libros.añadir(libro)
        uow.flush()

        ejemplar = Ejemplar(
            id_libro=libro.id_libro,
            codigo_inventario=1001,
            ubicacion="Pasillo A",
            estado="DISPONIBLE",
            fecha_alta=datetime.now(),
        )
        uow.ejemplares.añadir(ejemplar)

        socio = Socio(
            dni="12345678A",
            nombre="Elena",
            apellidos="Díaz",
            email="elena@example.com",
            telefono="600111222",
            fecha_alta=datetime.now(),
            activo=True,
        )
        uow.socios.añadir(socio)
        uow.flush()

        ids = {
            "id_autor": autor.id_autor,
            "id_libro": libro.id_libro,
            "id_ejemplar": ejemplar.id_ejemplar,
            "id_socio": socio.id_socio,
        }
        uow.commit()
    return ids
