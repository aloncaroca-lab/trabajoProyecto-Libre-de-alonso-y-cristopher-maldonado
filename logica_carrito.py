import json
import os

try:
    import requests
except Exception:
    requests = None


catalogo = {
    1: {"nombre": "Camisa", "precio": 25.0},
    2: {"nombre": "Pantalón", "precio": 40.0},
    3: {"nombre": "Zapatos", "precio": 60.0},
    4: {"nombre": "Gorra", "precio": 15.0},
    5: {"nombre": "Mochila", "precio": 30.0},
}

cupones = {
    "DESC10": 0.10,
    "DESC20": 0.20,
    "DESC30": 0.30,
}

ARCHIVO_CARRITO = "carrito.json"
API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
API_URL_FALLBACK = "https://open.er-api.com/v6/latest/USD"
CURRENCIES_DESTINO = ["CLP", "EUR", "GBP", "AUD", "CAD", "CHF", "JPY"]
CURRENCY_LABELS = {
    "CLP": "Pesos chilenos",
    "EUR": "Euros",
    "GBP": "Libras esterlinas",
    "AUD": "Dólares australianos",
    "CAD": "Dólares canadienses",
    "CHF": "Francos suizos",
    "JPY": "Yenes japoneses",
}


def guardar_datos(carrito: dict) -> bool:
    try:
        with open(ARCHIVO_CARRITO, "w", encoding="utf-8") as archivo:
            json.dump(carrito, archivo, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar los datos: {e}")
        return False


def cargar_datos() -> dict:
    if not os.path.exists(ARCHIVO_CARRITO):
        return {}
    try:
        with open(ARCHIVO_CARRITO, "r", encoding="utf-8") as archivo:
            datos_cargados = json.load(archivo)
            return {int(k): v for k, v in datos_cargados.items()}
    except Exception as e:
        print(f"Error al leer el archivo (puede estar corrupto): {e}")
        return {}


def codigo_valido(codigo: int) -> bool:
    return codigo in catalogo


def agregar_al_carrito(carrito: dict, codigo: int, cantidad: int) -> dict:
    carrito[codigo] = carrito.get(codigo, 0) + cantidad
    return carrito


def calcular_subtotales(carrito: dict) -> list:
    detalle = []
    for codigo, cantidad in carrito.items():
        producto = catalogo[codigo]
        subtotal = producto["precio"] * cantidad
        detalle.append((producto["nombre"], cantidad, subtotal))
    return detalle


def calcular_total_sin_descuento(carrito: dict) -> float:
    return sum(catalogo[codigo]["precio"] * cantidad for codigo, cantidad in carrito.items())


def aplicar_cupon(total: float, cupon: str):
    cupon = cupon.strip().upper()
    if not cupon:
        return total, 0.0, None
    descuento = cupones.get(cupon)
    if descuento is None:
        return total, 0.0, False
    total_final = total * (1 - descuento)
    return total_final, descuento, True


def vaciar_carrito(carrito: dict) -> dict:
    carrito.clear()
    return carrito


def fetch_usd_rates():
    if requests is None:
        print("La librería 'requests' no está instalada. Instálala con: pip install requests")
        return None
    for url in (API_URL, API_URL_FALLBACK):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            if url is API_URL_FALLBACK:
                print(f"Error al obtener la tasa de cambio: {e}")
            continue
        rates = data.get("rates")
        if not rates:
            continue
        resultado = {sym: rates[sym] for sym in CURRENCIES_DESTINO if sym in rates}
        if resultado:
            return resultado
    print("No se pudo obtener la tasa de cambio desde ninguna API.")
    return None


def calcular_detalle_convertido(carrito: dict, rates: dict) -> list:
    detalle = []
    for codigo, cantidad in carrito.items():
        producto = catalogo[codigo]
        subtotal_usd = producto["precio"] * cantidad
        subtotales = {symbol: subtotal_usd * rate for symbol, rate in rates.items()}
        detalle.append((producto["nombre"], cantidad, subtotal_usd, subtotales))
    return detalle
z