"""Backtracking with Branch & Bound algorithm for matrix crossing."""


def backtracking_cross(matriz, y=0):
    """
    Find optimal path using backtracking with pruning (branch & bound).
    
    More efficient than brute force due to pruning of suboptimal branches.
    
    Args:
        matriz: 2D list representing the cost matrix
        y: Starting row position (0-indexed)
    
    Returns:
        List of [col, row] positions representing the optimal path
    """
    if not matriz or not matriz[0]:
        return []
    
    m = len(matriz)
    n = len(matriz[0])
    mejor_costo = float('inf')
    mejor_camino = []

    def obtener_vecinos(fila, col):
        if col >= n - 1:
            return []
        vecinos = []
        vecinos.append((fila - 1) % m)
        vecinos.append(fila)
        vecinos.append((fila + 1) % m)
        return vecinos

    def buscar_exhaustivo(fila_actual, col_actual, costo_actual, camino_actual):
        nonlocal mejor_costo, mejor_camino
        
        if col_actual == n - 1:
            if costo_actual < mejor_costo:
                mejor_costo = costo_actual
                mejor_camino = camino_actual.copy()
            return
        
        # PRUNING: skip branch if already worse than best known solution
        if costo_actual >= mejor_costo:
            return
        
        for siguiente_fila in obtener_vecinos(fila_actual, col_actual):
            siguiente_col = col_actual + 1
            siguiente_costo = costo_actual + matriz[siguiente_fila][siguiente_col]
            camino_actual.append([siguiente_col, siguiente_fila])
            buscar_exhaustivo(siguiente_fila, siguiente_col, siguiente_costo, camino_actual)
            camino_actual.pop()

    costo_inicial = matriz[y][0]
    camino_inicial = [[0, y]]
    buscar_exhaustivo(y, 0, costo_inicial, camino_inicial)
    
    return mejor_camino
