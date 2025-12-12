"""Brute Force (Pure Exhaustive) algorithm for matrix crossing."""


def brute_force(matriz, y=0):
    """
    Find optimal path using pure brute force search.
    Explores ALL possible paths (3^(n-1)) without any pruning/optimization.
    
    WARNING: Extremely slow. Only use for small matrices (< 10 columns).
    
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

    def vecinos(fila, col):
        """Get valid next row positions (with toroidal wrapping)."""
        if col >= n - 1:
            return []
        return [(fila - 1) % m, fila, (fila + 1) % m]

    def buscar(fila, col, costo, camino):
        """Explore all paths without pruning."""
        nonlocal mejor_costo, mejor_camino
        
        if col == n - 1:
            # Reached end of matrix
            if costo < mejor_costo:
                mejor_costo = costo
                mejor_camino = camino.copy()
            return
        
        # NO PRUNING - explores all branches regardless of cost
        for nf in vecinos(fila, col):
            nc = col + 1
            ncosto = costo + matriz[nf][nc]
            camino.append([nc, nf])
            buscar(nf, nc, ncosto, camino)
            camino.pop()

    costo_inicial = matriz[y][0]
    camino_inicial = [[0, y]]
    buscar(y, 0, costo_inicial, camino_inicial)
    
    return mejor_camino
