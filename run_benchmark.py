#!/usr/bin/env python3
"""
Main entry point for running benchmarks.
Designed to be executed on EC2 instances.

Usage:
    python run_benchmark.py --algorithm brute_force
    python run_benchmark.py --algorithm tabulation --complexity-only --sizes 5 10 20 50
    python run_benchmark.py --algorithm memoization --timeout 600
"""

import argparse
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.benchmark import BenchmarkRunner


def get_instance_id() -> str:
    """Get EC2 instance ID or fallback to hostname."""
    # Try to get EC2 instance ID from metadata
    try:
        import urllib.request
        url = "http://169.254.169.254/latest/meta-data/instance-id"
        req = urllib.request.Request(url, headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"})
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read().decode()
    except:
        pass
    
    # Fallback to hostname
    import socket
    return socket.gethostname()


def main():
    parser = argparse.ArgumentParser(
        description="Run algorithm benchmarks with comprehensive testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run full benchmark suite (presets + complexity analysis)
    python run_benchmark.py --algorithm brute_force
    
    # Run only complexity analysis with custom sizes
    python run_benchmark.py --algorithm tabulation --complexity-only --sizes 10 20 50 100
    
    # Run only preset benchmarks
    python run_benchmark.py --algorithm memoization --presets-only
    
    # Custom timeout for slow algorithms
    python run_benchmark.py --algorithm backtracking --timeout 600
        """
    )
    
    parser.add_argument(
        "--algorithm", "-a",
        required=True,
        choices=["brute_force", "backtracking", "divide_and_conquer", "memoization", "tabulation"],
        help="Algorithm to benchmark"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./results",
        help="Output directory for results (default: ./results)"
    )
    
    parser.add_argument(
        "--complexity-only",
        action="store_true",
        help="Run only complexity analysis"
    )
    
    parser.add_argument(
        "--presets-only",
        action="store_true",
        help="Run only preset matrix benchmarks"
    )
    
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=None,
        help="Specific matrix sizes for complexity analysis (e.g., --sizes 5 10 20 50)"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Timeout per benchmark in seconds (default: 300 = 5 minutes)"
    )
    
    parser.add_argument(
        "--matrices-dir",
        type=str,
        default=None,
        help="Directory with pre-generated test matrices (enables reproducibility)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    
    args = parser.parse_args()
    
    # Validate options
    if args.complexity_only and args.presets_only:
        parser.error("Cannot use both --complexity-only and --presets-only")
    
    # Get instance ID
    instance_id = get_instance_id()
    print(f"Instance ID: {instance_id}")
    print(f"Algorithm: {args.algorithm}")
    print(f"Output directory: {args.output}")
    print(f"Timeout: {args.timeout}s")
    print("-" * 50)
    
    # Create runner
    runner = BenchmarkRunner(
        algorithm_name=args.algorithm,
        instance_id=instance_id,
        output_dir=args.output,
        timeout_seconds=args.timeout,
        matrices_dir=args.matrices_dir
    )
    
    # Run benchmarks
    if args.complexity_only:
        sizes_str = f"custom {args.sizes}" if args.sizes else "default"
        print(f"Running complexity analysis (sizes: {sizes_str})...")
        runner.run_complexity_analysis(sizes=args.sizes)
    elif args.presets_only:
        print("Running preset benchmarks...")
        runner.run_preset_benchmarks()
    else:
        print("Running full benchmark suite...")
        print("\n=== PRESET BENCHMARKS ===")
        runner.run_preset_benchmarks()
        print("\n=== COMPLEXITY ANALYSIS ===")
        runner.run_complexity_analysis(sizes=args.sizes)
    
    # Save results
    output_file = runner.save(format=args.format)
    print("-" * 50)
    print(f"Results saved to: {output_file}")
    print(f"Total results: {len(runner.results)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
