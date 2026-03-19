Quiero hacer una app de grafos usando PyQt6 en la cual poder setear dos parametros:
- NxN = el tamaño del grafo, con restriccion de (0, 100]
- D, densidad que definiremos como V_A / V_T, donde V_A es la cantidad de vertices con aristas y V_T la cantidad total de vertices
luego dado los parametros generar un grafo reticular cuadrado segun los parametros. 


- Quiero que el paradigma principal sea POO
- Quiero se asignen pesos de forma aleatoria a los vertices entre [0, 1]
- Quiero la interfaz minimalista, solo blanco y negro, neo-brutalista.


Ahora, el fin, es poder observar los siguientes 3 algoritmos de busqueda:
1. Búsqueda en Amplitud 
2. Búsqueda en Profundidad
3. Dijkstra
4. como "bogo-sort" o sea, aleatorio

Quisiera poder ver los 4 algoritmos ejecutandose a la misma vez, con un temporizador y al final el tamaño del camino encontrado


- El inicio siempre sera la esquina superir izquierda y el final la esquina inferior derecha
- si se detecta GPU (NVIDIA, AMD, AppleSillicon (Mx)), utilizarla (colocar un indicador en la UI)
- Procurar una buena UI/UX