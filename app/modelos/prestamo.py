from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos import Base

if TYPE_CHECKING:
    from app.modelos.ejemplar import Ejemplar
    from app.modelos.socio import Socio


prestamo_ejemplares = Table(
    "prestamo_ejemplares",
    Base.metadata,
    Column("id_prestamo", Integer, ForeignKey("prestamos.id_prestamo"), primary_key=True),
    Column("id_ejemplar", Integer, ForeignKey("ejemplares.id_ejemplar"), primary_key=True),
)


class Prestamo(Base):
    __tablename__ = "prestamos"

    id_prestamo: Mapped[int] = mapped_column(primary_key=True)
    id_socio: Mapped[int] = mapped_column(ForeignKey("socios.id_socio"))
    fecha_prestamo: Mapped[date] = mapped_column(Date)
    fecha_limite: Mapped[date] = mapped_column(Date)
    fecha_devolucion: Mapped[date | None] = mapped_column(Date, nullable=True)

    socio: Mapped["Socio"] = relationship(back_populates="prestamos")
    ejemplares: Mapped[list["Ejemplar"]] = relationship(
        secondary=prestamo_ejemplares,
        back_populates="prestamos",
    )

    def __repr__(self) -> str:
        return (
            f"Prestamo(id_prestamo={self.id_prestamo!r}, id_socio={self.id_socio!r}, "
            f"fecha_prestamo={self.fecha_prestamo!r}, fecha_limite={self.fecha_limite!r}, "
            f"fecha_devolucion={self.fecha_devolucion!r})"
        )
