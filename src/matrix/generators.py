"""Matrix generation utilities."""

import random
import numpy as np
from typing import Callable, Tuple, List, Optional


def matrix_from_function(
    f: Callable[[float, float], float],
    x_range: Tuple[float, float],
    y_range: Tuple[float, float],
    h_x: float = 1.0,
    h_y: float = 1.0,
    round_values: bool = True
) -> List[List[float]]:
    """
    Generate a matrix from a mathematical function.
    
    Args:
        f: Function f(x, y) -> value
        x_range: Tuple (x_start, x_end)
        y_range: Tuple (y_start, y_end)
        h_x: Step size in x direction
        h_y: Step size in y direction
        round_values: Whether to round values to integers
    
    Returns:
        2D list representing the matrix
    """
    x_0, x_n = x_range
    y_0, y_m = y_range
    
    x_values = np.arange(x_0, x_n + h_x, h_x)
    y_values = np.arange(y_0, y_m + h_y, h_y)
    
    matriz = []
    for y in y_values:
        fila = []
        for x in x_values:
            valor = f(x, y)
            if round_values:
                valor = int(round(valor))
            fila.append(valor)
        matriz.append(fila)
    
    return matriz


def matrix_random(
    n_rows: int,
    n_cols: int,
    value_min: float = -10,
    value_max: float = 10,
    integers: bool = True,
    seed: Optional[int] = None
) -> List[List[float]]:
    """
    Generate a random matrix.
    
    Args:
        n_rows: Number of rows
        n_cols: Number of columns
        value_min: Minimum value
        value_max: Maximum value
        integers: Whether to use integer values
        seed: Random seed for reproducibility
    
    Returns:
        2D list representing the matrix
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    matriz = []
    for _ in range(n_rows):
        fila = []
        for _ in range(n_cols):
            if integers:
                valor = random.randint(int(value_min), int(value_max))
            else:
                valor = random.uniform(value_min, value_max)
            fila.append(valor)
        matriz.append(fila)
    
    return matriz
