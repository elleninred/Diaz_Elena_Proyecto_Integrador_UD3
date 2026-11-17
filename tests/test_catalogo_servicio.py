from decimal import Decimal
import pytest

from app.dto.libros import DatosLibro, FiltroLibros
from app.excepciones import AutorNoEncontrado, IsbnDuplicado, LibroNoEncontrado, PrecioInvalido
from app.modelos.autor import Autor
from app.modelos.libro import Libro
from app.servicios.catalogo import CatalogoServicio


class RepoAutoresFalso:
    def __init__(self, autores: dict[int, Autor]):
        self.autores = autores

    def buscar(self, id_autor: int) -> Autor | None:
        return self.autores.get(id_autor)


class RepoLibrosFalso:
    def __init__(self, libros: dict[int, Libro]):
        self.libros = libros
        self._seq = max(libros.keys(), default=0) + 1

    def buscar(self, id_libro: int) -> Libro | None:
        return self.libros.get(id_libro)

    def buscar_por_isbn(self, isbn: str) -> Libro | None:
        return next((l for l in self.libros.values() if l.isbn == isbn), None)

    def añadir(self, libro: Libro) -> None:
        libro.id_libro = self._seq
        self.libros[self._seq] = libro
        self._seq += 1

    def buscar_con_filtros(self, filtro: FiltroLibros) -> list[Libro]:
        res = list(self.libros.values())
        if filtro.solo_activos:
            res = [l for l in res if l.activo]
        return res


class UowFalsa:
    def __init__(self, autores=None, libros=None):
        self.autores = RepoAutoresFalso(autores or {})
        self.libros = RepoLibrosFalso(libros or {})
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


@pytest.mark.parametrize("precio_invalido", [Decimal("-0.01"), Decimal("-15.00")])
def test_rechaza_precio_negativo_al_cambiar(precio_invalido):
    uow = UowFalsa()
    srv = CatalogoServicio(uow)
    with pytest.raises(PrecioInvalido):
        srv.cambiar_precio(1, precio_invalido)


def test_no_crea_libro_si_autor_no_existe():
    uow = UowFalsa(autores={})
    srv = CatalogoServicio(uow)
    datos = DatosLibro(isbn="978-1", titulo="Prueba", precio=Decimal("10.00"), id_autor=99)
    with pytest.raises(AutorNoEncontrado):
        srv.crear_libro(datos)
    assert not uow.confirmed


def test_no_crea_libro_si_isbn_duplicado():
    autor = Autor(id_autor=1, nombre="Gabriel", apellidos="García")
    libro = Libro(id_libro=1, isbn="978-1", titulo="Existente", precio=Decimal("12.00"), id_autor=1)
    uow = UowFalsa(autores={1: autor}, libros={1: libro})
    srv = CatalogoServicio(uow)

    with pytest.raises(IsbnDuplicado):
        srv.crear_libro(DatosLibro(isbn="978-1", titulo="Otro", precio=Decimal("15.00"), id_autor=1))


def test_crea_libro_correctamente():
    autor = Autor(id_autor=1, nombre="Gabriel", apellidos="García")
    uow = UowFalsa(autores={1: autor})
    srv = CatalogoServicio(uow)

    id_nuevo = srv.crear_libro(
        DatosLibro(isbn="978-2", titulo="Cien años", precio=Decimal("22.50"), id_autor=1)
    )
    assert id_nuevo == 1
    assert uow.confirmed


def test_desactivar_libro_inexistente_lanza_error():
    srv = CatalogoServicio(UowFalsa())
    with pytest.raises(LibroNoEncontrado):
        srv.desactivar_libro(404)
