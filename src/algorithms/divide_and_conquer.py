"""Divide & Conquer algorithm for matrix crossing (no memoization)."""


def _min_cost(M, movs):
    """Find index of path with minimum cost."""
    sums = [sum(M[pos[1]][pos[0]] for pos in path) for path in movs]
    return sums.index(min(sums))


def _front(M, sy):
    """Wrap row index for toroidal matrix."""
    num_rows = len(M)
    return sy % num_rows


def divide_and_conquer(M, y=0):
    """
    Find optimal path using divide & conquer approach (no memoization).
    
    Warning: Exponential time complexity O(3^n) due to overlapping subproblems.
    
    Args:
        M: 2D list representing the cost matrix
        y: Starting row position (0-indexed)
    
    Returns:
        List of [col, row] positions representing the optimal path
    """
    if not M or not M[0]:
        return []
    
    def _recursive_cross_impl(M, sx, sy):
        sy = _front(M, sy)
        here = [[sx, sy]]
        sx = sx + 1
        
        if sx == len(M[0]):
            return here
        
        movs = [
            _recursive_cross_impl(M, sx, sy - 1),
            _recursive_cross_impl(M, sx, sy),
            _recursive_cross_impl(M, sx, sy + 1)
        ]
        
        return here + movs[_min_cost(M, movs)]
    
    return _recursive_cross_impl(M, 0, y)
