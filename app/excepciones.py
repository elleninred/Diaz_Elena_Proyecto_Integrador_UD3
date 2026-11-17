class ErrorBiblioteca(Exception):
    """Excepción base de dominio de la biblioteca."""


class ErrorCatalogo(ErrorBiblioteca):
    """Excepción base para operaciones del catálogo."""


class AutorNoEncontrado(ErrorCatalogo):
    pass


class LibroNoEncontrado(ErrorCatalogo):
    pass


class IsbnDuplicado(ErrorCatalogo):
    pass


class PrecioInvalido(ErrorCatalogo, ValueError):
    pass


class ErrorPrestamo(ErrorBiblioteca):
    """Excepción base para operaciones de préstamos."""


class SocioNoEncontrado(ErrorPrestamo):
    pass


class SocioInactivo(ErrorPrestamo):
    pass


class EjemplarNoEncontrado(ErrorPrestamo):
    pass


class EjemplarNoDisponible(ErrorPrestamo):
    pass


class PrestamoNoEncontrado(ErrorPrestamo):
    pass


class PrestamoYaDevuelto(ErrorPrestamo):
    pass
