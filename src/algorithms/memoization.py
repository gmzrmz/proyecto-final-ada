"""Memoization (Top-down DP) algorithm for matrix crossing."""


def _min_cost(M, movs):
    """Find index of path with minimum cost."""
    sums = [sum(M[pos[1]][pos[0]] for pos in path) for path in movs]
    return sums.index(min(sums))


def _front(M, sy):
    """Wrap row index for toroidal matrix."""
    num_rows = len(M)
    return sy % num_rows


def memoization(M, y=0):
    """
    Find optimal path using memoization (top-down dynamic programming).
    
    Args:
        M: 2D list representing the cost matrix
        y: Starting row position (0-indexed)
    
    Returns:
        List of [col, row] positions representing the optimal path
    """
    if not M or not M[0]:
        return []
    
    num_rows = len(M)
    num_cols = len(M[0])
    data = [[None for _ in range(num_cols)] for _ in range(num_rows)]
    
    def _recursive_cross(M, sx, sy):
        sy = _front(M, sy)
        
        if data[sy][sx] is not None:
            return data[sy][sx]
        
        here = [[sx, sy]]
        
        if sx == num_cols - 1:
            data[sy][sx] = here
            return here
        
        next_sx = sx + 1
        movs = [
            _recursive_cross(M, next_sx, sy - 1),
            _recursive_cross(M, next_sx, sy),
            _recursive_cross(M, next_sx, sy + 1)
        ]
        
        best_path = movs[_min_cost(M, movs)]
        data[sy][sx] = here + best_path
        
        return data[sy][sx]
    
    return _recursive_cross(M, 0, y)
