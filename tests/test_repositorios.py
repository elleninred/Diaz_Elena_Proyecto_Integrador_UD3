from decimal import Decimal
import pytest

from app.dto.libros import DatosLibro, FiltroLibros
from app.dto.prestamos import DatosPrestamo
from app.excepciones import IsbnDuplicado
from app.servicios.catalogo import CatalogoServicio
from app.servicios.prestamos import PrestamoServicio


def test_integracion_insertar_y_recuperar_libro(uow_integracion, datos_base_integracion):
    srv = CatalogoServicio(uow_integracion)
    id_nuevo = srv.crear_libro(
        DatosLibro(
            isbn="978-8497592208",
            titulo="El amor en los tiempos del cólera",
            precio=Decimal("18.50"),
            id_autor=datos_base_integracion["id_autor"],
        )
    )
    recuperado = srv.buscar_libro(id_nuevo)
    assert recuperado.titulo == "El amor en los tiempos del cólera"
    assert recuperado.autor == "Isabel Allende"


def test_integracion_isbn_duplicado(uow_integracion, datos_base_integracion):
    srv = CatalogoServicio(uow_integracion)
    with pytest.raises(IsbnDuplicado):
        srv.crear_libro(
            DatosLibro(
                isbn="978-8401352836",
                titulo="Duplicado",
                precio=Decimal("10.00"),
                id_autor=datos_base_integracion["id_autor"],
            )
        )


def test_integracion_registrar_y_devolver_prestamo(uow_integracion, datos_base_integracion):
    srv = PrestamoServicio(uow_integracion)
    id_ejemplar = datos_base_integracion["id_ejemplar"]

    id_prestamo = srv.registrar_prestamo(
        DatosPrestamo(
            id_socio=datos_base_integracion["id_socio"],
            ids_ejemplares=[id_ejemplar],
        )
    )

    with uow_integracion as uow:
        ej = uow.ejemplares.buscar(id_ejemplar)
        assert ej.estado == "PRESTADO"

    srv.devolver_prestamo(id_prestamo)

    with uow_integracion as uow:
        ej = uow.ejemplares.buscar(id_ejemplar)
        assert ej.estado == "DISPONIBLE"


def test_integracion_filtros_y_paginacion(uow_integracion, datos_base_integracion):
    srv = CatalogoServicio(uow_integracion)
    resultados = srv.listar_libros(
        FiltroLibros(texto="espíritus", precio_minimo=Decimal("10.00"), pagina=1, tamano=5)
    )
    assert len(resultados) == 1
