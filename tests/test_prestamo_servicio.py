from datetime import datetime
import pytest

from app.dto.prestamos import DatosPrestamo
from app.excepciones import (
    EjemplarNoDisponible,
    PrestamoYaDevuelto,
    SocioInactivo,
)
from app.modelos.ejemplar import Ejemplar
from app.modelos.socio import Socio
from app.servicios.prestamos import PrestamoServicio


class RepoSociosFalso:
    def __init__(self, socios):
        self.socios = socios

    def buscar(self, id_socio: int):
        return self.socios.get(id_socio)


class RepoEjemplaresFalso:
    def __init__(self, ejemplares):
        self.ejemplares = ejemplares

    def buscar(self, id_ejemplar: int):
        return self.ejemplares.get(id_ejemplar)


class RepoPrestamosFalso:
    def __init__(self, prestamos=None):
        self.prestamos = prestamos or {}
        self._seq = 1

    def buscar(self, id_prestamo: int):
        return self.prestamos.get(id_prestamo)

    def añadir(self, prestamo):
        prestamo.id_prestamo = self._seq
        self.prestamos[self._seq] = prestamo
        self._seq += 1


class UowPrestamosFalsa:
    def __init__(self, socios=None, ejemplares=None, prestamos=None):
        self.socios = RepoSociosFalso(socios or {})
        self.ejemplares = RepoEjemplaresFalso(ejemplares or {})
        self.prestamos = RepoPrestamosFalso(prestamos or {})
        self.confirmed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def flush(self):
        pass

    def commit(self):
        self.confirmed = True

    def rollback(self):
        pass


def test_rechaza_socio_inactivo():
    socio = Socio(
        id_socio=1, dni="111A", nombre="Ana", apellidos="Pérez",
        email="a@a.com", telefono="600", fecha_alta=datetime.now(), activo=False
    )
    uow = UowPrestamosFalsa(socios={1: socio})
    srv = PrestamoServicio(uow)

    with pytest.raises(SocioInactivo):
        srv.registrar_prestamo(DatosPrestamo(id_socio=1, ids_ejemplares=[1]))
    assert not uow.confirmed


def test_rechaza_ejemplar_no_disponible():
    socio = Socio(
        id_socio=1, dni="111A", nombre="Ana", apellidos="Pérez",
        email="a@a.com", telefono="600", fecha_alta=datetime.now(), activo=True
    )
    ejemplar = Ejemplar(
        id_ejemplar=1, id_libro=1, codigo_inventario=10,
        ubicacion="Sala", estado="PRESTADO", fecha_alta=datetime.now()
    )
    uow = UowPrestamosFalsa(socios={1: socio}, ejemplares={1: ejemplar})
    srv = PrestamoServicio(uow)

    with pytest.raises(EjemplarNoDisponible):
        srv.registrar_prestamo(DatosPrestamo(id_socio=1, ids_ejemplares=[1]))
    assert not uow.confirmed


def test_registra_y_devuelve_prestamo_correctamente():
    socio = Socio(
        id_socio=1, dni="111A", nombre="Ana", apellidos="Pérez",
        email="a@a.com", telefono="600", fecha_alta=datetime.now(), activo=True
    )
    ejemplar = Ejemplar(
        id_ejemplar=1, id_libro=1, codigo_inventario=10,
        ubicacion="Sala", estado="DISPONIBLE", fecha_alta=datetime.now()
    )
    uow = UowPrestamosFalsa(socios={1: socio}, ejemplares={1: ejemplar})
    srv = PrestamoServicio(uow)

    id_p = srv.registrar_prestamo(DatosPrestamo(id_socio=1, ids_ejemplares=[1]))
    assert id_p == 1
    assert ejemplar.estado == "PRESTADO"

    srv.devolver_prestamo(id_p)
    assert ejemplar.estado == "DISPONIBLE"

    with pytest.raises(PrestamoYaDevuelto):
        srv.devolver_prestamo(id_p)
