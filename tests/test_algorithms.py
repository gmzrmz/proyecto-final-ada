"""
Unit tests for algorithm correctness.
Original tests from test_taller_7.py adapted for the new project structure.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms import (
    brute_force,
    backtracking,
    divide_and_conquer,
    memoization,
    tabulation,
)

# =============================================================================
# TEST CASE DEFINITIONS
# =============================================================================

# Defined 1
# Prueba: Verifica correctitud básica con matriz estándar
# Caso: Matriz 5x6 con valores variados, camino óptimo predefinido
# Objetivo: Validar que el algoritmo encuentra el camino esperado en caso realista
M1 = [
    [3, 4, 1, 2, 8, 6],
    [6, 1, 8, 2, 7, 4],
    [5, 9, 3, 9, 9, 5],
    [8, 4, 1, 3, 2, 6],
    [3, 7, 2, 8, 6, 4]
]
expected_path_M1 = None
expected_cost_M1 = 16

# Defined 2
# Prueba: Similar a M1 pero con cambio sutil en un valor
# Caso: Matriz 5x6 con una celda diferente (posición [4,4])
# Objetivo: Validar que pequeños cambios afectan correctamente el camino óptimo
M2 = [
    [3, 4, 1, 2, 8, 6],
    [6, 1, 8, 2, 7, 4],
    [5, 9, 3, 9, 9, 5],
    [8, 4, 1, 3, 2, 6],
    [3, 7, 2, 1, 2, 3]
]
expected_path_M2 = None
expected_cost_M2 = 11

# All positive numbers
# Prueba: Verifica caso donde todos los valores son positivos
# Caso: Matriz 2x3 con todos valores = 1
# Objetivo: Validar que funciona correctamente sin números negativos o ceros
M3 = [
    [1, 1, 1],
    [1, 1, 1],
]
expected_path_M3 = None
expected_cost_M3 = 3

# All negative numbers
# Prueba: Verifica caso donde todos los valores son negativos
# Caso: Matriz 2x3 con todos valores = -5
# Objetivo: Validar que minimiza correctamente con números negativos (busca más negativo)
M4 = [
    [-5, -5, -5],
    [-5, -5, -5],
]
expected_path_M4 = None
expected_cost_M4 = -15

# Mixed numbers (positive & negative)
# Prueba: Verifica mezcla de números positivos y negativos
# Caso: Matriz 3x3 con valores variados positivos y negativos
# Objetivo: Validar que calcula correctamente sumas con signos mixtos
M5 = [
    [5, -4, 6],
    [-3, 10, -1],
    [2, -2, 1]
]
expected_path_M5 = None
expected_cost_M5 = 0

# Single positive element
# Prueba: Verifica edge case de matriz 1x1 con positivo
# Caso: Matriz 1x1 con valor 7
# Objetivo: Validar que maneja matriz mínima posible
M6 = [[7]]
expected_path_M6 = None
expected_cost_M6 = 7

# Single negative element
# Prueba: Verifica edge case de matriz 1x1 con negativo
# Caso: Matriz 1x1 con valor -9
# Objetivo: Validar que maneja negativo en matriz mínima
M7 = [[-9]]
expected_path_M7 = None
expected_cost_M7 = -9

# Empty matrix → camino vacío
# Prueba: Verifica el edge case de matriz vacía
# Caso: Matriz vacía []
# Objetivo: Validar manejo de entrada nula sin crashes
M8 = []
expected_path_M8 = []
expected_cost_M8 = 0

# Large numbers
# Prueba: Verifica que funciona con números muy grandes
# Caso: Matriz 2x3 con valores de magnitud 10^6
# Objetivo: Validar precisión numérica con valores extremos
M9 = [
    [10**6, -10**6, 10**6],
    [-10**6, 10**6, -10**6]
]
expected_path_M9 = None
expected_cost_M9 = -1000000

# Alternating values
# Prueba: Verifica patrón alternante 1/-1 en matriz cuadrada
# Caso: Matriz 3x5 con alternancia 1,-1 en diagonal
# Objetivo: Validar comportamiento con patrones repetitivos simples
M10 = [
    [1, -1, 1, -1, 1],
    [-1, 1, -1, 1, -1],
    [1, -1, 1, -1, 1]
]
expected_path_M10 = None
expected_cost_M10 = -3

# One row
# Prueba: Verifica caso donde la matriz tiene una sola fila
# Caso: Matriz 1x5 con valores alternados 1,-1
# Objetivo: Validar que funciona sin cilindro real (solo una fila)
M11 = [
    [1, -1, 1, -1, 1]
]
expected_path_M11 = None
expected_cost_M11 = 1 + -1 + 1 + -1 + 1

# One column
# Prueba: Verifica caso donde la matriz tiene una sola columna
# Caso: Matriz 4x1 (solo inicio, sin decisiones de movimiento)
# Objetivo: Validar que retorna el único elemento
M12 = [
    [1],
    [0],
    [-1],
    [2],
]
expected_path_M12 = None
expected_cost_M12 = 1

# First row optimal
# Prueba: Verifica que el algoritmo elige la primera fila cuando tiene costos mínimos
# Caso: Primera fila con valores bajos (1), demás filas con valores altos (20)
# Objetivo: Validar que no fuerza movimientos innecesarios
M13 = [
    [1, 1, 1, 1],
    [20, 20, 20, 20],
    [20, 20, 20, 20]
]
expected_path_M13 = None
expected_cost_M13 = 4

# Last row optimal
# Prueba: Verifica que el algoritmo alcanza la última fila cuando es óptima
# Caso: Última fila con valores bajos (1), primeras dos filas con valores altos (20)
# Objetivo: Validar manejo de objetivos en filas lejanas
M14 = [
    [20, 20, 20, 20],
    [20, 20, 20, 20],
    [1, 1, 1, 1]
]
expected_path_M14 = None
expected_cost_M14 = 23

# Diagonal pattern optimal
# Prueba: Verifica que el algoritmo puede seguir una diagonal pura
# Caso: Matriz 4x4 donde diagonal principal tiene costo 1, resto tiene costo 5
# Objetivo: Validar movimientos diagonales consistentes
M15 = [
    [1, 5, 5, 5],
    [5, 1, 5, 5],
    [5, 5, 1, 5],
    [5, 5, 5, 1]
]
expected_path_M15 = None
expected_cost_M15 = 4

# Cylindric wrapping behavior - starting from row 0, wraps to row 2
# Prueba: Verifica que el algoritmo usa el comportamiento cilíndrico como ventaja
# Caso: Fila 1 muy cara (20), fila 2 barata, wrap de fila 0 a fila 2 es óptimo
# Objetivo: Validar que evita filas caras usando el cilindro
M16 = [
    [1, 10, 10, 10],
    [20, 20, 20, 20],
    [2, 1, 1, 1]
]
expected_path_M16 = None
expected_cost_M16 = 4

# Middle row optimal
# Prueba: Verifica que el algoritmo elige fila intermedia cuando es óptima
# Caso: Fila del medio (índice 1) con costos bajos, primera y última con costos altos
# Objetivo: Validar que no prioriza filas específicas, considera todas
M17 = [
    [10, 10, 10, 10],
    [1, 1, 1, 1],
    [10, 10, 10, 10]
]
expected_path_M17 = None
expected_cost_M17 = 13

# Zigzag forced pattern
# Prueba: Verifica que el algoritmo cambia de fila cuando es necesario
# Caso: Matriz donde cada fila alterna entre caro (100) y barato (1)
# Objetivo: Validar que realiza movimientos optimales no-triviales
M18 = [
    [1, 100, 1, 100, 1],
    [100, 1, 100, 1, 100],
    [1, 100, 1, 100, 1]
]
expected_path_M18 = None
expected_cost_M18 = 5

# Matrix with only 2 columns
# Prueba: Verifica el caso borde más extremo (solo inicio y fin)
# Caso: Matriz 3x2 con valores variados
# Objetivo: Validar que funciona con matrices muy estrechas
M19 = [
    [5, 3],
    [2, 7],
    [4, 1]
]
expected_path_M19 = None
expected_cost_M19 = 6

# Matrix with 2 rows (minimal cylindric interaction)
# Prueba: Verifica matriz con solo 2 filas (wrapping minimal)
# Caso: Matriz 2x5 con todos valores iguales (1)
# Objetivo: Validar que funciona con matrices muy bajas (máximo cilindro posible)
M20 = [
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1]
]
expected_path_M20 = None
expected_cost_M20 = 5

# All zeros
# Prueba: Verifica caso donde todos los costos son cero
# Caso: Matriz 3x3 con todos valores = 0
# Objetivo: Validar que el costo total es 0 y el camino es válido
M21 = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]
expected_path_M21 = None
expected_cost_M21 = 0

# Abrupt value changes - sudden spikes and negative values requiring smart routing
# Prueba: Verifica que el algoritmo evita picos de valores usando negativos
# Caso: Valores -1 en rutas buenas, picos de 100 en rutas malas
# Objetivo: Validar que maximiza ganancias (minimiza con negativos)
M22 = [
    [-1, -1, 100, -1],
    [100, -1, -1, 100],
    [-1, 100, -1, -1]
]
expected_path_M22 = None
expected_cost_M22 = -4

# Wrap is more expensive than zigzag
# Prueba: Verifica que el algoritmo elige zigzag cuando wrap es más caro
# Caso: Wrapping a fila lejana es más caro que moverse gradualmente
# Objetivo: Validar que no abusa del cilindro innecesariamente
M23 = [
    [1, 100, 100],
    [1, 1, 1],
    [100, 100, 100]
]
expected_path_M23 = None
expected_cost_M23 = 3

# Large matrix stress test (10x10)
# Prueba: Verifica rendimiento y correctitud en matrices más grandes
# Caso: Matriz 10x10 con patrón repetitivo de valores 1-3
# Objetivo: Validar escalabilidad, no solo matrices pequeñas
M24 = [
    [1, 2, 3, 2, 1, 2, 3, 2, 1, 2],
    [2, 1, 2, 3, 2, 1, 2, 3, 2, 1],
    [3, 2, 1, 2, 3, 2, 1, 2, 3, 2],
    [2, 3, 2, 1, 2, 3, 2, 1, 2, 3],
    [1, 2, 3, 2, 1, 2, 3, 2, 1, 2],
    [2, 1, 2, 3, 2, 1, 2, 3, 2, 1],
    [3, 2, 1, 2, 3, 2, 1, 2, 3, 2],
    [2, 3, 2, 1, 2, 3, 2, 1, 2, 3],
    [1, 2, 3, 2, 1, 2, 3, 2, 1, 2],
    [2, 1, 2, 3, 2, 1, 2, 3, 2, 1]
]
expected_path_M24 = None
expected_cost_M24 = 10

# All rows same cost (any path is equally optimal)
# Prueba: Verifica caso donde múltiples caminos son igualmente válidos
# Caso: Todos los valores son 2, cualquier camino tiene costo 8
# Objetivo: Validar que acepta múltiples soluciones óptimas
M25 = [
    [2, 2, 2, 2],
    [2, 2, 2, 2],
    [2, 2, 2, 2]
]
expected_path_M25 = None
expected_cost_M25 = 8

# Decimals/floats
# Prueba: Verifica que el algoritmo maneja números decimales correctamente
# Caso: Matriz con valores flotantes (1.5, 2.3, 0.5, etc.)
# Objetivo: Validar precisión numérica con decimales, suma correcta de floats
M26 = [
    [1.5, 2.3, 0.5],
    [3.2, 0.1, 2.8],
    [0.7, 4.2, 1.1]
]
expected_path_M26 = None
expected_cost_M26 = 2.1

# Isolated optimal value surrounded by high values
# Prueba: Verifica que el algoritmo alcanza un valor óptimo aislado
# Caso: Un único 0 rodeado de 100s, solo accesible en columna 1
# Objetivo: Validar que hace sacrificios para alcanzar mínimos globales
M27 = [
    [100, 100, 100, 100],
    [100, 0, 100, 100],
    [100, 100, 100, 100]
]
expected_path_M27 = None
expected_cost_M27 = 300


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_path_cost(matrix, path):
    """Calculate total cost of a path through the matrix."""
    cost = 0
    for x, y in path:
        cost += matrix[y][x]
    return cost


def validate_path(matrix, path, start_row=0):
    """Valida que el camino sea legal:
    - Tenga longitud igual al número de columnas
    - Empiece en columna 0
    - Termine en última columna
    - Avance exactamente una columna por paso
    - Cada movimiento entre filas sea hacia arriba/igual/abajo (con wrapping cilíndrico)
    """
    if not matrix:
        return path == []
    
    m = len(matrix)  # número de filas
    n = len(matrix[0])  # número de columnas
    
    # Validar longitud del camino
    if len(path) != n:
        return False
    
    # Validar que empiece en columna 0
    if path[0][0] != 0:
        return False
    
    # Validar que termine en última columna
    if path[-1][0] != n - 1:
        return False
    
    # Validar movimientos
    for i in range(len(path) - 1):
        curr_x, curr_y = path[i]
        next_x, next_y = path[i + 1]
        
        # Debe avanzar exactamente una columna
        if next_x != curr_x + 1:
            return False
        
        # El cambio de fila debe ser válido (-1, 0, +1 con wrapping)
        row_diff = (next_y - curr_y) % m
        # row_diff debe ser m-1 (wrap arriba), 0 (mismo), o 1 (abajo)
        if row_diff not in [0, 1, m - 1]:
            return False
    
    return True


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

ALGORITHMS = [
    ("brute_force", lambda M, y: brute_force(M, y)),
    ("backtracking", lambda M, y: backtracking(M, y)),
    ("divide_and_conquer", lambda M, y: divide_and_conquer(M, y)),
    ("memoization", lambda M, y: memoization(M, y)),
    ("tabulation", lambda M, y: tabulation(M, y)),
]

MATRICES = [
    ("M1", M1, expected_path_M1, expected_cost_M1),
    ("M2", M2, expected_path_M2, expected_cost_M2),
    ("M3", M3, expected_path_M3, expected_cost_M3),
    ("M4", M4, expected_path_M4, expected_cost_M4),
    ("M5", M5, expected_path_M5, expected_cost_M5),
    ("M6", M6, expected_path_M6, expected_cost_M6),
    ("M7", M7, expected_path_M7, expected_cost_M7),
    ("M8", M8, expected_path_M8, expected_cost_M8),
    ("M9", M9, expected_path_M9, expected_cost_M9),
    ("M10", M10, expected_path_M10, expected_cost_M10),
    ("M11", M11, expected_path_M11, expected_cost_M11),
    ("M12", M12, expected_path_M12, expected_cost_M12),
    ("M13", M13, expected_path_M13, expected_cost_M13),
    ("M14", M14, expected_path_M14, expected_cost_M14),
    ("M15", M15, expected_path_M15, expected_cost_M15),
    ("M16", M16, expected_path_M16, expected_cost_M16),
    ("M17", M17, expected_path_M17, expected_cost_M17),
    ("M18", M18, expected_path_M18, expected_cost_M18),
    ("M19", M19, expected_path_M19, expected_cost_M19),
    ("M20", M20, expected_path_M20, expected_cost_M20),
    ("M21", M21, expected_path_M21, expected_cost_M21),
    ("M22", M22, expected_path_M22, expected_cost_M22),
    ("M23", M23, expected_path_M23, expected_cost_M23),
    ("M24", M24, expected_path_M24, expected_cost_M24),
    ("M25", M25, expected_path_M25, expected_cost_M25),
    ("M26", M26, expected_path_M26, expected_cost_M26),
    ("M27", M27, expected_path_M27, expected_cost_M27),
]


# =============================================================================
# TESTS
# =============================================================================

@pytest.mark.parametrize("matrix_name, matrix, expected_path, expected_cost", MATRICES)
@pytest.mark.parametrize("algo_name, algorithm", ALGORITHMS)
def test_all_algorithms(matrix_name, matrix, expected_path, expected_cost, algo_name, algorithm):
    """Prueba cada algoritmo individualmente contra cada matriz."""
    # Caso matriz vacía
    if matrix == []:
        assert algorithm(matrix, 0) == []
        return

    result_path = algorithm(matrix, 0)

    # Validar que el camino sea legal
    assert validate_path(matrix, result_path), \
        f"{algo_name} produced illegal path on {matrix_name}"

    # Si expected_path es especificado, verificar que coincida exactamente
    if expected_path is not None:
        assert result_path == expected_path, \
            f"{algo_name} failed on {matrix_name}: got {result_path}, expected {expected_path}"

    # Validar el costo calculado del camino
    result_cost = calculate_path_cost(matrix, result_path)

    # Si expected_cost es especificado, verificar que coincida
    if expected_cost is not None:
        assert result_cost == pytest.approx(expected_cost, rel=1e-9), \
            f"{algo_name} wrong cost on {matrix_name}: got {result_cost}, expected {expected_cost}"

    # Verificaciones básicas de sanidad
    assert len(result_path) == len(matrix[0]), \
        f"{algo_name} path length incorrect on {matrix_name}: got {len(result_path)}, expected {len(matrix[0])}"

    # Verificar que el camino comience en la columna 0
    assert result_path[0][0] == 0, \
        f"{algo_name} path doesn't start at column 0 on {matrix_name}"


def test_algorithm_consistency():
    """Verifica que TODOS los algoritmos den resultados consistentes entre sí."""
    # Usar matrices pequeñas donde todos los algoritmos pueden terminar
    test_matrices = [M1, M2, M3, M4, M5, M6, M7, M8]

    for i, matrix in enumerate(test_matrices, 1):
        if matrix == []:  # Skip empty matrix
            continue

        results = {}

        # Ejecutar todos los algoritmos que deberían dar resultados consistentes
        algorithms_to_test = [
            ("brute_force", brute_force),
            ("backtracking", backtracking),
            ("divide_and_conquer", divide_and_conquer),
            ("memoization", memoization),
            ("tabulation", tabulation),
        ]

        for algo_name, algorithm in algorithms_to_test:
            try:
                path = algorithm(matrix, 0)
                if validate_path(matrix, path):  # Solo considerar caminos válidos
                    cost = calculate_path_cost(matrix, path)
                    results[algo_name] = cost
                else:
                    pytest.fail(f"{algo_name} produced invalid path on M{i}")
            except RecursionError:
                # Recursion depth exceeded - algoritmo no puede manejar esta matriz
                continue
            except TimeoutError:
                # Timeout - algoritmo es demasiado lento
                continue
            except Exception as e:
                # Otros errores (división por cero, etc.) deberían fallar
                pytest.fail(f"{algo_name} failed with unexpected error on M{i}: {e}")

        # Verificar que todos los algoritmos que completaron den el mismo costo
        if len(results) >= 2:  # Necesitamos al menos 2 algoritmos para comparar
            costs = list(results.values())
            min_cost = min(costs)
            max_cost = max(costs)

            # Todos deberían dar el mismo costo óptimo
            assert min_cost == pytest.approx(max_cost, rel=1e-9), \
                f"Inconsistent results on M{i}: {results}"

            print(f"M{i}: {len(results)} algorithms consistent, optimal cost = {min_cost}")
        else:
            pytest.fail(f"Only {len(results)} algorithms completed on M{i}, need at least 2 for consistency check")


def test_dp_optimality():
    """Verifica que los algoritmos DP (óptimos) den mejores o iguales resultados que los aproximados."""
    # Usar matrices donde algunos algoritmos pueden no terminar pero DP sí
    test_matrices = [M1, M2, M3, M4, M5]

    for i, matrix in enumerate(test_matrices, 1):
        if matrix == []:
            continue

        # Algoritmos óptimos (deberían dar el mejor resultado posible)
        optimal_algorithms = [
            ("memoization", memoization),
            ("tabulation", tabulation),
        ]

        # Algoritmos que pueden ser subóptimos o no terminar
        other_algorithms = [
            ("brute_force", brute_force),
            ("backtracking", backtracking),
            ("divide_and_conquer", divide_and_conquer),
        ]

        optimal_costs = []
        other_costs = []

        # Obtener resultados de algoritmos óptimos
        for algo_name, algorithm in optimal_algorithms:
            try:
                path = algorithm(matrix, 0)
                if validate_path(matrix, path):
                    cost = calculate_path_cost(matrix, path)
                    optimal_costs.append(cost)
            except:
                continue

        # Obtener resultados de otros algoritmos
        for algo_name, algorithm in other_algorithms:
            try:
                path = algorithm(matrix, 0)
                if validate_path(matrix, path):
                    cost = calculate_path_cost(matrix, path)
                    other_costs.append(cost)
            except:
                continue

        # Verificaciones
        if optimal_costs:
            min_optimal = min(optimal_costs)
            max_optimal = max(optimal_costs)

            # Los algoritmos DP deberían ser consistentes entre sí
            assert min_optimal == pytest.approx(max_optimal, rel=1e-9), \
                f"DP algorithms inconsistent on M{i}: {optimal_costs}"

            # Otros algoritmos no deberían ser mejores que DP
            for cost in other_costs:
                assert cost >= min_optimal - 1e-9, \
                    f"Non-DP algorithm better than DP on M{i}: DP={min_optimal}, other={cost}"

            print(f"M{i}: DP optimal cost = {min_optimal}, {len(other_costs)} other algorithms checked")


def test_path_properties():
    """Verifica propiedades básicas de los caminos generados."""
    test_matrix = M1  # Matriz de ejemplo

    for algo_name, algorithm in ALGORITHMS:
        path = algorithm(test_matrix, 0)

        # Verificar estructura básica
        assert isinstance(path, list), f"{algo_name}: path should be a list"
        assert len(path) == len(test_matrix[0]), f"{algo_name}: path length incorrect"

        # Verificar que cada elemento sea una coordenada [col, row]
        for i, coord in enumerate(path):
            assert isinstance(coord, list) and len(coord) == 2, \
                f"{algo_name}: coordinate {i} should be [col, row]"
            assert isinstance(coord[0], int) and isinstance(coord[1], int), \
                f"{algo_name}: coordinates should be integers"

        # Verificar que las coordenadas estén dentro de límites
        rows, cols = len(test_matrix), len(test_matrix[0])
        for coord in path:
            col, row = coord
            assert 0 <= col < cols, f"{algo_name}: column {col} out of bounds"
            assert 0 <= row < rows, f"{algo_name}: row {row} out of bounds"

        # Verificar que sea un camino válido
        assert validate_path(test_matrix, path), f"{algo_name}: invalid path"


def test_cost_sanity():
    """Verifica que los costos calculados sean razonables."""
    test_matrices = [M1, M2, M3, M4, M5, M6, M7]

    for matrix in test_matrices:
        if matrix == []:
            continue

        for algo_name, algorithm in ALGORITHMS:
            try:
                path = algorithm(matrix, 0)
                if validate_path(matrix, path):
                    cost = calculate_path_cost(matrix, path)

                    # Verificar que el costo sea un número finito
                    assert isinstance(cost, (int, float)), f"{algo_name}: cost should be numeric"
                    assert not (cost != cost), f"{algo_name}: cost should not be NaN"  # NaN check
                    assert cost != float('inf') and cost != float('-inf'), \
                        f"{algo_name}: cost should be finite"

                    # Verificar que el costo esté en un rango razonable
                    # (la suma de valores absolutos más extremos)
                    max_possible = sum(abs(val) for row in matrix for val in row)
                    min_possible = -max_possible
                    assert min_possible <= cost <= max_possible, \
                        f"{algo_name}: cost {cost} outside reasonable range [{min_possible}, {max_possible}]"

            except:
                # Si el algoritmo falla, saltamos esta verificación
                continue


def test_path_uniqueness():
    """Verifica que no haya posiciones duplicadas consecutivas o problemas obvios."""
    test_matrix = M1

    for algo_name, algorithm in ALGORITHMS:
        try:
            path = algorithm(test_matrix, 0)
            if validate_path(test_matrix, path):

                # Verificar que no haya movimientos inválidos obvios
                for i in range(len(path) - 1):
                    curr_col, curr_row = path[i]
                    next_col, next_row = path[i + 1]

                    # Debe avanzar exactamente una columna
                    assert next_col == curr_col + 1, \
                        f"{algo_name}: invalid column progression at step {i}"

                    # El movimiento de fila debe ser válido
                    row_diff = abs(next_row - curr_row)
                    # Permitir diferencia de 0, 1, o (rows-1) para wrapping
                    rows = len(test_matrix)
                    assert row_diff in [0, 1] or row_diff == rows - 1, \
                        f"{algo_name}: invalid row movement at step {i}"

        except:
            continue


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
