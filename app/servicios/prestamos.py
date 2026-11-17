from datetime import date, timedelta

from app.dto.prestamos import DatosPrestamo, PrestamoResumen
from app.excepciones import (
    EjemplarNoDisponible,
    EjemplarNoEncontrado,
    PrestamoNoEncontrado,
    PrestamoYaDevuelto,
    SocioInactivo,
    SocioNoEncontrado,
)
from app.modelos.prestamo import Prestamo


class PrestamoServicio:
    def __init__(self, unidad_trabajo) -> None:
        self.unidad_trabajo = unidad_trabajo

    def registrar_prestamo(self, datos: DatosPrestamo) -> int:
        if not datos.ids_ejemplares:
            raise EjemplarNoEncontrado("Debe indicar al menos un ejemplar")

        with self.unidad_trabajo as uow:
            socio = uow.socios.buscar(datos.id_socio)
            if socio is None:
                raise SocioNoEncontrado(f"No se encuentra el socio con ID {datos.id_socio}")
            if not socio.activo:
                raise SocioInactivo(f"El socio con ID {datos.id_socio} está inactivo")

            ejemplares_validar = []
            for id_ejemplar in datos.ids_ejemplares:
                ejemplar = uow.ejemplares.buscar(id_ejemplar)
                if ejemplar is None:
                    raise EjemplarNoEncontrado(f"El ejemplar con ID {id_ejemplar} no existe")
                if ejemplar.estado != "DISPONIBLE":
                    raise EjemplarNoDisponible(
                        f"El ejemplar con ID {id_ejemplar} no está disponible"
                    )
                ejemplares_validar.append(ejemplar)

            hoy = date.today()
            prestamo = Prestamo(
                id_socio=socio.id_socio,
                fecha_prestamo=hoy,
                fecha_limite=hoy + timedelta(days=datos.dias_prestamo),
            )

            for ejemplar in ejemplares_validar:
                prestamo.ejemplares.append(ejemplar)
                ejemplar.estado = "PRESTADO"

            uow.prestamos.añadir(prestamo)
            uow.flush()
            id_prestamo = prestamo.id_prestamo
            uow.commit()
            return id_prestamo

    def devolver_prestamo(self, id_prestamo: int) -> bool:
        with self.unidad_trabajo as uow:
            prestamo = uow.prestamos.buscar(id_prestamo)
            if prestamo is None:
                raise PrestamoNoEncontrado(f"No existe el préstamo con ID {id_prestamo}")
            if prestamo.fecha_devolucion is not None:
                raise PrestamoYaDevuelto(f"El préstamo {id_prestamo} ya fue devuelto")

            prestamo.fecha_devolucion = date.today()
            for ejemplar in prestamo.ejemplares:
                ejemplar.estado = "DISPONIBLE"

            uow.commit()
            return True

    def listar_prestamos_abiertos(self) -> list[PrestamoResumen]:
        with self.unidad_trabajo as uow:
            prestamos = uow.prestamos.listar_abiertos()
            resultado: list[PrestamoResumen] = []
            for p in prestamos:
                nombre_socio = (
                    f"{p.socio.nombre} {p.socio.apellidos}"
                    if p.socio is not None
                    else f"Socio #{p.id_socio}"
                )
                resultado.append(
                    PrestamoResumen(
                        id_prestamo=p.id_prestamo,
                        socio=nombre_socio,
                        fecha_prestamo=p.fecha_prestamo,
                        fecha_limite=p.fecha_limite,
                        fecha_devolucion=p.fecha_devolucion,
                        ejemplares=[e.id_ejemplar for e in p.ejemplares],
                    )
                )
            return resultado
