from sqlalchemy.orm import sessionmaker

from app.repositorios.autores import AutorRepositorio
from app.repositorios.ejemplares import EjemplarRepositorio
from app.repositorios.libros import LibroRepositorio
from app.repositorios.prestamos import PrestamoRepositorio
from app.repositorios.socios import SocioRepositorio


class UnidadTrabajoSQLAlchemy:
    def __init__(self, fabrica_sesiones: sessionmaker) -> None:
        self.fabrica_sesiones = fabrica_sesiones

    def __enter__(self):
        self.session = self.fabrica_sesiones()
        self.autores = AutorRepositorio(self.session)
        self.libros = LibroRepositorio(self.session)
        self.socios = SocioRepositorio(self.session)
        self.ejemplares = EjemplarRepositorio(self.session)
        self.prestamos = PrestamoRepositorio(self.session)
        return self

    def __exit__(self, tipo_error, error, traceback) -> None:
        if tipo_error is not None:
            self.rollback()
        self.session.close()

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
