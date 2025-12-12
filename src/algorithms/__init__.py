from .brute_force import brute_force
from .backtracking import backtracking
from .divide_and_conquer import divide_and_conquer
from .memoization import memoization
from .tabulation import tabulation

ALGORITHMS = {
    "brute_force": brute_force,
    "backtracking": backtracking,
    "divide_and_conquer": divide_and_conquer,
    "memoization": memoization,
    "tabulation": tabulation,
}

__all__ = [
    "brute_force",
    "backtracking",
    "divide_and_conquer", 
    "memoization",
    "tabulation",
    "ALGORITHMS",
]
