from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modelos.autor import Autor


class AutorRepositorio:
    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar(self, id_autor: int) -> Autor | None:
        return self.session.get(Autor, id_autor)

    def añadir(self, autor: Autor) -> None:
        self.session.add(autor)

    def listar_con_libros(self) -> list[Autor]:
        """Evita N+1 al cargar autores con sus libros usando selectinload."""
        stmt = (
            select(Autor)
            .options(selectinload(Autor.libros))
            .order_by(Autor.apellidos, Autor.nombre)
        )
        return list(self.session.scalars(stmt).all())
