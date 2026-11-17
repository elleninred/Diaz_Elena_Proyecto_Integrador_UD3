from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modelos.prestamo import Prestamo


class PrestamoRepositorio:
    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar(self, id_prestamo: int) -> Prestamo | None:
        stmt = (
            select(Prestamo)
            .options(
                joinedload(Prestamo.socio),
                selectinload(Prestamo.ejemplares),
            )
            .where(Prestamo.id_prestamo == id_prestamo)
        )
        return self.session.scalar(stmt)

    def añadir(self, prestamo: Prestamo) -> None:
        self.session.add(prestamo)

    def listar_abiertos(self) -> list[Prestamo]:
        """Carga préstamos abiertos evitando N+1 en socio y ejemplares."""
        stmt = (
            select(Prestamo)
            .options(
                joinedload(Prestamo.socio),
                selectinload(Prestamo.ejemplares),
            )
            .where(Prestamo.fecha_devolucion.is_(None))
            .order_by(Prestamo.id_prestamo)
        )
        return list(self.session.scalars(stmt).all())
