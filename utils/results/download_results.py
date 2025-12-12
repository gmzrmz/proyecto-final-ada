#!/usr/bin/env python3
"""
Download all benchmark results from S3 when all instances are complete.
Monitors instances and automatically downloads results when ready.
"""
import boto3
import time
import zipfile
import sys
import subprocess
from pathlib import Path
from datetime import datetime

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

def list_available_buckets():
    """List all available S3 buckets with creation dates"""
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_buckets()
        buckets = []
        
        for bucket in response['Buckets']:
            # Filter only matrix-crossing buckets
            if 'matrix-crossing' in bucket['Name']:
                buckets.append({
                    'name': bucket['Name'],
                    'created': bucket['CreationDate']
                })
        
        # Sort by creation date (newest first)
        buckets.sort(key=lambda x: x['created'], reverse=True)
        
        return buckets
    except Exception as e:
        print(f"[ERROR] Listando buckets: {e}")
        return []

def select_bucket_interactive():
    """Interactive bucket selection"""
    buckets = list_available_buckets()
    
    if not buckets:
        print("[!] No se encontraron buckets de matrix-crossing")
        return None
    
    print("\nBuckets disponibles (ordenados por fecha de creación):")
    print("="*70)
    
    for i, bucket in enumerate(buckets, 1):
        created_str = bucket['created'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i:2d}. {bucket['name']} (creado: {created_str})")
    
    print(f"{len(buckets)+1:2d}. Usar bucket de Terraform ({get_bucket_name()})")
    print(f"{len(buckets)+2:2d}. Cancelar")
    
    while True:
        try:
            choice = input(f"\nSelecciona bucket (1-{len(buckets)+2}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(buckets):
                selected = buckets[choice_num - 1]['name']
                print(f"[OK] Seleccionado: {selected}")
                return selected
            elif choice_num == len(buckets) + 1:
                selected = get_bucket_name()
                print(f"[OK] Usando bucket de Terraform: {selected}")
                return selected
            elif choice_num == len(buckets) + 2:
                print("[INFO] Cancelado por usuario")
                return None
            else:
                print(f"[!] Opción inválida. Usa 1-{len(buckets)+2}")
        except ValueError:
            print("[!] Ingresa un número válido")

def get_running_instances():
    """Check if any benchmark instances are still running"""
    ec2 = boto3.client('ec2')
    
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Environment', 'Values': ['benchmark']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        
        running = []
        for reservation in response['Reservations']:
            for inst in reservation['Instances']:
                tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
                running.append(tags.get('Algorithm', 'unknown'))
        
        return running
    except Exception as e:
        print(f"[ERROR] Checking instances: {e}")
        return []

def download_all_results(bucket=None):
    """Download all result files from S3"""
    if bucket is None:
        bucket = get_bucket_name()
    
    s3 = boto3.client('s3')
    
    # Create results directory
    results_dir = Path('benchmark_results')
    results_dir.mkdir(exist_ok=True)
    
    print(f"\n>> Descargando resultados desde S3 bucket: {bucket}")
    print("="*80)
    
    try:
        response = s3.list_objects_v2(Bucket=bucket)
        objects = response.get('Contents', [])
        
        # Filter result files (ZIPs and test matrices)
        result_files = []
        test_matrix_files = []
        
        for obj in objects:
            if obj['Key'].endswith('.zip'):
                result_files.append(obj)
            elif 'test_matrices' in obj['Key']:
                test_matrix_files.append(obj)
        
        all_files = result_files + test_matrix_files
        
        if not all_files:
            print("[!] No hay archivos de resultados o matrices de testeo en S3")
            return False
        
        downloaded = []
        skipped = []
        
        for obj in all_files:
            filename = obj['Key']
            size_kb = obj['Size'] / 1024
            local_path = results_dir / filename
            
            # Check if already exists and has correct size
            if local_path.exists() and local_path.stat().st_size == obj['Size']:
                print(f"  [SKIP] {filename} (ya existe, {size_kb:.1f} KB)")
                skipped.append(filename)
                continue
            
            print(f"  Descargando: {filename} ({size_kb:.1f} KB)...")
            try:
                s3.download_file(bucket, filename, str(local_path))
                
                # Verify download
                if not local_path.exists() or local_path.stat().st_size == 0:
                    print(f"    [ERROR] Descarga fallida para {filename}")
                    continue
                
                # Extract if it's a ZIP file
                if filename.endswith('.zip'):
                    # Extract ZIP
                    extract_dir = results_dir / filename.replace('.zip', '')
                    extract_dir.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(local_path, 'r') as zf:
                        zf.extractall(extract_dir)
                        files = zf.namelist()
                        print(f"    Extraido: {len(files)} archivo(s) en {extract_dir.name}/")
                
                # Extract if it's a tar.gz file
                elif filename.endswith('.tar.gz'):
                    import tarfile
                    # Extract to project root (not in results_dir)
                    extract_path = Path('.')
                    
                    with tarfile.open(local_path, 'r:gz') as tar:
                        tar.extractall(extract_path)
                        files = tar.getnames()
                        print(f"    Extraido: {len(files)} archivo(s) en directorio raíz")
                
                downloaded.append(filename)
                
            except Exception as e:
                print(f"    [ERROR] Procesando {filename}: {e}")
                continue
        
        total_processed = len(downloaded) + len(skipped)
        print("\n" + "="*80)
        print(f"[OK] {total_processed} archivo(s) procesado(s)")
        if downloaded:
            print(f"    Descargados: {len(downloaded)}")
        if skipped:
            print(f"    Saltados: {len(skipped)}")
        print(f"[INFO] Resultados en: {results_dir.absolute()}")
        print("="*80)
        
        # List what was downloaded
        if downloaded or skipped:
            print("\nArchivos procesados:")
            for fname in downloaded + skipped:
                if fname.endswith('.zip'):
                    algo = fname.split('_')[0]
                    status = "[NEW]" if fname in downloaded else "[SKIP]"
                    print(f"  {status} {algo:18} -> benchmark_results/{fname.replace('.zip', '')}/")
                elif 'test_matrices' in fname:
                    status = "[NEW]" if fname in downloaded else "[SKIP]"
                    print(f"  {status} {fname:18} -> extraído en directorio raíz")
        
        return len(downloaded) > 0 or len(skipped) > 0
        
    except Exception as e:
        print(f"[ERROR] Descargando: {e}")
        return False

def wait_for_completion(check_interval=60, max_wait_minutes=180):
    """Wait for all instances to complete before downloading"""
    print("\n" + "="*80)
    print("  ESPERANDO COMPLETACION DE BENCHMARKS")
    print("="*80)
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    iteration = 0
    while True:
        iteration += 1
        elapsed_minutes = (time.time() - start_time) / 60
        
        print(f"\n[{iteration}] Verificando estado... (Transcurrido: {elapsed_minutes:.1f} min)")
        
        running = get_running_instances()
        
        if not running:
            print("\n[OK] Todas las instancias han terminado!")
            return True
        
        print(f"[WAIT] {len(running)} instancia(s) aun corriendo:")
        for algo in running:
            print(f"  - {algo}")
        
        # Check timeout
        if time.time() - start_time > max_wait_seconds:
            print(f"\n[!] Timeout alcanzado ({max_wait_minutes} minutos)")
            print(f"    Instancias aun corriendo: {', '.join(running)}")
            
            response = input("\nDescargar resultados disponibles? (s/n): ")
            if response.lower() in ['s', 'si', 'y', 'yes']:
                return True
            return False
        
        # Wait before next check
        print(f"[WAIT] Esperando {check_interval} segundos antes de siguiente verificacion...")
        time.sleep(check_interval)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download benchmark results from S3')
    parser.add_argument('--wait', action='store_true', 
                       help='Wait for all instances to complete before downloading')
    parser.add_argument('--interval', type=int, default=60,
                       help='Check interval in seconds (default: 60)')
    parser.add_argument('--max-wait', type=int, default=180,
                       help='Maximum wait time in minutes (default: 180)')
    parser.add_argument('--bucket', type=str,
                       help='S3 bucket name (default: interactive selection)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto mode: use Terraform bucket without interaction')
    parser.add_argument('--list-buckets', action='store_true',
                       help='List available buckets and exit')
    
    args = parser.parse_args()
    
    # List buckets mode
    if args.list_buckets:
        buckets = list_available_buckets()
        if buckets:
            print("Buckets disponibles:")
            for i, bucket in enumerate(buckets, 1):
                created_str = bucket['created'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"{i:2d}. {bucket['name']} (creado: {created_str})")
        else:
            print("[!] No se encontraron buckets")
        return
    
    # Get bucket name
    if args.bucket:
        bucket = args.bucket
        print(f"[OK] Usando bucket especificado: {bucket}")
    elif args.auto:
        bucket = get_bucket_name()
        print(f"[OK] Modo automático: usando bucket de Terraform: {bucket}")
    else:
        bucket = select_bucket_interactive()
        if bucket is None:
            print("\n[!] Operación cancelada por el usuario")
            sys.exit(1)  # Exit with error code
    
    if args.wait:
        # Wait mode - monitor instances
        if wait_for_completion(args.interval, args.max_wait):
            success = download_all_results(bucket)
            if success:
                print("\n[TIP] Analiza con: python utils/results/analyze_results.py")
                print("[TIP] Genera graficas con: python generate_visualizations.py\n")
        else:
            print("\n[!] Descarga cancelada")
    else:
        # Immediate download
        running = get_running_instances()
        if running:
            print(f"\n[!] ADVERTENCIA: {len(running)} instancia(s) aun corriendo:")
            for algo in running:
                print(f"  - {algo}")
            
            response = input("\n¿Descargar resultados disponibles de todos modos? (s/n): ")
            if response.lower() not in ['s', 'si', 'y', 'yes']:
                print("\n[INFO] Usa --wait para esperar automaticamente")
                return
        
        success = download_all_results(bucket)
        if success:
            print("\n[TIP] Analiza con: python utils/results/analyze_results.py")
            print("[TIP] Genera graficas con: python generate_visualizations.py\n")

if __name__ == "__main__":
    main()
