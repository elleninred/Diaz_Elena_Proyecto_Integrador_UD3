from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import SQLAlchemyError

from app.conexion import SessionLocal
from app.dto.libros import DatosLibro, FiltroLibros
from app.dto.prestamos import DatosPrestamo
from app.excepciones import ErrorBiblioteca
from app.servicios.catalogo import CatalogoServicio
from app.servicios.prestamos import PrestamoServicio
from app.unidad_trabajo import UnidadTrabajoSQLAlchemy


def leer_entero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            print("Por favor, introduce un número entero válido.")


def leer_decimal(mensaje: str, opcional: bool = False) -> Decimal | None:
    while True:
        valor = input(mensaje).strip()
        if opcional and valor == "":
            return None
        try:
            return Decimal(valor.replace(",", "."))
        except InvalidOperation:
            print("Introduce un importe decimal válido (ej. 19.95).")


def mostrar_menu() -> None:
    print("\n=== BIBLIOTECA ORM ===")
    print("1. Listar libros")
    print("2. Buscar libros")
    print("3. Crear libro")
    print("4. Actualizar precio")
    print("5. Desactivar libro")
    print("6. Registrar préstamo")
    print("7. Devolver préstamo")
    print("8. Mostrar préstamos abiertos")
    print("9. Salir")


def main() -> None:
    uow = UnidadTrabajoSQLAlchemy(SessionLocal)
    catalogo_srv = CatalogoServicio(uow)
    prestamo_srv = PrestamoServicio(uow)

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()

        try:
            if opcion == "1":
                pagina = leer_entero("Página (1..N): ")
                tamano = leer_entero("Tamaño de página: ")
                libros = catalogo_srv.listar_libros(
                    FiltroLibros(pagina=pagina, tamano=tamano)
                )
                if not libros:
                    print("No hay libros activos en esa página.")
                for l in libros:
                    print(f"[{l.id_libro}] {l.titulo} — {l.autor} ({l.precio} €)")

            elif opcion == "2":
                texto = input("Texto en título (Enter para omitir): ").strip() or None
                id_autor_str = input("ID autor (Enter para omitir): ").strip()
                id_autor = int(id_autor_str) if id_autor_str else None
                p_min = leer_decimal("Precio mínimo (Enter para omitir): ", opcional=True)
                p_max = leer_decimal("Precio máximo (Enter para omitir): ", opcional=True)
                pagina = leer_entero("Página (1): ")
                tamano = leer_entero("Tamaño (10): ")

                filtro = FiltroLibros(
                    texto=texto,
                    precio_minimo=p_min,
                    precio_maximo=p_max,
                    id_autor=id_autor,
                    solo_activos=True,
                    pagina=pagina,
                    tamano=tamano,
                )
                libros = catalogo_srv.listar_libros(filtro)
                if not libros:
                    print("No se encontraron libros con esos filtros.")
                for l in libros:
                    print(f"[{l.id_libro}] {l.titulo} — {l.autor} ({l.precio} €)")

            elif opcion == "3":
                isbn = input("ISBN: ").strip()
                titulo = input("Título: ").strip()
                precio = leer_decimal("Precio: ")
                id_autor = leer_entero("ID del autor: ")
                id_creado = catalogo_srv.crear_libro(
                    DatosLibro(
                        isbn=isbn,
                        titulo=titulo,
                        precio=precio,
                        id_autor=id_autor,
                    )
                )
                print(f"Libro creado correctamente con ID {id_creado}.")

            elif opcion == "4":
                id_libro = leer_entero("ID del libro: ")
                nuevo_precio = leer_decimal("Nuevo precio: ")
                catalogo_srv.cambiar_precio(id_libro, nuevo_precio)
                print("Precio actualizado correctamente.")

            elif opcion == "5":
                id_libro = leer_entero("ID del libro a desactivar: ")
                catalogo_srv.desactivar_libro(id_libro)
                print("Libro desactivado lógicamente.")

            elif opcion == "6":
                id_socio = leer_entero("ID del socio: ")
                ids_raw = input("IDs de ejemplares separados por coma (ej. 1,2): ").strip()
                ids_ejemplares = [int(x.strip()) for x in ids_raw.split(",") if x.strip()]
                id_prestamo = prestamo_srv.registrar_prestamo(
                    DatosPrestamo(id_socio=id_socio, ids_ejemplares=ids_ejemplares)
                )
                print(f"Préstamo registrado correctamente con ID {id_prestamo}.")

            elif opcion == "7":
                id_prestamo = leer_entero("ID del préstamo a devolver: ")
                prestamo_srv.devolver_prestamo(id_prestamo)
                print("Préstamo devuelto y ejemplares disponibles de nuevo.")

            elif opcion == "8":
                abiertos = prestamo_srv.listar_prestamos_abiertos()
                if not abiertos:
                    print("No hay préstamos abiertos.")
                for p in abiertos:
                    print(
                        f"Préstamo #{p.id_prestamo} | Socio: {p.socio} | "
                        f"Alta: {p.fecha_prestamo} | Límite: {p.fecha_limite} | "
                        f"Ejemplares: {p.ejemplares}"
                    )

            elif opcion == "9":
                print("Saliendo de Biblioteca ORM.")
                break

            else:
                print("Opción no válida.")

        except ErrorBiblioteca as error:
            print(f"[Aviso] {error}")
        except ValueError:
            print("[Error] Formato numérico no válido.")
        except SQLAlchemyError as error:
            print(f"[Error de base de datos] {error}")


if __name__ == "__main__":
    main()
