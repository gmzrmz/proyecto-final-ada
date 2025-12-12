#!/usr/bin/env python3
"""
Upload test matrices to S3 bucket.
"""

import boto3
import sys
import os
import tarfile
from pathlib import Path

def create_tarball(source_dir, output_file):
    """Create tarball from directory"""
    print(f"\n[+] Creando tarball desde {source_dir}...")
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    print(f"[OK] Tarball creado: {output_file}")
    return output_file

def upload_to_s3(file_path, bucket_name, s3_key=None):
    """Upload file to S3"""
    if s3_key is None:
        s3_key = os.path.basename(file_path)
    
    print(f"\n[+] Subiendo {file_path} a s3://{bucket_name}/{s3_key}...")
    
    try:
        s3 = boto3.client('s3')
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"[OK] Archivo subido exitosamente")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo subir: {e}")
        return False

def get_bucket_name():
    """Get bucket name from Terraform output or use default"""
    try:
        import subprocess
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
    
    # Default bucket name pattern
    return "matrix-crossing-benchmark-91097"

def main():
    """Main function"""
    print("="*70)
    print("  SUBIDA DE MATRICES DE PRUEBA A S3")
    print("="*70)
    
    # Check if test_matrices directory exists
    matrices_dir = "test_matrices"
    if not os.path.exists(matrices_dir):
        print(f"\n[ERROR] Directorio {matrices_dir}/ no encontrado")
        print("Ejecuta primero: python utils/start/generate_test_matrices.py")
        return 1
    
    # Check for tarball or create it
    tarball = "test_matrices.tar.gz"
    if not os.path.exists(tarball):
        print(f"\n[!] No se encontró {tarball}, creándolo...")
        create_tarball(matrices_dir, tarball)
    else:
        print(f"\n[OK] Usando tarball existente: {tarball}")
    
    # Get bucket name
    bucket_name = get_bucket_name()
    print(f"\n[OK] Bucket S3: {bucket_name}")
    
    # Upload
    if upload_to_s3(tarball, bucket_name, "test_matrices.tar.gz"):
        print("\n" + "="*70)
        print("  MATRICES SUBIDAS EXITOSAMENTE")
        print("="*70)
        print(f"\nUbicación: s3://{bucket_name}/test_matrices.tar.gz")
        print("\nSiguiente paso:")
        print("  python utils/start/deploy.py deploy")
        return 0
    else:
        print("\n[ERROR] Fallo la subida a S3")
        print("\nVerifica:")
        print("  1. Credenciales AWS configuradas")
        print("  2. Bucket existe")
        print("  3. Permisos de escritura")
        return 1

if __name__ == "__main__":
    sys.exit(main())
