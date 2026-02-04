# Variable global para rastrear la profundidad de las llamadas recursivas
_recursion_depth = 0

# Funcion que calcula el factorial de un numero usando recursion
def factorial(n: int, trace: bool = False) -> int:
    """Calcula el factorial de un número entero no negativo mediante recursión.
    El factorial de un número n (denotado como n!) es el producto de todos los
    enteros positivos menores o iguales a n. Por definición, 0! = 1 y 1! = 1.
    Args:
        n (int): Número entero no negativo del cual se desea calcular el factorial.
                 Debe ser mayor o igual a 0.
        trace (bool): Si es True, muestra una traza visual de las llamadas recursivas.
                      Por defecto es False.
        int: El factorial del número dado. Por ejemplo:
             - factorial(0) = 1
             - factorial(5) = 120
             - factorial(10) = 3628800
    Raises:
        ValueError: Si n es menor que 0 (números negativos no tienen factorial).
    Examples:
        >>> factorial(0)
        1
        >>> factorial(5)
        120
        >>> factorial(10)
        3628800
    """
    global _recursion_depth
    
    if n < 0:
        raise ValueError("El número debe ser no negativo")
    
    # Mostrar la llamada
    indent = "  " * _recursion_depth
    if trace:
        print(f"{indent}→ factorial({n})")
    
    # Caso base
    if n == 0 or n == 1:
        if trace:
            print(f"{indent}← Caso base: factorial({n}) = 1")
        return 1
    
    # Caso recursivo
    _recursion_depth += 1
    result = n * factorial(n - 1, trace)
    _recursion_depth -= 1
    
    if trace:
        print(f"{indent}← factorial({n}) = {n} × factorial({n-1}) = {result}")
    
    return result

def main():
    # Ejemplos de uso sin traza visual
    print("=" * 50)
    print("CÁLCULOS DE FACTORIAL (sin traza)")
    print("=" * 50)
    print(f"Factorial de 0: {factorial(0)}")   # Salida: 1
    print(f"Factorial de 5: {factorial(5)}")   # Salida: 120
    print(f"Factorial de 10: {factorial(10)}") # Salida: 3628800
    
    # Ejemplos de uso con traza visual
    print("\n" + "=" * 50)
    print("TRAZA VISUAL - FACTORIAL DE 5")
    print("=" * 50)
    print("\nSe muestra el árbol de llamadas recursivas:\n")
    result = factorial(5, trace=True)
    print(f"\n✓ Resultado final: {result}\n")
    
    print("=" * 50)
    print("TRAZA VISUAL - FACTORIAL DE 3")
    print("=" * 50)
    print("\nSe muestra el árbol de llamadas recursivas:\n")
    result = factorial(3, trace=True)
    print(f"\n✓ Resultado final: {result}\n")

if __name__ == "__main__":
    main()