def es_primo(n):
    """Verifica si un número es primo."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Solo probamos divisores impares hasta la raíz cuadrada de n
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def encontrar_n_primo(objetivo):
    contador = 0
    numero_actual = 1
    
    while contador < objetivo:
        numero_actual += 1
        if es_primo(numero_actual):
            contador += 1
            
    return numero_actual

if __name__ == "__main__":
    import time

    # Calculamos el primo número N y medimos el tiempo total
    objetivo = 1000001
    inicio = time.perf_counter()
    resultado = encontrar_n_primo(objetivo)
    fin = time.perf_counter()

    duracion_s = fin - inicio
    print(f"El primo número {objetivo:,} es: {resultado}")
    print(f"Tiempo de ejecución: {duracion_s:.6f} s ({duracion_s * 1000:.2f} ms)")