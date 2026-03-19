from std.time import perf_counter


def es_primo(n: Int) -> Bool:
    """Verifica si un número es primo."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    # Solo probamos divisores impares.
    # En vez de usar sqrt(), usamos i * i <= n para evitar conversión a float.
    var i: Int = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2

    return True


def encontrar_n_primo(objetivo: Int) -> Int:
    var contador: Int = 0
    var numero_actual: Int = 1

    while contador < objetivo:
        numero_actual += 1
        if es_primo(numero_actual):
            contador += 1

    return numero_actual


def main() raises:
    var objetivo: Int = 10000001

    var inicio = perf_counter()
    var resultado = encontrar_n_primo(objetivo)
    var fin = perf_counter()

    var duracion_s = fin - inicio

    print("El primo número {} es: {}".format(objetivo, resultado))
    print("Tiempo de ejecución: {} s ({} ms)".format(duracion_s, duracion_s * 1000.0))