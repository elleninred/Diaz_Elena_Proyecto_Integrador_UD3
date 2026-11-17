from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modelos import Base

if TYPE_CHECKING:
    from app.modelos.autor import Autor
    from app.modelos.ejemplar import Ejemplar


class Libro(Base):
    __tablename__ = "libros"

    id_libro: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True)
    titulo: Mapped[str] = mapped_column(String(200))
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    id_autor: Mapped[int] = mapped_column(ForeignKey("autores.id_autor"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    autor: Mapped["Autor"] = relationship(back_populates="libros")
    ejemplares: Mapped[list["Ejemplar"]] = relationship(back_populates="libro")

    def __repr__(self) -> str:
        return (
            f"Libro(id_libro={self.id_libro!r}, isbn={self.isbn!r}, "
            f"titulo={self.titulo!r}, precio={self.precio!r}, activo={self.activo!r})"
        )
