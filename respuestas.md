# Respuestas — Proyecto Integrador UD3

1. **¿Qué responsabilidad tiene una entidad ORM?**
   Representar una tabla de la base de datos relacional como una clase Python, definiendo sus columnas, restricciones, tipos de datos y relaciones navegables mediante objetos sin acoplar lógica de acceso a datos ni interfaz.

2. **¿Qué diferencia existe entre repositorio y servicio?**
   El repositorio encapsula la construcción de consultas y persistencia sobre una entidad usando la `Session` (sin `commit()` ni reglas de negocio). El servicio orquesta casos de uso completos, aplica las reglas de negocio, valida precondiciones y delimita la transacción mediante la Unit of Work.

3. **¿Qué función tiene la Unit of Work?**
   Agrupar todos los repositorios bajo una misma `Session` de SQLAlchemy, exponiendo operaciones transaccionales unificadas (`flush()`, `commit()`, `rollback()`) y garantizando el cierre seguro de recursos al salir del contexto.

4. **¿Por qué los repositorios no ejecutan `commit()`?**
   Porque un caso de uso puede involucrar varios repositorios a la vez (por ejemplo, crear un préstamo y cambiar el estado de varios ejemplares). Si cada repositorio hiciera `commit()`, se rompería la atomicidad de la operación.

5. **¿Qué es un DTO?**
   Un *Data Transfer Object* (objeto plano inmutable, implementado con `@dataclass(frozen=True)`) destinado únicamente a transportar datos entre capas sin exponer entidades ORM activas ni depender de sesiones abiertas.

6. **¿Por qué se utilizan DTO en las lecturas?**
   Para evitar errores de carga perezosa (`DetachedInstanceError`) una vez cerrada la `Session` en la Unit of Work y para devolver únicamente los datos proyectados que necesita la capa de presentación.

7. **¿Qué significa que una operación sea atómica?**
   Que todas las modificaciones dentro de la transacción se confirman conjuntamente (`commit()`) o, ante cualquier fallo o excepción de negocio, se revierten por completo (`rollback()`), evitando estados intermedios inconsistentes.

8. **¿Qué problema intenta evitar `selectinload()`?**
   El problema de consultas **N+1**: en lugar de lanzar una consulta SQL adicional por cada entidad padre al acceder a sus colecciones relacionadas, ejecuta una única consulta agrupada con `WHERE id IN (...)`.

9. **¿Qué diferencia existe entre una prueba unitaria y una de integración?**
   La prueba unitaria aísla la lógica de negocio de los servicios usando repositorios y Unit of Work falsos en memoria (sin base de datos). La prueba de integración verifica la interacción real con PostgreSQL, consultas SQLAlchemy, restricciones y transacciones.

10. **¿Por qué se utiliza `biblioteca_test`?**
    Para aislar completamente el entorno de pruebas de la base de datos principal de trabajo, evitando borrar o corromper datos reales durante la creación y limpieza de tablas.

11. **¿Qué función tiene una `fixture`?**
    Preparar, inicializar y limpiar de forma reutilizable las dependencias y datos de contexto necesarios antes y después de ejecutar cada prueba en `pytest`.

12. **¿Qué hace `pytest.raises()`?**
    Actúa como gestor de contexto que verifica que el bloque de código ejecutado lanza exactamente la excepción esperada; si no se lanza o es de otro tipo, la prueba falla.

13. **¿Qué función tiene Alembic?**
    Gestionar el control de versiones del esquema de la base de datos de forma incremental y reproducible, sincronizando los cambios de los modelos ORM con las tablas de PostgreSQL.

14. **¿Qué diferencia existe entre `upgrade()` y `downgrade()`?**
    `upgrade()` aplica los cambios estructurales hacia una revisión posterior del esquema (crear tablas/columnas), mientras que `downgrade()` revierte esos cambios hacia una revisión anterior.

15. **¿Por qué deben guardarse las migraciones en Git?**
    Para que todo el equipo pueda reconstruir exactamente el mismo historial de evolución del esquema en sus entornos locales y sincronizar código y estructura de base de datos en cada commit.

16. **¿Qué mejora incorporaríais en una siguiente versión?**
    Incorporar gestión de sanciones por devoluciones fuera de `fecha_limite`, reservas de ejemplares prestados, registro de auditoría de movimientos y exposición de los servicios mediante una API REST con FastAPI.
