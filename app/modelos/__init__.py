from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.modelos.autor import Autor  # noqa: E402, F401
from app.modelos.libro import Libro  # noqa: E402, F401
from app.modelos.socio import Socio  # noqa: E402, F401
from app.modelos.ejemplar import Ejemplar  # noqa: E402, F401
from app.modelos.prestamo import Prestamo, prestamo_ejemplares  # noqa: E402, F401
