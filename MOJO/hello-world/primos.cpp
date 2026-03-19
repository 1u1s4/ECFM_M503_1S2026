#include <iostream>
#include <cmath>
#include <chrono>
#include <iomanip>

bool es_primo(int n) {
    if (n < 2) {
        return false;
    }
    if (n == 2) {
        return true;
    }
    if (n % 2 == 0) {
        return false;
    }

    int limite = static_cast<int>(std::sqrt(n));
    for (int i = 3; i <= limite; i += 2) {
        if (n % i == 0) {
            return false;
        }
    }

    return true;
}

int encontrar_n_primo(int objetivo) {
    int contador = 0;
    int numero_actual = 1;

    while (contador < objetivo) {
        numero_actual += 1;
        if (es_primo(numero_actual)) {
            contador += 1;
        }
    }

    return numero_actual;
}

int main() {
    int objetivo = 10000001;

    auto inicio = std::chrono::high_resolution_clock::now();
    int resultado = encontrar_n_primo(objetivo);
    auto fin = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> duracion = fin - inicio;
    double duracion_s = duracion.count();

    std::cout << "El primo número " << objetivo << " es: " << resultado << std::endl;
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Tiempo de ejecución: " << duracion_s
              << " s (" << duracion_s * 1000 << " ms)" << std::endl;

    return 0;
}
