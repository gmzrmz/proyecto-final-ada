"""
Script para desplegar benchmarks en AWS
"""
import subprocess
import sys
import time
import argparse

TERRAFORM = r"C:\terraform_1.14.1_windows_386\terraform.exe"

def run_command(cmd, cwd=None):
    """Ejecuta comando y muestra output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[ERROR] {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"[ERROR] Excepción: {e}")
        return False

def init_terraform_if_needed():
    """Inicializa Terraform si es necesario"""
    import os
    
    print("[+] Inicializando Terraform...")
    cmd = f'{TERRAFORM} init'
    if not run_command(cmd, cwd='infrastructure'):
        print("[ERROR] Falló inicialización de Terraform")
        return False
    
    return True

def deploy(experiment_id=None):
    """Despliega infraestructura"""
    print("\n>> Desplegando infraestructura...\n")
    
    # Inicializar Terraform si es necesario
    if not init_terraform_if_needed():
        return False
    
    cmd = f'{TERRAFORM} apply -auto-approve'
    if experiment_id:
        cmd += f' -var="experiment_id={experiment_id}"'
        print(f"[+] Using experiment ID: {experiment_id}")
    
    return run_command(cmd, cwd='infrastructure')

def destroy():
    """Destruye infraestructura"""
    print("\n>> Destruyendo infraestructura...\n")
    
    # Inicializar Terraform si es necesario
    if not init_terraform_if_needed():
        return False
    
    cmd = f'{TERRAFORM} destroy -auto-approve'
    return run_command(cmd, cwd='infrastructure')

def status():
    """Muestra estado actual"""
    print("\n>> Estado de la infraestructura:\n")
    
    # Inicializar Terraform si es necesario
    if not init_terraform_if_needed():
        return False
    
    cmd = f'{TERRAFORM} show'
    return run_command(cmd, cwd='infrastructure')

def main():
    parser = argparse.ArgumentParser(
        description='Deploy Matrix Crossing Benchmark infrastructure',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        choices=['deploy', 'd', 'destroy', 'x', 'status', 's'],
        help='Command to execute: deploy, destroy, or status'
    )
    
    parser.add_argument(
        '--experiment-id',
        type=str,
        default=None,
        help='Unique experiment ID for S3 bucket naming (YYYYMMDDHHMMSS format)'
    )
    
    args = parser.parse_args()
    command = args.command.lower()
    
    if command == 'deploy' or command == 'd':
        if deploy(experiment_id=args.experiment_id):
            print("\n[OK] Deploy completado")
            print("[TIP] Monitorea con: python monitor.py")
    elif command == 'destroy' or command == 'del':
        if destroy():
            print("\n[OK] Infraestructura destruida")
    elif command == 'status' or command == 's':
        status()
    else:
        print(f"[ERROR] Comando desconocido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
