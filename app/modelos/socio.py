from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos import Base

if TYPE_CHECKING:
    from app.modelos.prestamo import Prestamo


class Socio(Base):
    __tablename__ = "socios"

    id_socio: Mapped[int] = mapped_column(primary_key=True)
    dni: Mapped[str] = mapped_column(String(12), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150))
    telefono: Mapped[str] = mapped_column(String(20))
    fecha_alta: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="socio")

    def __repr__(self) -> str:
        return (
            f"Socio(id_socio={self.id_socio!r}, dni={self.dni!r}, "
            f"nombre={self.nombre!r}, apellidos={self.apellidos!r}, activo={self.activo!r})"
        )
