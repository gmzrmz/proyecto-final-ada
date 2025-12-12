"""Benchmark runner for algorithm testing."""

import time
import os
import tracemalloc
from multiprocessing import Process, Queue
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

from ..algorithms import ALGORITHMS
from ..matrix.presets import get_matrix_by_preset, MATRIX_PRESETS
from ..matrix.generators import matrix_random
from .results import BenchmarkResult, save_results


def run_algorithm_in_process(queue: Queue, algorithm: Callable, matrix: List[List[float]], start_position: int) -> None:
    """
    Run algorithm in a separate process for memory measurement.
    
    Args:
        queue: Queue to put results
        algorithm: Algorithm function to run
        matrix: Cost matrix
        start_position: Starting position
    """
    try:
        # Start memory tracing
        tracemalloc.start()
        
        path = algorithm(matrix, start_position)
        
        # Get peak memory usage
        current, peak = tracemalloc.get_traced_memory()
        peak_memory_kb = peak / 1024  # Convert to KB
        
        # Stop memory tracing
        tracemalloc.stop()
        
        queue.put({
            "path": path, 
            "error": None, 
            "peak_memory_kb": peak_memory_kb
        })
    except Exception as e:
        # Make sure to stop tracemalloc even if there's an error
        try:
            tracemalloc.stop()
        except:
            pass
        queue.put({
            "path": None, 
            "error": str(e), 
            "peak_memory_kb": None
        })


def calculate_path_cost(matrix: List[List[float]], path: List[List[int]]) -> float:
    """Calculate the total cost of a path through the matrix."""
    return sum(matrix[pos[1]][pos[0]] for pos in path)


def get_adaptive_timeout(matrix_size: int) -> float:
    """
    Get adaptive timeout based on matrix size.
    
    Args:
        matrix_size: Maximum dimension of matrix (rows or cols)
    
    Returns:
        Timeout in seconds
    """
    if matrix_size <= 12:
        return 60.0  # 1 minute for small matrices
    elif matrix_size <= 20:
        return 120.0  # 2 minutes for medium matrices
    elif matrix_size <= 50:
        return 180.0  # 3 minutes for medium-large matrices
    else:
        return 240.0  # 4 minutes for large matrices


class BenchmarkRunner:
    """
    Runs benchmarks for a single algorithm across multiple matrix configurations.
    Designed to run on individual EC2 instances.
    """
    
    def get_available_matrix_files(self, subdir: str) -> Dict[str, List[str]]:
        """
        Get available matrix files from the matrices directory.
        
        Args:
            subdir: Subdirectory name ('presets' or 'complexity')
            
        Returns:
            Dict mapping preset names or sizes to list of available seed files
        """
        if not self.matrices_dir:
            return {}
        
        matrix_dir = os.path.join(self.matrices_dir, subdir)
        if not os.path.exists(matrix_dir):
            return {}
        
        files = {}
        for filename in os.listdir(matrix_dir):
            if filename.endswith('.json'):
                if subdir == 'presets':
                    # Parse preset files: preset_name_seedXXXX.json
                    parts = filename.replace('.json', '').split('_seed')
                    if len(parts) == 2:
                        preset_name = parts[0]
                        if preset_name not in files:
                            files[preset_name] = []
                        files[preset_name].append(filename)
                elif subdir == 'complexity':
                    # Parse complexity files: square_SIZE_seedXXXX.json
                    parts = filename.replace('.json', '').split('_seed')
                    if len(parts) == 2 and parts[0].startswith('square_'):
                        # Extract size from square_SIZExSIZE format
                        size_part = parts[0].replace('square_', '')
                        if 'x' in size_part:
                            size = int(size_part.split('x')[0])  # Take first dimension
                        else:
                            size = int(size_part)
                        if size not in files:
                            files[size] = []
                        files[size].append(filename)
        
        return files
    
    def __init__(
        self,
        algorithm_name: str,
        instance_id: Optional[str] = None,
        output_dir: str = "./results",
        timeout_seconds: float = 60.0,  # 1 minute default
        matrices_dir: Optional[str] = None  # Directory with pre-generated matrices
    ):
        """
        Initialize benchmark runner.
        
        Args:
            algorithm_name: Name of algorithm to test ('exhaustive', 'recursive', 
                           'memoization', or 'dynamic')
            instance_id: EC2 instance identifier (optional)
            output_dir: Directory for output files
            timeout_seconds: Maximum time allowed per benchmark (default: 300s)
        """
        if algorithm_name not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm_name}. "
                           f"Available: {list(ALGORITHMS.keys())}")
        
        self.algorithm_name = algorithm_name
        self.algorithm = ALGORITHMS[algorithm_name]
        self.instance_id = instance_id or os.environ.get("EC2_INSTANCE_ID", "local")
        self.output_dir = output_dir
        self.timeout_seconds = timeout_seconds
        self.matrices_dir = matrices_dir
        self.results: List[BenchmarkResult] = []
    
    def load_matrix_from_file(self, filepath: str) -> List[List[float]]:
        """Load matrix from JSON file."""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data["data"]
    
    def run_single(
        self,
        matrix: List[List[float]],
        matrix_type: str,
        start_position: int,
        timeout: Optional[float] = None,
        use_adaptive_timeout: bool = True
    ) -> BenchmarkResult:
        """
        Run a single benchmark with timeout support using multiprocessing.
        
        Args:
            matrix: The cost matrix
            matrix_type: Description of matrix type
            start_position: Starting row position
            timeout: Override default timeout (seconds)
            use_adaptive_timeout: Use adaptive timeout based on matrix size
        
        Returns:
            BenchmarkResult object
        """
        if use_adaptive_timeout and timeout is None:
            matrix_size = max(len(matrix), len(matrix[0]) if matrix else 0)
            timeout = get_adaptive_timeout(matrix_size)
        elif timeout is None:
            timeout = self.timeout_seconds
        
        # Use multiprocessing to enable actual timeout
        result_queue = Queue()
        
        time_start = time.perf_counter()
        process = Process(target=run_algorithm_in_process, args=(result_queue, self.algorithm, matrix, start_position))
        process.start()
        process.join(timeout=timeout)
        time_end = time.perf_counter()
        
        execution_time = time_end - time_start
        
        # Check if timeout occurred
        timed_out = False
        error_message = None
        path = []
        peak_memory_kb = None
        
        if process.is_alive():
            # Process timed out
            process.terminate()
            process.join(timeout=5)  # Wait up to 5s for graceful termination
            if process.is_alive():
                process.kill()  # Force kill if still alive
            timed_out = True
            error_message = f"Timeout after {timeout}s"
            path = []
            path_cost = 0.0
        else:
            # Process completed
            if not result_queue.empty():
                result_data = result_queue.get()
                path = result_data["path"] if result_data["path"] else []
                error_message = result_data["error"]
                path_cost = calculate_path_cost(matrix, path) if path else 0.0
                peak_memory_kb = result_data.get("peak_memory_kb")
                # Round to 2 decimal places if we have memory data
                if peak_memory_kb is not None:
                    peak_memory_kb = round(peak_memory_kb, 2)
            else:
                # Process exited without putting result (crashed)
                path = []
                path_cost = 0.0
                error_message = "Process crashed without returning result"
        
        result = BenchmarkResult(
            algorithm=self.algorithm_name,
            matrix_type=matrix_type,
            matrix_rows=len(matrix),
            matrix_cols=len(matrix[0]) if matrix else 0,
            start_position=start_position,
            execution_time_seconds=execution_time,
            path=path,
            path_cost=path_cost,
            timestamp=datetime.now().isoformat(),
            instance_id=self.instance_id,
            timed_out=timed_out,
            error_message=error_message,
            peak_memory_kb=peak_memory_kb
        )
        
        self.results.append(result)
        return result
    
    def run_preset_benchmarks(
        self,
        preset_names: Optional[List[str]] = None,
        seeds: List[int] = None,
        start_positions: Optional[List[int]] = None
    ) -> List[BenchmarkResult]:
        """
        Run benchmarks on preset matrix configurations.
        Uses pre-generated matrices if matrices_dir is set.
        
        Args:
            preset_names: List of preset names to test (None = all)
            seeds: Random seeds for reproducibility (None = [42,123,456])
            start_positions: Starting positions to test (None = [0] only)
        
        Returns:
            List of BenchmarkResult objects
        """
        if preset_names is None:
            preset_names = list(MATRIX_PRESETS.keys())
        
        # Get available matrix files if using pre-generated matrices
        available_files = {}
        if self.matrices_dir:
            available_files = self.get_available_matrix_files('presets')
            if available_files:
                # Use only presets that have available files
                preset_names = [p for p in preset_names if p in available_files]
        
        for preset_name in preset_names:
            # Get available seeds for this preset
            if self.matrices_dir and available_files:
                seed_files = available_files.get(preset_name, [])
                if not seed_files:
                    continue
                # Extract seed numbers from filenames
                current_seeds = []
                for filename in seed_files:
                    parts = filename.replace('.json', '').split('_seed')
                    if len(parts) == 2:
                        try:
                            seed = int(parts[1])
                            current_seeds.append(seed)
                        except ValueError:
                            continue
                current_seeds.sort()  # Sort for consistency
            else:
                # Fallback to hardcoded seeds if not using pre-generated matrices
                current_seeds = seeds if seeds is not None else [42, 123, 456]
            
            for seed in current_seeds:
                # Load or generate matrix
                if self.matrices_dir and available_files:
                    # Use the actual filename from available files
                    filename = f"{preset_name}_seed{seed}.json"
                    filepath = os.path.join(self.matrices_dir, "presets", filename)
                    matrix = self.load_matrix_from_file(filepath)
                else:
                    matrix = get_matrix_by_preset(preset_name, seed=seed)
                
                if start_positions is None:
                    positions = [0]  # Only test from top row
                else:
                    positions = start_positions
                
                for start_pos in positions:
                    print(f"  {preset_name} (semilla={seed}, inicio={start_pos}): ", end="", flush=True)
                    result = self.run_single(
                        matrix=matrix,
                        matrix_type=f"{preset_name}_seed{seed}",
                        start_position=start_pos,
                        use_adaptive_timeout=True
                    )
                    if result.timed_out:
                        print(f"TIMEOUT ({result.execution_time_seconds:.1f}s)")
                    elif result.error_message:
                        print(f"ERROR: {result.error_message}")
                    else:
                        print(f"{result.execution_time_seconds:.4f}s")
        
        return self.results
    
    def run_complexity_analysis(
        self,
        sizes: Optional[List[int]] = None,
        seeds: Optional[List[int]] = None
    ) -> List[BenchmarkResult]:
        """
        Run complexity analysis with increasing matrix sizes.
        Uses pre-generated matrices if matrices_dir is set.
        
        Args:
            sizes: List of matrix sizes to test (None = [5,7,9,10,11,12,15,18,20,30,50,75,100])
            seeds: Random seeds for reproducibility (None = [42,123,456,789,1011])
        
        Returns:
            List of BenchmarkResult objects
        """
        if sizes is None:
            sizes = [5, 7, 9, 10, 11, 12, 15, 18, 20, 30, 50, 75, 100]
        
        # Get available matrix files if using pre-generated matrices
        available_files = {}
        if self.matrices_dir:
            available_files = self.get_available_matrix_files('complexity')
            if available_files:
                # Use only sizes that have available files
                sizes = [s for s in sizes if s in available_files]
        
        for size in sizes:
            # Get available seeds for this size
            if self.matrices_dir and available_files:
                seed_files = available_files.get(size, [])
                if not seed_files:
                    continue
                # Extract seed numbers from filenames
                current_seeds = []
                for filename in seed_files:
                    parts = filename.replace('.json', '').split('_seed')
                    if len(parts) == 2:
                        try:
                            seed = int(parts[1])
                            current_seeds.append(seed)
                        except ValueError:
                            continue
                current_seeds.sort()  # Sort for consistency
            else:
                # Fallback to hardcoded seeds if not using pre-generated matrices
                current_seeds = seeds if seeds is not None else [42, 123, 456, 789, 1011]
        
        for size in sizes:
            for seed in current_seeds:
                # Load or generate square matrix (n×n)
                if self.matrices_dir and available_files:
                    # Use the actual filename from available files
                    filename = f"square_{size}x{size}_seed{seed}.json"
                    filepath = os.path.join(self.matrices_dir, "complexity", filename)
                    matrix = self.load_matrix_from_file(filepath)
                else:
                    matrix = matrix_random(size, size, -10, 10, integers=False, seed=seed)
                
                print(f"  {size}×{size} (semilla={seed}): ", end="", flush=True)
                result = self.run_single(
                    matrix=matrix,
                    matrix_type=f"square_{size}x{size}_seed{seed}",
                    start_position=0,
                    use_adaptive_timeout=True
                )
                if result.timed_out:
                    print(f"TIMEOUT ({result.execution_time_seconds:.1f}s)")
                elif result.error_message:
                    print(f"ERROR")
                else:
                    print(f"{result.execution_time_seconds:.4f}s")
        
        return self.results
    
    def save(self, format: str = "json") -> str:
        """
        Save all results to file.
        
        Args:
            format: Output format ('json' or 'csv')
        
        Returns:
            Path to saved file
        """
        return save_results(
            results=self.results,
            output_dir=self.output_dir,
            format=format,
            filename_prefix=f"benchmark_{self.algorithm_name}"
        )
    
    def clear_results(self):
        """Clear stored results."""
        self.results = []
