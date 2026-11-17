from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DatosPrestamo:
    id_socio: int
    ids_ejemplares: list[int]
    dias_prestamo: int = 15


@dataclass(frozen=True)
class PrestamoResumen:
    id_prestamo: int
    socio: str
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: date | None
    ejemplares: list[int]
