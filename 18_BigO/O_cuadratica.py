import time

# ===== CONFIGURACIÓN =====
N = 10_000  # Tamaño del array
A = range(N)

print(f"Comparación de algoritmos con n={N}")
print("=" * 60)

# ===== VERSIÓN 1: O(n²) - Original (Fuerza bruta) =====
print("\n1️⃣  VERSIÓN O(n²) - Doble bucle")
inicio = time.perf_counter()

S1 = 0
for i in A:  # n operaciones
    for j in A:  # n operaciones cada una
        S1 += i + j

tiempo_1 = time.perf_counter() - inicio
print(f"   Resultado: {S1:,}")
print(f"   Tiempo: {tiempo_1:.6f} segundos")
print(f"   Complejidad: n² = {N}² = {N**2:,} operaciones")


# ===== VERSIÓN 2: O(n) - Precálculo de suma =====
print("\n2️⃣  VERSIÓN O(n) - Precálculo de suma")
inicio = time.perf_counter()

n = len(A)
suma_A = sum(A)  # O(n) - calcular una vez

S2 = 0
for i in A:  # n operaciones
    # Por cada i, sumamos: i*n + suma_A
    # Esto equivale a: (i+0) + (i+1) + (i+2) + ... + (i+(n-1))
    S2 += n * i + suma_A

tiempo_2 = time.perf_counter() - inicio
print(f"   Resultado: {S2:,}")
print(f"   Tiempo: {tiempo_2:.6f} segundos")
print(f"   Complejidad: n = {N:,} operaciones")


# ===== VERSIÓN 3: O(1) - Fórmula matemática =====
print("\n3️⃣  VERSIÓN O(1) - Fórmula matemática directa")
inicio = time.perf_counter()

n = len(A)
# Fórmula: S = 2n × suma(A)
# Para range(n): suma(0..n-1) = n(n-1)/2
suma_A = n * (n - 1) // 2
S3 = 2 * n * suma_A

tiempo_3 = time.perf_counter() - inicio
print(f"   Resultado: {S3:,}")
print(f"   Tiempo: {tiempo_3:.6f} segundos")
print(f"   Complejidad: O(1) - operaciones constantes")


# ===== COMPARACIÓN FINAL =====
print("\n" + "=" * 60)
print("📊 COMPARACIÓN DE RENDIMIENTO:")
print("=" * 60)
print(f"O(n²):  {tiempo_1:.6f}s  {'✓ Correcto' if S1 == S2 == S3 else '✗ Error'}")
print(f"O(n):   {tiempo_2:.6f}s  (×{tiempo_1/tiempo_2:.1f} más rápido)")
print(f"O(1):   {tiempo_3:.6f}s  (×{tiempo_1/tiempo_3:.1f} más rápido)")
print("=" * 60)

# Verificación
assert S1 == S2 == S3, "¡Error! Los resultados no coinciden"
print("✅ Todos los resultados coinciden")
