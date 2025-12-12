#!/usr/bin/env python3
"""
Generate experiment metadata and upload results to S3.
Handles metadata generation, ZIP creation, and S3 upload.
"""
import sys
import json
import zipfile
import subprocess
import os
import time
from datetime import datetime
from pathlib import Path


def generate_metadata(experiment_id, algorithm, start_time, end_time, s3_bucket):
    """Generate experiment metadata JSON"""
    total_duration = end_time - start_time
    hours = total_duration // 3600
    minutes = (total_duration % 3600) // 60
    seconds = total_duration % 60
    
    metadata = {
        "experiment_id": experiment_id,
        "algorithm": algorithm,
        "start_time": start_time,
        "end_time": end_time,
        "total_duration_seconds": total_duration,
        "total_duration_formatted": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        "completion_timestamp": datetime.now().strftime('%Y%m%d_%H%M%S'),
        "bucket": s3_bucket
    }
    
    return metadata


def upload_to_s3(experiment_id, algorithm, result_dir, s3_bucket):
    """Create ZIP and upload to S3"""
    completion_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"{experiment_id}_{algorithm}_{completion_time}.zip"
    zip_path = f"/tmp/{zip_filename}"
    
    # Create ZIP with all results
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(result_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, result_dir)
                zipf.write(file_path, arcname)
    
    print(f"[OK] ZIP creado: {zip_filename}")
    
    # Upload to S3
    subprocess.run([
        '/usr/local/bin/aws', 's3', 'cp', 
        zip_path, 
        f"s3://{s3_bucket}/"
    ], check=True)
    
    print(f"[OK] Resultados subidos como: {zip_filename}")
    return zip_filename


def main():
    """Main function"""
    if len(sys.argv) < 4:
        print("Uso: python upload_results.py <id_experimento> <algoritmo> <s3_bucket>")
        sys.exit(1)
    
    experiment_id = sys.argv[1]
    algorithm = sys.argv[2]
    s3_bucket = sys.argv[3]
    
    result_dir = "/results"
    
    # Read start time from marker file (created before benchmark)
    start_marker = os.path.join(result_dir, ".benchmark_start_time")
    if os.path.exists(start_marker):
        with open(start_marker, 'r') as f:
            start_time = int(f.read().strip())
    else:
        print("[WARNING] No se encontró el marcador de tiempo inicial, usando el tiempo actual")
        start_time = int(time.time())
    
    end_time = int(time.time())
    
    # Generate and save metadata
    metadata = generate_metadata(experiment_id, algorithm, start_time, end_time, s3_bucket)
    
    metadata_path = os.path.join(result_dir, "experiment_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, indent=2, fp=f)
    
    print("="*70)
    print("Metadatos del experimento:")
    print(json.dumps(metadata, indent=2))
    print("="*70)
    
    # Upload to S3
    upload_to_s3(experiment_id, algorithm, result_dir, s3_bucket)
    
    print(f"\nBenchmark completado para {algorithm}!")
    print(f"Tiempo total del experimento: {metadata['total_duration_seconds']} segundos")
    print(f"Duración formateada: {metadata['total_duration_formatted']}")


if __name__ == "__main__":
    main()
