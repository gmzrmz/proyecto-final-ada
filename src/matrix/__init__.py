"""
Módulo para generación de matrices
"""

from .generators import matrix_from_function, matrix_random
from .presets import (
    create_wavy_matrix,
    create_turbulent_matrix,
    create_gaussian_matrix,
    create_valley_matrix,
    create_paraboloid_matrix,
    create_inclined_plane_matrix,
    create_checkerboard_matrix,
    create_stairs_matrix,
    MATRIX_PRESETS,
    get_matrix_by_preset,
)

__all__ = [
    "matrix_from_function",
    "matrix_random",
    "create_wavy_matrix",
    "create_turbulent_matrix",
    "create_gaussian_matrix",
    "create_valley_matrix",
    "create_paraboloid_matrix",
    "create_inclined_plane_matrix",
    "create_checkerboard_matrix",
    "create_stairs_matrix",
    "MATRIX_PRESETS",
    "get_matrix_by_preset",
]
