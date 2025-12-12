#!/usr/bin/env python3
"""
Script 2: MONITOREAR PROGRESO
Monitorea el progreso de las instancias EC2 ejecutando benchmarks.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_menu():
    """Print monitoring menu"""
    print("\n" + "-"*70)
    print("OPCIONES DE MONITOREO:")
    print("-"*70)
    print("  1. Monitor general (estado de instancias y S3)")
    print("  2. Monitor detallado (logs y pruebas ejecutadas)")
    print("  3. Monitor continuo (actualización automática cada 60s)")
    print("  4. Ver solo instancias en ejecución")
    print("  5. Verificar si todas las instancias terminaron")
    print("  0. Salir")
    print("-"*70)

def run_monitor_general():
    """Run general progress monitor"""
    script = "utils/monitor/monitor_progress.py"
    if not os.path.exists(script):
        print(f"[ERROR] No se encontró {script}")
        return False
    
    print("\n[+] Ejecutando monitor general...\n")
    try:
        subprocess.run(f"python {script}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def run_monitor_detailed():
    """Run detailed instance progress monitor"""
    script = str(Path(__file__).parent.parent / "utils" / "monitor" / "check_instance_progress.py")
    if not os.path.exists(script):
        print(f"[ERROR] No se encontró {script}")
        return False
    
    print("\n[+] Ejecutando monitor detallado...\n")
    try:
        subprocess.run(f"python {script}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def run_monitor_continuous():
    """Run continuous monitoring with auto-refresh"""
    print("\n[+] Monitor continuo (Ctrl+C para detener)")
    print("[!] Actualización automática cada 60 segundos\n")
    
    script = str(Path(__file__).parent.parent / "utils" / "monitor" / "check_instance_progress.py")
    if not os.path.exists(script):
        print(f"[ERROR] No se encontró {script}")
        return False
    
    try:
        iteration = 1
        while True:
            print(f"\n{'='*70}")
            print(f"  ACTUALIZACIÓN #{iteration} - {time.strftime('%H:%M:%S')}")
            print(f"{'='*70}\n")
            
            subprocess.run(f"python {script}", shell=True, check=False)
            
            print(f"\n[!] Esperando 60 segundos... (Ctrl+C para detener)")
            time.sleep(60)
            iteration += 1
            
            # Clear screen (optional)
            if sys.platform == "win32":
                os.system('cls')
            else:
                os.system('clear')
                
    except KeyboardInterrupt:
        print("\n\n[!] Monitor detenido por el usuario")
        return True

def check_running_instances():
    """Check only running instances"""
    print("\n[+] Verificando instancias en ejecución...\n")
    
    try:
        # Get all running EC2 instances (not filtered by tags, just state)
        result = subprocess.run(
            'aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[*].Instances[*].[InstanceId,LaunchTime,State.Name,Tags[?Key==`Name`].Value|[0]]" --output table',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout
        print(output)
        
        # Count instances by looking for instance IDs (i-xxxxxxxxxxxxxxxxx)
        import re
        instance_ids = re.findall(r'i-[a-f0-9]{17}', output)
        running_count = len(instance_ids)
        
        print(f"\n[INFO] Instancias en ejecución: {running_count}")
        
        if running_count == 0:
            print("[OK] No hay instancias en ejecución")
            print("[!] Puedes proceder a descargar resultados con scripts/3_results.py")
        else:
            print(f"[!] Hay {running_count} instancia(s) ejecutándose")
            print("[!] Espera a que terminen o usa opción 2 para ver logs detallados")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudieron consultar las instancias: {e}")
        return False

def check_all_finished():
    """Check if all instances have finished"""
    print("\n[+] Verificando estado completo del experimento...\n")
    
    try:
        # Check ALL instances (running, stopped, terminated)
        result = subprocess.run(
            'aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,State.Name,LaunchTime,Tags[?Key==`Name`].Value|[0]]" --output json',
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        import re
        data = json.loads(result.stdout)
        
        total = 0
        running = 0
        stopped = 0
        terminated = 0
        
        print("Estado de instancias EC2:")
        print("-" * 70)
        
        for reservation in data:
            for instance in reservation:
                instance_id = instance[0]
                state = instance[1]
                name = instance[3] if len(instance) > 3 and instance[3] else "sin-nombre"
                
                total += 1
                print(f"  {instance_id} - {state:12s} - {name}")
                
                if state == 'running':
                    running += 1
                elif state == 'stopped':
                    stopped += 1
                elif state == 'terminated':
                    terminated += 1
        
        print("-" * 70)
        print(f"Total: {total} | Running: {running} | Stopped: {stopped} | Terminated: {terminated}")
        
        # Check S3 results
        print("\n[+] Verificando resultados en S3...")
        bucket_name = get_bucket_name()
        print(f"    Bucket: {bucket_name}")
        
        s3_result = subprocess.run(
            f'aws s3 ls s3://{bucket_name}/',
            shell=True,
            capture_output=True,
            text=True
        )
        
        # Count .zip files
        zip_count = len(re.findall(r'\.zip', s3_result.stdout))
        
        print(f"\nArchivos ZIP en S3: {zip_count}")
        if s3_result.stdout.strip():
            for line in s3_result.stdout.strip().split('\n'):
                if '.zip' in line:
                    print(f"  {line.strip()}")
        
        print("\n" + "="*70)
        if running == 0 and zip_count >= 5:
            print("[OK] EXPERIMENTO COMPLETADO")
            print("[OK] Todas las instancias han terminado")
            print(f"[OK] {zip_count} resultados disponibles en S3")
            print("="*70)
            print("\nPróximo paso:")
            print("  python scripts/3_results.py")
        elif running > 0:
            print(f"[!] EXPERIMENTO EN PROGRESO")
            print(f"[!] {running} instancia(s) aún ejecutándose")
            print(f"[!] {zip_count}/5 resultados en S3")
            print("="*70)
            print("\nAcciones sugeridas:")
            print("  - Usa opción 2 para ver logs detallados")
            print("  - Usa opción 3 para monitoreo continuo")
        elif running == 0 and zip_count < 5:
            print(f"[!] POSIBLE PROBLEMA")
            print(f"[!] Instancias terminadas pero solo {zip_count}/5 resultados")
            print("="*70)
            print("\nVerifica:")
            print("  - Logs de instancias con opción 2")
            print("  - Pruebas unitarias pueden haber fallado")
        else:
            print("[INFO] Estado del experimento")
            print("="*70)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] No se pudo verificar el estado: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"[ERROR] No se pudo parsear la respuesta de AWS: {e}")
        print(f"[ERROR] No se pudo parsear la respuesta de AWS: {e}")
        return False

def main():
    print_header("SCRIPT 2: MONITOREAR PROGRESO DEL BENCHMARK")
    
    while True:
        print_menu()
        
        choice = input("\nSelecciona una opción [0-5]: ").strip()
        
        if choice == "1":
            run_monitor_general()
        elif choice == "2":
            run_monitor_detailed()
        elif choice == "3":
            run_monitor_continuous()
        elif choice == "4":
            check_running_instances()
        elif choice == "5":
            check_all_finished()
        elif choice == "0":
            print("\n[!] Saliendo del monitor...")
            break
        else:
            print("\n[ERROR] Opción inválida. Intenta de nuevo.")
        
        input("\nPresiona Enter para continuar...")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario")
        sys.exit(130)
