from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DatosLibro:
    isbn: str
    titulo: str
    precio: Decimal
    id_autor: int
    observaciones: str | None = None


@dataclass(frozen=True)
class LibroResumen:
    id_libro: int
    titulo: str
    autor: str
    precio: Decimal


@dataclass(frozen=True)
class FiltroLibros:
    texto: str | None = None
    precio_minimo: Decimal | None = None
    precio_maximo: Decimal | None = None
    id_autor: int | None = None
    solo_activos: bool = True
    pagina: int = 1
    tamano: int = 10
