from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos import Base

if TYPE_CHECKING:
    from app.modelos.libro import Libro
    from app.modelos.prestamo import Prestamo


class Ejemplar(Base):
    __tablename__ = "ejemplares"

    id_ejemplar: Mapped[int] = mapped_column(primary_key=True)
    id_libro: Mapped[int] = mapped_column(ForeignKey("libros.id_libro"))
    codigo_inventario: Mapped[int] = mapped_column(Integer, unique=True)
    ubicacion: Mapped[str] = mapped_column(String(40))
    estado: Mapped[str] = mapped_column(String(20), default="DISPONIBLE")
    fecha_alta: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    libro: Mapped["Libro"] = relationship(back_populates="ejemplares")
    prestamos: Mapped[list["Prestamo"]] = relationship(
        secondary="prestamo_ejemplares",
        back_populates="ejemplares",
    )

    def __repr__(self) -> str:
        return (
            f"Ejemplar(id_ejemplar={self.id_ejemplar!r}, id_libro={self.id_libro!r}, "
            f"codigo_inventario={self.codigo_inventario!r}, estado={self.estado!r})"
        )
