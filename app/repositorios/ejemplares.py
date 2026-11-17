from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.modelos.ejemplar import Ejemplar


class EjemplarRepositorio:
    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar(self, id_ejemplar: int) -> Ejemplar | None:
        stmt = (
            select(Ejemplar)
            .options(joinedload(Ejemplar.libro))
            .where(Ejemplar.id_ejemplar == id_ejemplar)
        )
        return self.session.scalar(stmt)

    def añadir(self, ejemplar: Ejemplar) -> None:
        self.session.add(ejemplar)
