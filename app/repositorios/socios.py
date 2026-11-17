from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modelos.socio import Socio


class SocioRepositorio:
    def __init__(self, session: Session) -> None:
        self.session = session

    def buscar(self, id_socio: int) -> Socio | None:
        return self.session.get(Socio, id_socio)

    def añadir(self, socio: Socio) -> None:
        self.session.add(socio)

    def listar_activos(self) -> list[Socio]:
        stmt = select(Socio).where(Socio.activo.is_(True)).order_by(Socio.id_socio)
        return list(self.session.scalars(stmt).all())
