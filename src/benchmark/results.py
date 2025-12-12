"""Benchmark results handling and export."""

import json
import csv
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Single benchmark result."""
    algorithm: str
    matrix_type: str
    matrix_rows: int
    matrix_cols: int
    start_position: int
    execution_time_seconds: float
    path: List[List[int]]
    path_cost: float
    timestamp: str
    instance_id: Optional[str] = None  # For AWS EC2 identification
    timed_out: bool = False  # True if benchmark exceeded timeout
    error_message: Optional[str] = None  # Error description if any
    peak_memory_kb: Optional[float] = None  # Peak memory usage in KB (2 decimal precision)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def save_results(
    results: List[BenchmarkResult],
    output_dir: str,
    format: str = "json",
    filename_prefix: str = "benchmark"
) -> str:
    """
    Save benchmark results to file.
    
    Args:
        results: List of BenchmarkResult objects
        output_dir: Output directory path
        format: Output format ('json' or 'csv')
        filename_prefix: Prefix for the output filename
    
    Returns:
        Path to the saved file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_results": len(results),
            },
            "results": [r.to_dict() for r in results]
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    elif format == "csv":
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        if not results:
            return filepath
        
        fieldnames = [
            "algorithm", "matrix_type", "matrix_rows", "matrix_cols",
            "start_position", "execution_time_seconds", "path_cost",
            "timestamp", "instance_id", "timed_out", "error_message", "peak_memory_kb"
        ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for r in results:
                row = r.to_dict()
                row.pop("path")  # Don't include path in CSV (too long)
                writer.writerow(row)
    
    else:
        raise ValueError(f"Unknown format: {format}")
    
    return filepath


def load_results(filepath: str) -> List[BenchmarkResult]:
    """
    Load benchmark results from file.
    
    Args:
        filepath: Path to the results file (JSON only)
    
    Returns:
        List of BenchmarkResult objects
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    results = []
    for r in data["results"]:
        results.append(BenchmarkResult(**r))
    
    return results


def merge_results(filepaths: List[str], output_path: str) -> str:
    """
    Merge multiple result files into one.
    
    Args:
        filepaths: List of paths to result files
        output_path: Path for merged output
    
    Returns:
        Path to merged file
    """
    all_results = []
    
    for fp in filepaths:
        results = load_results(fp)
        all_results.extend(results)
    
    # Sort by algorithm and matrix type
    all_results.sort(key=lambda r: (r.algorithm, r.matrix_type, r.matrix_rows))
    
    return save_results(all_results, os.path.dirname(output_path), 
                       filename_prefix=os.path.basename(output_path).replace(".json", ""))
