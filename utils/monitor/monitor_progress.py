#!/usr/bin/env python3
"""
Monitor benchmark progress on AWS instances.
Checks instance status and S3 results.
"""
import boto3
import subprocess
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
    
    # Fallback to old bucket if Terraform not available
    print("  [!] No se pudo obtener bucket desde Terraform, usando bucket anterior")
    return "matrix-crossing-benchmark-91097"

def list_instances():
    """List all benchmark instances"""
    ec2 = boto3.client('ec2')
    
    print("\nINSTANCIAS EC2")
    print("="*80)
    
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Environment', 'Values': ['benchmark']}
            ]
)
        
        instances = []
        for reservation in response['Reservations']:
            for inst in reservation['Instances']:
                tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
                state = inst['State']['Name']
                
                # Calculate uptime
                if state == 'running':
                    launch_time = inst['LaunchTime']
                    now = datetime.now(launch_time.tzinfo)
                    elapsed = now - launch_time
                    mins = int(elapsed.total_seconds() / 60)
                    uptime = f"{mins} min"
                else:
                    uptime = "N/A"
                
                instances.append({
                    'id': inst['InstanceId'],
                    'algorithm': tags.get('Algorithm', 'N/A'),
                    'state': state,
                    'uptime': uptime
                })
        
        if not instances:
            print("  [!] No hay instancias")
            return []
        
        for inst in instances:
            icon = "[+]" if inst['state'] == 'running' else "[-]" if inst['state'] == 'terminated' else "[.]" 
            print(f"  {icon} {inst['algorithm']:20} {inst['id']:20} {inst['state']:12} {inst['uptime']}")
        
        return [i for i in instances if i['state'] == 'running']
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []

def check_s3_results(bucket=None):
    """Check S3 bucket for results"""
    if bucket is None:
        bucket = get_bucket_name()
    
    s3 = boto3.client('s3')
    
    print("\nRESULTADOS EN S3")
    print("="*80)
    
    try:
        response = s3.list_objects_v2(Bucket=bucket)
        objects = response.get('Contents', [])
        
        if not objects:
            print("  [!] Bucket vacío")
            return
        
        # Separate matrices from results
        matrices = [o for o in objects if 'test_matrices' in o['Key']]
        results = [o for o in objects if o['Key'].endswith('.zip')]
        
        print("\nMatrices de prueba:")
        for obj in matrices:
            size_mb = obj['Size'] / 1024 / 1024
            print(f"  [OK] {obj['Key']} ({size_mb:.2f} MB)")
        
        if results:
            print("\nResultados:")
            for obj in results:
                size_kb = obj['Size'] / 1024
                algo = obj['Key'].split('_')[0]
                timestamp = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"  [*] {algo:20} ({size_kb:.1f} KB) - {timestamp}")
            
            print(f"\n  [OK] {len(results)} algoritmo(s) completado(s)")
        else:
            print("\n  [WAIT] Aún no hay resultados")
        
    except Exception as e:
        print(f"  [ERROR] {e}")

def main():
    """Main monitoring function"""
    print("\n" + "="*80)
    print("  MONITOR DE BENCHMARKS AWS")
    print("="*80)
    
    running = list_instances()
    check_s3_results()
    
    print("\n" + "="*80)
    if running:
        print(f"[WAIT] {len(running)} instancia(s) ejecutándose - Esperar 15-180 minutos")
    else:
        print("[OK] Todas las instancias completadas o detenidas")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
