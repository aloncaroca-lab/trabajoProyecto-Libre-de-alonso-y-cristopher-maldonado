import logica_carrito as logica


def mostrar_catalogo():
    print("\nCatálogo de productos:")
    for codigo, producto in logica.catalogo.items():
        print(f"{codigo}. {producto['nombre']} - ${producto['precio']:.2f}")
    print()


def pedir_y_agregar_producto(carrito: dict) -> dict:
    try:
        codigo = int(input("Ingrese el código del producto: "))
        if not logica.codigo_valido(codigo):
            print("Código inválido.")
            return carrito
        cantidad = int(input("Ingrese la cantidad: "))
        if cantidad <= 0:
            print("La cantidad debe ser mayor que cero.")
            return carrito
        carrito = logica.agregar_al_carrito(carrito, codigo, cantidad)
        print(f"Se agregaron {cantidad} x {logica.catalogo[codigo]['nombre']} al carrito.")
    except ValueError:
        print("Entrada inválida. Intente nuevamente.")
    return carrito


def mostrar_carrito(carrito: dict):
    if not carrito:
        print("\nEl carrito está vacío.\n")
        return
    print("\nDetalle del carrito:")
    total = 0.0
    for nombre, cantidad, subtotal in logica.calcular_subtotales(carrito):
        total += subtotal
        print(f"{nombre} x {cantidad} = ${subtotal:.2f}")
    print(f"Total parcial: ${total:.2f}\n")


def mostrar_carrito_con_conversion(carrito: dict):
    if not carrito:
        print("\nEl carrito está vacío.\n")
        return
    rates = logica.fetch_usd_rates()
    if rates is None:
        print("No se pudo obtener la tasa. Mostrando solo USD:\n")
        mostrar_carrito(carrito)
        return
    print("\n+" + "=" * 64 + "+")
    print("|       DETALLE DEL CARRITO CON CONVERSIÓN       |")
    print("+" + "=" * 64 + "+")
    total_usd = 0.0
    total_convertido = {symbol: 0.0 for symbol in rates}
    for nombre, cantidad, subtotal_usd, subtotales in logica.calcular_detalle_convertido(carrito, rates):
        total_usd += subtotal_usd
        for symbol, subtotal_converted in subtotales.items():
            total_convertido[symbol] += subtotal_converted
        print(f"| {nombre} x {cantidad} = ${subtotal_usd:.2f} USD")
        for symbol in rates:
            label = logica.CURRENCY_LABELS.get(symbol, "")
            print(f"|    → ${subtotales[symbol]:.2f} {symbol} ({label})")
        print("+" + "-" * 64 + "+")
    print("| Total: ${:.2f} USD".format(total_usd))
    for symbol in rates:
        label = logica.CURRENCY_LABELS.get(symbol, "")
        print(f"|    → ${total_convertido[symbol]:.2f} {symbol} ({label})")
    print("+" + "=" * 64 + "+")
    print()


def calcular_total(carrito: dict):
    if not carrito:
        print("\nEl carrito está vacío.\n")
        return
    total = logica.calcular_total_sin_descuento(carrito)
    print(f"\nTotal sin descuento: ${total:.2f}")
    print("Cupones disponibles:")
    for codigo, descuento in logica.cupones.items():
        print(f"  {codigo} -> {int(descuento * 100)}%")

    while True:
        cupon = input("Ingrese un cupón de descuento (o deje vacío): ").strip()
        total_final, descuento, valido = logica.aplicar_cupon(total, cupon)
        if valido is True:
            print(f"Cupón {cupon.upper()} aplicado: {int(descuento * 100)}% de descuento.")
            print(f"Total con descuento: ${total_final:.2f}\n")
            break
        elif valido is False:
            print("Cupón inválido. Verifique el código y vuelva a intentarlo.")
        else:
            print(f"Total a pagar: ${total:.2f}\n")
            break


def vaciar_carrito(carrito: dict) -> dict:
    carrito = logica.vaciar_carrito(carrito)
    print("El carrito ha sido vaciado.")
    return carrito


def menu():
    carrito = logica.cargar_datos()
    if carrito:
        print("¡Datos previos cargados con éxito! Puedes continuar con tu compra.")
    else:
        print("No se encontró historial de compras. Iniciando carrito vacío.")
    print()

    while True:
        print("+" + "=" * 44 + "+")
        print("|     SIMULADOR DE CARRITO DE COMPRAS     |")
        print("+" + "=" * 44 + "+")
        print("| 1. Mostrar catálogo                    |")
        print("| 2. Agregar producto al carrito         |")
        print("| 3. Ver detalle del carrito             |")
        print("| 4. Calcular total                      |")
        print("| 5. Vaciar carrito                      |")
        print("| 6. Mostrar carrito con conversión a monedas importantes |")
        print("| 7. Salir (escriba '7' o 'Salir')       |")
        print("+" + "=" * 44 + "+")
        opcion = input("Seleccione una opción: ").strip()
        opcion_normalizada = opcion.lower()

        if opcion == "1":
            mostrar_catalogo()
        elif opcion == "2":
            carrito = pedir_y_agregar_producto(carrito)
        elif opcion == "3":
            mostrar_carrito(carrito)
        elif opcion == "4":
            calcular_total(carrito)
        elif opcion == "5":
            carrito = vaciar_carrito(carrito)
        elif opcion == "6":
            mostrar_carrito_con_conversion(carrito)
        elif opcion == "7" or opcion_normalizada == "salir":
            if logica.guardar_datos(carrito):
                print("¡Datos guardados exitosamente antes de salir!")
            print("Gracias por usar el simulador.")
            break
        else:
            print("Opción inválida. Intente nuevamente.")
        print()


if __name__ == "__main__":
    menu()