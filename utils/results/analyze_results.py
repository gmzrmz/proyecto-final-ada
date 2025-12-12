#!/usr/bin/env python3
"""
Analyze benchmark results from JSON files.
Downloads results from S3 and generates analysis reports.
"""
import json
import sys
import os
import argparse
from pathlib import Path
import boto3
import subprocess

def get_bucket_name():
    """Get bucket name from Terraform output"""
    try:
        result = subprocess.run(
            ['terraform', 'output', '-raw', 'bucket_name'],
            cwd='infrastructure',
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    return "matrix-crossing-benchmark-91097"  # Fallback

def download_results_from_s3(bucket=None, results_dir='results'):
    """Download all result files from S3"""
    if bucket is None:
        bucket = get_bucket_name()
    
    s3 = boto3.client('s3')
    results_path = Path(results_dir)
    results_path.mkdir(exist_ok=True)
    
    print(f">> Descargando resultados desde S3 bucket: {bucket}")
    
    try:
        response = s3.list_objects_v2(Bucket=bucket)
        objects = response.get('Contents', [])
        
        result_files = [obj for obj in objects if obj['Key'].endswith('.zip')]
        
        if not result_files:
            print("[!] No hay archivos de resultados en S3")
            return []
        
        downloaded = []
        for obj in result_files:
            filename = obj['Key']
            local_path = results_path / filename
            
            # Skip if already exists
            if local_path.exists():
                print(f"  [SKIP] {filename} (ya existe)")
                downloaded.append(local_path)
                continue
            
            print(f"  [*] {filename}...")
            s3.download_file(bucket, filename, str(local_path))
            downloaded.append(local_path)
        
        print(f"\n[OK] {len(downloaded)} archivo(s) procesado(s)")
        return downloaded
        
    except Exception as e:
        print(f"[ERROR] Error descargando: {e}")
        return []

def extract_and_find_json(zip_path, extract_to='results'):
    """Extract ZIP and find JSON file"""
    import zipfile
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        json_files = [f for f in zf.namelist() if f.endswith('.json')]
        if not json_files:
            return None
        
        # Extract first JSON found
        zf.extract(json_files[0], extract_to)
        return Path(extract_to) / json_files[0]

def analyze_json_file(json_path):
    """Analyze a single JSON results file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar {json_path}: {e}")
        return None
    
    results = data.get('results', [])
    
    # Skip files that don't have results array or it's empty
    if not results:
        return None
    
    # Get algorithm name from first result, filename, or folder name
    if results and results[0].get('algorithm'):
        algorithm = results[0]['algorithm']
    elif 'benchmark_' in json_path.name:
        # Extract from filename like "benchmark_backtracking_20251210_223215.json"
        algorithm = json_path.name.split('_')[1]
    else:
        # Extract from folder name like "20251210155943_backtracking_20251210_223215"
        folder_parts = json_path.parent.name.split('_')
        if len(folder_parts) > 1:
            algorithm = folder_parts[1]
        else:
            # Try to extract from filename if it contains algorithm name
            filename_parts = json_path.stem.split('_')
            for part in filename_parts:
                if part in ['backtracking', 'brute_force', 'divide_and_conquer', 'memoization', 'tabulation']:
                    algorithm = part
                    break
            else:
                algorithm = 'unknown'
    
    total = len(results)
    success = sum(1 for r in results if not r.get('timed_out', False) and not r.get('error_message'))
    timeout = sum(1 for r in results if r.get('timed_out', False))
    error = sum(1 for r in results if r.get('error_message'))
    
    # Calculate avg time for successful runs
    success_times = [r['execution_time_seconds'] for r in results 
                     if not r.get('timed_out', False) and not r.get('error_message') 
                     and r.get('execution_time_seconds') is not None]
    avg_time = sum(success_times) / len(success_times) if success_times else 0
    
    # Memory analysis
    memory_values = [r.get('peak_memory_kb', 0) for r in results 
                     if r.get('peak_memory_kb') is not None and not r.get('timed_out', False)]
    avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0
    
    return {
        'algorithm': algorithm,
        'total': total,
        'success': success,
        'timeout': timeout,
        'error': error,
        'avg_time': avg_time,
        'avg_memory': avg_memory,
        'results': results
    }

def main():
    """Main analysis function"""
    parser = argparse.ArgumentParser(description="Analyze benchmark results")
    parser.add_argument('--bucket', help='S3 bucket name (default: from Terraform)')
    parser.add_argument('--results-dir', default='benchmark_results', help='Results directory')
    parser.add_argument('--no-download', action='store_true', help='Skip download, analyze existing files')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  ANÁLISIS DE RESULTADOS DE BENCHMARKS")
    print("="*60)
    
    # Download from S3 unless skipped
    if not args.no_download:
        downloaded = download_results_from_s3(args.bucket, args.results_dir)
        if not downloaded:
            print("\n[!] No hay resultados para analizar")
            return
    else:
        # Find existing files to analyze
        results_path = Path(args.results_dir)
        downloaded = list(results_path.glob('*.zip'))
        json_files = list(results_path.glob('**/benchmark_*.json'))  # Include subdirectories
        if not downloaded and not json_files:
            print(f"\n[!] No hay archivos ZIP o JSON en {args.results_dir}")
            return
        print(f"[OK] Analizando {len(downloaded)} ZIP y {len(json_files)} JSON existente(s)")
    
    # Analyze each file
    print("\nRESUMEN POR ALGORITMO")
    print("="*60)
    
    all_stats = []
    
    # Process ZIP files
    for zip_path in downloaded:
        json_path = extract_and_find_json(zip_path, args.results_dir)
        if json_path and json_path.exists():
            stats = analyze_json_file(json_path)
            if stats:
                all_stats.append(stats)
    
    # Process standalone JSON files (including those in subdirectories)
    results_path = Path(args.results_dir)
    for json_path in results_path.glob('**/benchmark_*.json'):
        # Skip metadata files
        if 'metadata' in json_path.name.lower():
            continue
        stats = analyze_json_file(json_path)
        if stats:
            all_stats.append(stats)
    
    # Remove duplicates (same algorithm)
    seen_algorithms = set()
    unique_stats = []
    for stats in all_stats:
        if stats['algorithm'] not in seen_algorithms:
            seen_algorithms.add(stats['algorithm'])
            unique_stats.append(stats)
    
    all_stats = unique_stats
    
    for stats in all_stats:
        print(f"\n{stats['algorithm'].upper()}")
        print(f"  Total: {stats['total']}")
        print(f"  [OK] Completadas: {stats['success']}")
        print(f"  [T] Timeouts: {stats['timeout']}")
        print(f"  [E] Errores: {stats['error']}")
        print(f"  Tiempo promedio: {stats['avg_time']*1000:.2f} ms")
        if stats['avg_memory'] > 0:
            print(f"  Memoria promedio: {stats['avg_memory']:.1f} KB")
    
    if not all_stats:
        print("[!] No se pudieron analizar resultados")
        return
    
    # Overall comparison
    print("\n" + "="*60)
    print("COMPARACION GENERAL")
    print("="*60)
    
    # Sort by average time
    time_sorted = sorted(all_stats, key=lambda x: x['avg_time'])
    print("\nRanking por velocidad (tiempo promedio):")
    for i, stats in enumerate(time_sorted, 1):
        print(f"{i}. {stats['algorithm']:20} {stats['avg_time']*1000:8.2f} ms")
    
    # Sort by success rate
    success_sorted = sorted(all_stats, key=lambda x: x['success']/x['total'] if x['total'] > 0 else 0, reverse=True)
    print("\nRanking por tasa de éxito:")
    for i, stats in enumerate(success_sorted, 1):
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{i}. {stats['algorithm']:20} {success_rate:6.1f}% ({stats['success']}/{stats['total']})")
    
    # Memory ranking if available
    memory_stats = [s for s in all_stats if s['avg_memory'] > 0]
    if memory_stats:
        memory_sorted = sorted(memory_stats, key=lambda x: x['avg_memory'])
        print("\nRanking por uso de memoria:")
        for i, stats in enumerate(memory_sorted, 1):
            print(f"{i}. {stats['algorithm']:20} {stats['avg_memory']:8.1f} KB")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
