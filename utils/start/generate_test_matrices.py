#!/usr/bin/env python3
"""
Generate all test matrices and save them to files.
This ensures all algorithms test on EXACTLY the same data.

Usage:
    python generate_test_matrices.py --output ./test_matrices
    python generate_test_matrices.py --output ./test_matrices --random-seeds  # Para matrices diferentes cada vez
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Add project root to path (go up 2 levels: utils/start/ -> utils/ -> root/)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.matrix.generators import matrix_random
from src.matrix.presets import get_matrix_by_preset, MATRIX_PRESETS


def save_matrix(matrix: List[List[float]], filepath: str):
    """Save matrix to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump({
            "rows": len(matrix),
            "cols": len(matrix[0]) if matrix else 0,
            "data": matrix
        }, f)
    print(f"  Guardado: {filepath}")


def generate_complexity_matrices(output_dir: str, use_random_seeds: bool = False):
    """Generate matrices for complexity analysis."""
    print("\n=== Generando matrices para análisis de complejidad ===")
    
    # Sizes and seeds
    sizes = [5, 7, 9, 10, 11, 12, 15, 18, 20, 30, 50, 75, 100]
    
    if use_random_seeds:
        # Generate seeds based on current timestamp for uniqueness
        base_seed = int(time.time())
        seeds = [base_seed + i * 1000 for i in range(5)]
        print(f"Usando seeds aleatorios basados en la hora actual: {seeds}")
    else:
        # Fixed seeds for reproducibility
        seeds = [42, 123, 456, 789, 1011]
        print(f"Usando seeds fijos para reproducibilidad: {seeds}")
    
    complexity_dir = os.path.join(output_dir, "complexity")
    
    for size in sizes:
        for seed in seeds:
            # Only square matrices (n×n) to keep it manageable
            matrix = matrix_random(size, size, -10, 10, integers=False, seed=seed)
            
            filename = f"square_{size}x{size}_seed{seed}.json"
            filepath = os.path.join(complexity_dir, filename)
            
            save_matrix(matrix, filepath)
    
    print(f"Total de matrices de complejidad: {len(sizes) * len(seeds)}")


def generate_preset_matrices(output_dir: str, use_random_seeds: bool = False):
    """Generate preset matrices."""
    print("\n=== Generando matrices de tipo preset ===")
    
    if use_random_seeds:
        # Generate seeds based on current timestamp
        base_seed = int(time.time())
        seeds = [base_seed + i * 100 for i in range(3)]
        print(f"Usando seeds aleatorios basados en la hora actual: {seeds}")
    else:
        # Fixed seeds for reproducibility
        seeds = [42, 123, 456]
        print(f"Usando seeds fijos para reproducibilidad: {seeds}")
    
    presets_dir = os.path.join(output_dir, "presets")
    
    total = 0
    for preset_name in MATRIX_PRESETS.keys():
        for seed in seeds:
            matrix = get_matrix_by_preset(preset_name, seed=seed)
            
            filename = f"{preset_name}_seed{seed}.json"
            filepath = os.path.join(presets_dir, filename)
            
            save_matrix(matrix, filepath)
            total += 1
    
    print(f"Total de matrices preset: {total}")


def generate_manifest(output_dir: str):
    """Generate manifest file with all matrix metadata."""
    print("\n=== Generando archivo manifest ===")
    
    manifest = {
        "complexity": {
            "sizes": [5, 7, 9, 10, 11, 12, 15, 18, 20, 30, 50, 75, 100],
            "seeds": [42, 123, 456, 789, 1011],
            "shapes": ["square"],
            "total": 65  # 13 sizes × 5 seeds
        },
        "presets": {
            "types": list(MATRIX_PRESETS.keys()),
            "seeds": [42, 123, 456],
            "total": 39  # 13 presets × 3 seeds
        },
        "total_matrices": 104,
        "start_positions": [0],  # Only test from top row for simplicity
        "timeout_policy": {
            "size_5_12": 300,    # 5 minutes
            "size_13_20": 900,   # 15 minutes
            "size_21_plus": 1800 # 30 minutes
        }
    }
    
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest guardado en: {manifest_path}")
    print(f"\nTotal de matrices de prueba: {manifest['total_matrices']}")
    print(f"Por algoritmo: {manifest['total_matrices']} pruebas")
    print(f"Para los 5 algoritmos: {manifest['total_matrices'] * 5} pruebas en total")


def main():
    parser = argparse.ArgumentParser(
        description="Generate all test matrices for benchmarks"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./test_matrices",
        help="Output directory for matrices (default: ./test_matrices)"
    )
    
    parser.add_argument(
        "--random-seeds", "-r",
        action="store_true",
        help="Use random seeds based on timestamp (generates different matrices each time)"
    )
    
    args = parser.parse_args()
    
    print(f"Generando matrices de prueba en: {args.output}")
    if args.random_seeds:
        print("Usando seeds aleatorios - las matrices serán diferentes cada vez")
    else:
        print("Usando seeds fijos - las matrices serán reproducibles")
    print("=" * 60)
    
    # Generate all matrices
    generate_complexity_matrices(args.output, args.random_seeds)
    generate_preset_matrices(args.output, args.random_seeds)
    generate_manifest(args.output)
    
    print("\n" + "=" * 60)
    print("[OK] ¡Todas las matrices de prueba se generaron correctamente!")
    print(f"[OK] Ubicación: {args.output}")
    print("\nPróximos pasos:")
    print("1. Sube las matrices a S3 o compártelas con todas las instancias EC2")
    print("2. Ejecuta los benchmarks con: python run_benchmark.py --matrices-dir ./test_matrices")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
