"""Predefined matrix configurations for benchmarking."""

import numpy as np
from typing import Dict, Any, List
from .generators import matrix_from_function, matrix_random


def create_random_matrix(
    rows: int = 7,
    cols: int = 15,
    value_min: float = -50,
    value_max: float = 50,
    integers: bool = False,
    seed: int = None
) -> List[List[float]]:
    """Create a random matrix with specified parameters."""
    return matrix_random(rows, cols, value_min, value_max, integers, seed)


def create_wavy_matrix(
    x_range: tuple = (0, 12),
    y_range: tuple = (0, 8),
    h_x: float = 1.0,
    h_y: float = 1.0,
    amplitude: float = 10,
    offset: float = 15
) -> List[List[float]]:
    """Create a wavy matrix using sine/cosine functions."""
    f = lambda x, y: amplitude * np.sin(x/2) * np.cos(y/2) + offset
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


def create_turbulent_matrix(
    x_range: tuple = (-10, 10),
    y_range: tuple = (-8, 8),
    h_x: float = 1.5,
    h_y: float = 1.5
) -> List[List[float]]:
    """Create a turbulent matrix with multiple oscillations."""
    f = lambda x, y: 10*np.sin(x) + 8*np.cos(y*1.5) + 5*np.sin(x*y/10) + 20
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


def create_gaussian_matrix(
    x_range: tuple = (0, 12),
    y_range: tuple = (0, 5),
    h_x: float = 1.0,
    h_y: float = 1.0
) -> List[List[float]]:
    """Create a matrix with Gaussian peaks."""
    f = lambda x, y: (
        20 * np.exp(-((x-4)**2 + (y-3)**2)/10) +
        15 * np.exp(-((x-8)**2 + (y-2)**2)/8)
    )
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


def create_valley_matrix(
    x_range: tuple = (0, 10),
    y_range: tuple = (0, 6),
    h_x: float = 1.0,
    h_y: float = 1.0
) -> List[List[float]]:
    """Create a matrix with a valley pattern."""
    f = lambda x, y: abs(y - 3) * 5 + x
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


def create_paraboloid_matrix(
    x_range: tuple = (0, 10),
    y_range: tuple = (0, 6),
    h_x: float = 1.0,
    h_y: float = 1.0
) -> List[List[float]]:
    """Create a paraboloid surface matrix."""
    f = lambda x, y: (x - 5)**2 + (y - 3)**2
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


def create_inclined_plane_matrix(
    x_range: tuple = (0, 8),
    y_range: tuple = (0, 5),
    h_x: float = 1.0,
    h_y: float = 1.0
) -> List[List[float]]:
    """Create an inclined plane matrix."""
    f = lambda x, y: x + 2*y
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


def create_checkerboard_matrix(
    x_range: tuple = (0, 10),
    y_range: tuple = (0, 6),
    h_x: float = 1.0,
    h_y: float = 1.0
) -> List[List[float]]:
    """Create a checkerboard pattern matrix."""
    f = lambda x, y: ((int(x) % 2) ^ (int(y) % 2)) * 20
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


def create_stairs_matrix(
    x_range: tuple = (0, 12),
    y_range: tuple = (0, 6),
    h_x: float = 1.0,
    h_y: float = 1.0
) -> List[List[float]]:
    """Create a stairs/steps pattern matrix."""
    f = lambda x, y: int(x/3) * 10 + int(y/2) * 5
    return matrix_from_function(f, x_range, y_range, h_x, h_y)


# Preset configurations for benchmarks
MATRIX_PRESETS: Dict[str, Dict[str, Any]] = {
    "random_small": {
        "type": "random",
        "params": {"rows": 7, "cols": 15, "value_min": -50, "value_max": 50, "integers": False}
    },
    "random_medium": {
        "type": "random",
        "params": {"rows": 10, "cols": 20, "value_min": -100, "value_max": 100, "integers": False}
    },
    "random_large": {
        "type": "random",
        "params": {"rows": 15, "cols": 30, "value_min": -100, "value_max": 100, "integers": False}
    },
    "wavy_small": {
        "type": "wavy",
        "params": {"x_range": (0, 12), "y_range": (0, 8), "h_x": 1.0, "h_y": 1.0}
    },
    "wavy_medium": {
        "type": "wavy",
        "params": {"x_range": (0, 20), "y_range": (0, 15), "h_x": 0.75, "h_y": 0.75}
    },
    "turbulent_small": {
        "type": "turbulent",
        "params": {"x_range": (-10, 10), "y_range": (-8, 8), "h_x": 1.5, "h_y": 1.5}
    },
    "turbulent_medium": {
        "type": "turbulent",
        "params": {"x_range": (-15, 15), "y_range": (-12, 12), "h_x": 1.0, "h_y": 1.0}
    },
    "gaussian_small": {
        "type": "gaussian",
        "params": {"x_range": (0, 12), "y_range": (0, 5), "h_x": 1.0, "h_y": 1.0}
    },
    "valley_small": {
        "type": "valley",
        "params": {"x_range": (0, 10), "y_range": (0, 6), "h_x": 1.0, "h_y": 1.0}
    },
    "paraboloid_small": {
        "type": "paraboloid",
        "params": {"x_range": (0, 10), "y_range": (0, 6), "h_x": 1.0, "h_y": 1.0}
    },
    "inclined_plane_small": {
        "type": "inclined_plane",
        "params": {"x_range": (0, 8), "y_range": (0, 5), "h_x": 1.0, "h_y": 1.0}
    },
    "checkerboard_small": {
        "type": "checkerboard",
        "params": {"x_range": (0, 10), "y_range": (0, 6), "h_x": 1.0, "h_y": 1.0}
    },
    "stairs_small": {
        "type": "stairs",
        "params": {"x_range": (0, 12), "y_range": (0, 6), "h_x": 1.0, "h_y": 1.0}
    },
}


def get_matrix_by_preset(preset_name: str, seed: int = None) -> List[List[float]]:
    """
    Get a matrix by preset name.
    
    Args:
        preset_name: Name of the preset from MATRIX_PRESETS
        seed: Random seed (only for random matrices)
    
    Returns:
        Generated matrix
    
    Raises:
        ValueError: If preset_name is not found
    """
    if preset_name not in MATRIX_PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    preset = MATRIX_PRESETS[preset_name]
    matrix_type = preset["type"]
    params = preset["params"].copy()
    
    if matrix_type == "random":
        if seed is not None:
            params["seed"] = seed
        return create_random_matrix(**params)
    elif matrix_type == "wavy":
        return create_wavy_matrix(**params)
    elif matrix_type == "turbulent":
        return create_turbulent_matrix(**params)
    elif matrix_type == "gaussian":
        return create_gaussian_matrix(**params)
    elif matrix_type == "valley":
        return create_valley_matrix(**params)
    elif matrix_type == "paraboloid":
        return create_paraboloid_matrix(**params)
    elif matrix_type == "inclined_plane":
        return create_inclined_plane_matrix(**params)
    elif matrix_type == "checkerboard":
        return create_checkerboard_matrix(**params)
    elif matrix_type == "stairs":
        return create_stairs_matrix(**params)
    else:
        raise ValueError(f"Unknown matrix type: {matrix_type}")
