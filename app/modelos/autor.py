from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos import Base

if TYPE_CHECKING:
    from app.modelos.libro import Libro


class Autor(Base):
    __tablename__ = "autores"

    id_autor: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(150))

    libros: Mapped[list["Libro"]] = relationship(back_populates="autor")

    def __repr__(self) -> str:
        return (
            f"Autor(id_autor={self.id_autor!r}, "
            f"nombre={self.nombre!r}, apellidos={self.apellidos!r})"
        )
