from decimal import Decimal

from app.dto.libros import DatosLibro, FiltroLibros, LibroResumen
from app.excepciones import (
    AutorNoEncontrado,
    IsbnDuplicado,
    LibroNoEncontrado,
    PrecioInvalido,
)
from app.modelos.libro import Libro


class CatalogoServicio:
    def __init__(self, unidad_trabajo) -> None:
        self.unidad_trabajo = unidad_trabajo

    @staticmethod
    def _a_resumen(libro: Libro) -> LibroResumen:
        nombre_autor = (
            f"{libro.autor.nombre} {libro.autor.apellidos}"
            if libro.autor is not None
            else f"Autor #{libro.id_autor}"
        )
        return LibroResumen(
            id_libro=libro.id_libro,
            titulo=libro.titulo,
            autor=nombre_autor,
            precio=libro.precio,
        )

    def listar_libros(self, filtro: FiltroLibros | None = None) -> list[LibroResumen]:
        filtro_efectivo = filtro or FiltroLibros()
        with self.unidad_trabajo as uow:
            libros = uow.libros.buscar_con_filtros(filtro_efectivo)
            return [self._a_resumen(libro) for libro in libros]

    def buscar_libro(self, id_libro: int) -> LibroResumen:
        with self.unidad_trabajo as uow:
            libro = uow.libros.buscar(id_libro)
            if libro is None:
                raise LibroNoEncontrado(f"No existe el libro con ID {id_libro}")
            return self._a_resumen(libro)

    def crear_libro(self, datos: DatosLibro) -> int:
        if datos.precio < Decimal("0"):
            raise PrecioInvalido("El precio no puede ser negativo")

        with self.unidad_trabajo as uow:
            autor = uow.autores.buscar(datos.id_autor)
            if autor is None:
                raise AutorNoEncontrado(f"No existe el autor con ID {datos.id_autor}")

            if uow.libros.buscar_por_isbn(datos.isbn) is not None:
                raise IsbnDuplicado(f"Ya existe un libro con ISBN {datos.isbn}")

            libro = Libro(
                isbn=datos.isbn.strip(),
                titulo=datos.titulo.strip(),
                precio=datos.precio,
                id_autor=datos.id_autor,
                activo=True,
                observaciones=datos.observaciones,
            )
            uow.libros.añadir(libro)
            uow.flush()
            id_libro = libro.id_libro
            uow.commit()
            return id_libro

    def cambiar_precio(self, id_libro: int, precio: Decimal) -> bool:
        if precio < Decimal("0"):
            raise PrecioInvalido("El precio no puede ser negativo")

        with self.unidad_trabajo as uow:
            libro = uow.libros.buscar(id_libro)
            if libro is None:
                raise LibroNoEncontrado(f"No existe el libro con ID {id_libro}")
            libro.precio = precio
            uow.commit()
        return True

    def desactivar_libro(self, id_libro: int) -> bool:
        with self.unidad_trabajo as uow:
            libro = uow.libros.buscar(id_libro)
            if libro is None:
                raise LibroNoEncontrado(f"No existe el libro con ID {id_libro}")
            libro.activo = False
            uow.commit()
        return True
