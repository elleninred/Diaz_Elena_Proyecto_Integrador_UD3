from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.dto.libros import FiltroLibros
from app.modelos.libro import Libro


class LibroRepositorio:
    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar(self, id_libro: int) -> Libro | None:
        stmt = (
            select(Libro)
            .options(joinedload(Libro.autor))
            .where(Libro.id_libro == id_libro)
        )
        return self.session.scalar(stmt)

    def buscar_por_isbn(self, isbn: str) -> Libro | None:
        stmt = select(Libro).where(Libro.isbn == isbn)
        return self.session.scalar(stmt)

    def añadir(self, libro: Libro) -> None:
        self.session.add(libro)

    def buscar_con_filtros(self, filtro: FiltroLibros) -> list[Libro]:
        """Consulta dinámica paginada evitando N+1 mediante joinedload(Libro.autor)."""
        stmt = select(Libro).options(joinedload(Libro.autor))

        if filtro.solo_activos:
            stmt = stmt.where(Libro.activo.is_(True))

        if filtro.texto:
            stmt = stmt.where(Libro.titulo.ilike(f"%{filtro.texto.strip()}%"))

        if filtro.id_autor is not None:
            stmt = stmt.where(Libro.id_autor == filtro.id_autor)

        if filtro.precio_minimo is not None:
            stmt = stmt.where(Libro.precio >= filtro.precio_minimo)

        if filtro.precio_maximo is not None:
            stmt = stmt.where(Libro.precio <= filtro.precio_maximo)

        offset = (max(filtro.pagina, 1) - 1) * max(filtro.tamano, 1)
        stmt = stmt.order_by(Libro.id_libro).offset(offset).limit(filtro.tamano)

        return list(self.session.scalars(stmt).all())
