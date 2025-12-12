"""Tabulation (Bottom-up Dynamic Programming) algorithm for matrix crossing."""


def tabulation(M, y=0):
    """
    Find optimal path using tabulation (bottom-up dynamic programming).
    
    Args:
        M: 2D list representing the cost matrix
        y: Starting row position (0-indexed)
    
    Returns:
        List of [col, row] positions representing the optimal path
    """
    if not M or not M[0]:
        return []
    
    h = len(M)
    w = len(M[0])
    inf = float("inf")
    path = [[0, y]]
    row = y
    
    # Initialize costs table
    costs = [[inf for _ in range(w)] for _ in range(h)]
    
    # Base case: last column
    for j in range(h):
        costs[j][-1] = M[j][-1]
    
    # Fill costs table from right to left
    for i in range(w - 2, -1, -1):
        for j in range(h):
            y_up = h - 1 if j == 0 else j - 1
            y_down = 0 if j == h - 1 else j + 1
            costs[j][i] = M[j][i] + min(
                costs[y_up][i + 1],
                costs[j][i + 1],
                costs[y_down][i + 1]
            )
    
    # Reconstruct path from left to right
    for i in range(w - 1):
        y_up = h - 1 if row == 0 else row - 1
        y_down = 0 if row == h - 1 else row + 1
        
        neighbors = [[i + 1, y_up], [i + 1, row], [i + 1, y_down]]
        cost = [costs[y_up][i + 1], costs[row][i + 1], costs[y_down][i + 1]]
        
        min_path = cost.index(min(cost))
        row = neighbors[min_path][1]
        path.append(neighbors[min_path])
    
    return path
