import os
from urllib.parse import quote_plus


def _construir_url(nombre_bd: str | None) -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    usuario = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    faltantes = [
        nombre
        for nombre, valor in (
            ("DB_NAME", nombre_bd),
            ("DB_USER", usuario),
            ("DB_PASSWORD", password),
        )
        if not valor
    ]
    if faltantes:
        raise ValueError(
            "Faltan variables de entorno necesarias: " + ", ".join(faltantes)
        )

    return (
        "postgresql+psycopg://"
        f"{quote_plus(usuario)}:"
        f"{quote_plus(password)}"
        f"@{host}:{port}/{quote_plus(nombre_bd)}"
    )


def obtener_url_bd() -> str:
    """Construye la URL para la base de datos principal de la aplicación y Alembic."""
    return _construir_url(os.getenv("DB_NAME"))


def obtener_url_bd_test() -> str:
    """Construye la URL de pruebas exigiendo que termine en _test."""
    nombre_bd_test = os.getenv("DB_TEST_NAME") or os.getenv("DB_NAME")
    if not nombre_bd_test or not nombre_bd_test.endswith("_test"):
        raise RuntimeError(
            "Por seguridad, las pruebas solo permiten bases terminadas en _test. "
            "Revisa DB_TEST_NAME o DB_NAME."
        )
    return _construir_url(nombre_bd_test)
