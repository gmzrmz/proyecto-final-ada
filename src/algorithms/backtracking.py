"""Backtracking with Branch & Bound algorithm for matrix crossing."""


def backtracking(matriz, y=0):
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
    rows = len(matriz)
    cols = len(matriz[0])
    
    min_val = float('inf')
    for row in matriz:
        for val in row:
            if val < min_val:
                min_val = val
    
    offset = abs(min_val)
    matriz_pos = []
    for row in matriz:
        new_row = []
        for val in row:
            new_row.append(val + offset)
        matriz_pos.append(new_row)
    
    best_cost = float('inf')
    best_path = []

    def obtener_vecinos(row, col):
        if col >= cols - 1:
            return []
        return [(row - 1) % rows, row, (row + 1) % rows]

    def buscar_exhaustivo(cur_row, cur_col, cur_cost, cur_path):
        nonlocal best_cost, best_path
        if cur_col == cols - 1:
            if cur_cost < best_cost:
                best_cost = cur_cost
                best_path = cur_path.copy()
            return
        if cur_cost >= best_cost:
            return
        for next_row in obtener_vecinos(cur_row, cur_col):
            next_col = cur_col + 1
            next_cost = cur_cost + matriz_pos[next_row][next_col]
            cur_path.append([next_col, next_row])
            buscar_exhaustivo(next_row, next_col, next_cost, cur_path)
            cur_path.pop()

    initial_cost = matriz_pos[y][0]
    initial_path = [[0, y]]
    buscar_exhaustivo(y, 0, initial_cost, initial_path)
    return best_path
