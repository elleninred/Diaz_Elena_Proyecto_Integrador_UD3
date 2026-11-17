# Proyecto Integrador UD3: Biblioteca ORM Completa

Aplicación de consola en Python para la gestión integral de una biblioteca mediante arquitectura por capas, SQLAlchemy 2.x, PostgreSQL, Alembic y pytest.

## Integrantes y reparto de tareas
- **Integrante 1 (Modelos y repositorios):** Entidades ORM (`Autor`, `Libro`, `Socio`, `Ejemplar`, `Prestamo`), relaciones `1:N` y `N:M`, consultas dinámicas paginadas y optimización N+1 (`joinedload` / `selectinload`).
- **Integrante 2 (Servicios y transacciones):** Reglas de negocio de catálogo y préstamos, DTOs inmutables, excepciones de dominio y patrón Unit of Work (`commit` / `rollback`).
- **Integrante 3 (Pruebas, migraciones y documentación):** Pruebas unitarias con dobles en memoria, pruebas de integración en `biblioteca_test`, migraciones incrementales con Alembic y documentación.

## Requisitos
- Python 3.11 o superior
- PostgreSQL 15 o superior

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Variables de entorno necesarias
Configura las siguientes variables antes de ejecutar la aplicación, Alembic o `pytest`:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=biblioteca
export DB_TEST_NAME=biblioteca_test
export DB_USER=tu_usuario
export DB_PASSWORD=tu_password
```

## Creación de bases de datos en PostgreSQL
```sql
CREATE DATABASE biblioteca;
CREATE DATABASE biblioteca_test;
```

## Aplicación de migraciones con Alembic
El historial de migraciones está en `alembic/versions/`:

| Revisión | Contenido |
|----------|-----------|
| `0001` | Esquema inicial (autores, socios, libros, ejemplares, préstamos, préstamo_ejemplares) |
| `0002` | Añade la columna `observaciones` a `libros` |

La base `biblioteca` debe crearse **vacía** (sin tablas): el esquema lo crea Alembic, no `create_all()`.
```bash
alembic upgrade head
```
Para revertir la última migración y volver a aplicarla:
```bash
alembic downgrade -1
alembic upgrade head
```

## Ejecución de la aplicación
```bash
python main.py
```

## Ejecución de las pruebas
```bash
pytest -q
```

## Estructura del proyecto
```text
biblioteca_orm/
├── alembic/
├── app/
│   ├── modelos/
│   ├── repositorios/
│   ├── servicios/
│   ├── dto/
│   ├── configuracion.py
│   ├── conexion.py
│   ├── excepciones.py
│   └── unidad_trabajo.py
├── tests/
│   ├── conftest.py
│   ├── test_catalogo_servicio.py
│   ├── test_prestamo_servicio.py
│   ├── test_repositorios.py
│   └── test_rendimiento.py
├── capturas/
├── main.py
├── alembic.ini
├── pytest.ini
├── requirements.txt
├── README.md
└── respuestas.pdf
```

## Arquitectura utilizada
`Interfaz de consola (main.py)` → `Servicios (DTOs)` → `Unit of Work` → `Repositorios ORM` → `SQLAlchemy` → `PostgreSQL`

## Decisiones principales y control de rendimiento (N+1)
- **Separación de DTOs:** Las lecturas devuelven `@dataclass(frozen=True)` (`LibroResumen`, `PrestamoResumen`) para evitar `DetachedInstanceError` tras cerrar la sesión.
- **Optimización N+1 (medida con `pytest -q -s tests/test_rendimiento.py`):** el test cuenta los `SELECT` reales enviados a PostgreSQL con 5 autores / 5 préstamos.

  | Consulta | Antes de optimizar | Después de optimizar |
  |----------|--------------------|----------------------|
  | Autores con sus libros (`selectinload(Autor.libros)`) | 1 + 5 = **6** | **2** (autores + una agrupada con `IN`) |
  | Libros con su autor (`joinedload(Libro.autor)`) | 1 + 5 = **6** | **1** (con `JOIN`) |
  | Préstamos con socio y ejemplares (`joinedload` + `selectinload`) | 1 + 5 + 5 = **11** | **2** |

- **Estrategia de carga:** `joinedload` para relaciones muchos-a-uno (socio, autor), que añade un `JOIN` sin duplicar filas; `selectinload` para colecciones (libros, ejemplares), que evita multiplicar filas y el producto cartesiano.
- **Alembic gestiona el esquema:** `create_all()` solo se usa en las pruebas sobre `biblioteca_test`, nunca sobre `biblioteca`.
- **Eliminación lógica:** los libros se desactivan (`activo = False`) en lugar de borrarse, para conservar el historial de ejemplares y préstamos.

## Errores conocidos o limitaciones
- La aplicación de consola no gestiona sanciones ni reservas; el plazo de préstamo es fijo (15 días por defecto).
- `FiltroLibros` pagina con `OFFSET`, que se vuelve lento en tablas muy grandes (convendría paginación por cursor).
- El estado del ejemplar es una cadena (`"DISPONIBLE"`, `"PRESTADO"`); sería más seguro un `Enum`.
- No se controla la concurrencia: dos usuarios podrían prestar el mismo ejemplar a la vez (haría falta `SELECT ... FOR UPDATE`).
- Las pruebas de integración necesitan una instancia de PostgreSQL con la base `biblioteca_test`.
- La búsqueda por título usa `ILIKE '%texto%'`, que no aprovecha índices.
