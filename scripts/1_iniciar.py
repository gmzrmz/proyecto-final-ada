#!/usr/bin/env python3
"""
Script 1: INICIAR EXPERIMENTO
Configura credenciales, genera/sube matrices y despliega benchmark en AWS.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(step_num, text):
    """Print formatted step"""
    print(f"\n[PASO {step_num}] {text}")
    print("-"*70)

def get_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    return input(f"{prompt}: ").strip()

def yes_no(prompt, default_yes=True):
    """Get yes/no response"""
    default = "S/n" if default_yes else "s/N"
    response = input(f"{prompt} [{default}]: ").strip().lower()
    
    if not response:
        return default_yes
    return response in ['s', 'si', 'y', 'yes']

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n[+] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"[OK] {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} falló con código {e.returncode}")
        return False

def configure_aws_credentials():
    """Configure AWS credentials interactively"""
    print_step(1, "CONFIGURACIÓN DE CREDENCIALES AWS ACADEMY")
    
    print("\n  IMPORTANTE: Credenciales de AWS Academy Learner Lab")
def configure_aws_credentials():
    """Configure AWS credentials interactively"""
    print_step(1, "CONFIGURACIÓN DE CREDENCIALES AWS ACADEMY")
    
    # Create .aws directory if it doesn't exist
    aws_dir = Path.home() / ".aws"
    aws_dir.mkdir(exist_ok=True)
    
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    # Remove old credentials to force fresh setup
    if credentials_file.exists():
        print(f"\n[!] Eliminando credenciales anteriores: {credentials_file}")
        credentials_file.unlink()
    
    if config_file.exists():
        print(f"[!] Eliminando configuración anterior: {config_file}")
        config_file.unlink()
    
    print("\n  IMPORTANTE: Credenciales de AWS Academy Learner Lab")
    print("=" * 70)
    print("1. Ve a AWS Academy Learner Lab")
    print("2. Haz clic en 'Start Lab' y espera a que esté verde ●")
    print("3. Haz clic en 'AWS Details'")
    print("4. Haz clic en 'Show' junto a 'AWS CLI'")
    print("5. Copia las credenciales COMPLETAS (las 3 líneas)")
    print("=" * 70)
    print("\n IMPORTANTE: Las credenciales expiran cuando el lab se apaga")
    print("   Si ves errores 'AccessDenied', vuelve a ejecutar este script\n")
    
    aws_access_key = get_input("AWS Access Key ID")
    aws_secret_key = get_input("AWS Secret Access Key")
    aws_session_token = get_input("AWS Session Token")
    aws_region = get_input("AWS Region", default="us-east-1")
    
    # Write NEW credentials file
    with open(credentials_file, 'w') as f:
        f.write("[default]\n")
        f.write(f"aws_access_key_id = {aws_access_key}\n")
        f.write(f"aws_secret_access_key = {aws_secret_key}\n")
        f.write(f"aws_session_token = {aws_session_token}\n")
    
    print(f"[OK] Nuevas credenciales escritas en {credentials_file}")
    
    # Write NEW config file
    with open(config_file, 'w') as f:
        f.write("[default]\n")
        f.write(f"region = {aws_region}\n")
        f.write("output = json\n")
    
    print(f"[OK] Nueva configuración escrita en {config_file}")
    
    # Verify credentials immediately
    print("\n[+] Verificando credenciales...")
    result = subprocess.run("aws sts get-caller-identity", 
                          shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        identity = json.loads(result.stdout)
        print(f"[OK] Autenticado correctamente como:")
        print(f"    ARN: {identity.get('Arn', 'Unknown')}")
        print(f"    Account: {identity.get('Account', 'Unknown')}")
        print(f"    UserID: {identity.get('UserId', 'Unknown')}")
        return True
    else:
        print("[ERROR] Las credenciales NO son válidas")
        print("Verifica que:")
        print("  1. El Lab esté ACTIVO (luz verde)")
        print("  2. Copiaste las 3 credenciales completas")
        print("  3. No hayan pasado más de 4 horas desde que iniciaste el Lab")
        print("\nError técnico:")
        print(result.stderr)
        return False

def generate_or_use_matrices():
    """Generate test matrices or use existing ones"""
    print_step(2, "MATRICES DE PRUEBA")
    
    # Check if matrices already exist
    matrices_exist = os.path.exists("test_matrices.tar.gz") or os.path.exists("test_matrices")
    
    if matrices_exist:
        print("\n[!] Se encontraron matrices existentes")
        if yes_no("¿Deseas usar las matrices existentes?", default_yes=True):
            print("[OK] Usando matrices existentes")
            # Ensure tarball exists
            if not os.path.exists("test_matrices.tar.gz") and os.path.exists("test_matrices"):
                run_command("tar -czf test_matrices.tar.gz test_matrices", 
                          "Comprimir matrices existentes")
            return True
        else:
            # User wants new matrices - delete old ones
            print("[+] Eliminando matrices anteriores...")
            if os.path.exists("test_matrices.tar.gz"):
                os.remove("test_matrices.tar.gz")
                print("    test_matrices.tar.gz eliminado")
            if os.path.exists("test_matrices"):
                import shutil
                shutil.rmtree("test_matrices")
                print("    test_matrices/ eliminado")
    
    if yes_no("\n¿Deseas generar nuevas matrices de prueba?", default_yes=True):
        script = "utils/start/generate_test_matrices.py"
        if not os.path.exists(script):
            print(f"[ERROR] No se encontró {script}")
            return False
        
        # Ask if user wants random or reproducible matrices
        print("\n[?] Tipo de matrices:")
        print("  1. Reproducibles (seeds fijos - mismas matrices siempre)")
        print("  2. Aleatorias (seeds basados en timestamp - diferentes cada vez)")
        
        use_random = yes_no("\n¿Deseas matrices ALEATORIAS (diferentes cada vez)?", default_yes=False)
        
        cmd = f"python {script}"
        if use_random:
            cmd += " --random-seeds"
            print("\n[+] Generando matrices con seeds aleatorias...")
        else:
            print("\n[+] Generando matrices con seeds fijos (reproducibles)...")
        
        if run_command(cmd, "Generar matrices de prueba"):
            # Create fresh tarball
            if os.path.exists("test_matrices"):
                run_command("tar -czf test_matrices.tar.gz test_matrices", 
                          "Comprimir matrices")
            return True
        return False
    else:
        print("\n[!] ADVERTENCIA: Se necesitan matrices para continuar")
        print("    Asegúrate de tener test_matrices.tar.gz en el directorio")
        return os.path.exists("test_matrices.tar.gz")

def upload_matrices_to_s3():
    """Upload test matrices to S3 using bucket from Terraform"""
    print_step(4, "SUBIR MATRICES A S3")
    
    if not os.path.exists("test_matrices.tar.gz"):
        print("[ERROR] No se encontró test_matrices.tar.gz")
        return False
    
    # Get bucket name from Terraform output
    print("\n[+] Obteniendo nombre del bucket desde Terraform...")
    try:
        result = subprocess.run(
            ['terraform', 'output', '-raw', 'bucket_name'],
            cwd='infrastructure',
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0 or not result.stdout.strip():
            print("[ERROR] No se pudo obtener el bucket name desde Terraform")
            print("Asegúrate de haber desplegado la infraestructura primero")
            return False
        
        bucket_name = result.stdout.strip()
        print(f"[OK] Bucket detectado: {bucket_name}")
    except Exception as e:
        print(f"[ERROR] Error al obtener bucket: {e}")
        return False
    
    cmd = f"aws s3 cp test_matrices.tar.gz s3://{bucket_name}/test_matrices.tar.gz"
    return run_command(cmd, "Subir matrices a S3")

def deploy_infrastructure():
    """Deploy AWS infrastructure (creates S3 bucket and EC2 instances)"""
    print_step(3, "DESPLEGAR INFRAESTRUCTURA")
    
    # Check if infrastructure already exists
    print("\n[+] Verificando infraestructura existente...")
    os.chdir("infrastructure")
    
    try:
        # Check if there's existing state
        result = subprocess.run(
            "terraform show",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("[!] Se detectó infraestructura/EC2 existente de experimento anterior")
            print("    Los buckets S3 anteriores se mantendrán como archivo histórico")
            
            if yes_no("\n¿Deseas DESTRUIR las instancias EC2 anteriores?", default_yes=True):
                print("\n[+] Destruyendo instancias EC2 anteriores...")
                print("    (El bucket S3 anterior se conservará como archivo)")
                
                # Remove S3 bucket from state to preserve it
                print("[+] Preservando bucket S3 en el state...")
                subprocess.run(
                    "terraform state rm aws_s3_bucket.results",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                subprocess.run(
                    "terraform state rm aws_s3_bucket_versioning.results[0]",
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                # Now destroy only EC2 instances
                destroy_result = subprocess.run(
                    "terraform destroy -auto-approve",
                    shell=True,
                    check=False
                )
                
                if destroy_result.returncode != 0:
                    print("[ERROR] No se pudieron destruir las instancias anteriores")
                    if not yes_no("¿Deseas continuar de todas formas?", default_yes=False):
                        os.chdir("..")
                        return False
                else:
                    print("[OK] Instancias EC2 anteriores destruidas")
                    print("[OK] Bucket S3 anterior conservado como archivo histórico")
            else:
                print("[!] ADVERTENCIA: Continuando con infraestructura existente")
                print("    Esto creará NUEVAS instancias adicionales")
        else:
            print("[OK] No hay infraestructura previa")
    
    except Exception as e:
        print(f"[!] No se pudo verificar estado: {e}")
    
    os.chdir("..")
    
    # Generate unique experiment ID
    from datetime import datetime
    experiment_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    print("\n[+] Iniciando despliegue completo...")
    print(f"    - Experiment ID: {experiment_id}")
    print(f"    - Se creará bucket: matrix-crossing-benchmark-{experiment_id}")
    print("    - Se crearán 5 instancias EC2 nuevas")
    print("    - Cada EC2 ejecutará automáticamente:")
    print("      1. Pruebas unitarias (obligatorias)")
    print("      2. Benchmarks (solo si pasan las pruebas)")
    print("      3. Subida de resultados a S3")
    print("      4. Auto-apagado al terminar")
    
    if not yes_no("\n¿Deseas continuar con el despliegue?", default_yes=True):
        print("[!] Despliegue cancelado")
        return False
    
    script = "utils/start/deploy.py"
    if not os.path.exists(script):
        print(f"[ERROR] No se encontró {script}")
        return False
    
    return run_command(f"python {script} deploy --experiment-id {experiment_id}", 
                     "Desplegar infraestructura e iniciar benchmark")

def main():
    print_header("SCRIPT 1: INICIAR EXPERIMENTO DE BENCHMARK")
    
    print("Este script te guiará en el proceso de:")
    print("  1. Configurar credenciales AWS Academy")
    print("  2. Generar/usar matrices de prueba")
    print("  3. Desplegar infraestructura (crea bucket S3 + EC2)")
    print("  4. Subir matrices al bucket S3 creado")
    
    if not yes_no("\n¿Deseas continuar?", default_yes=True):
        print("\n[!] Operación cancelada")
        return 1
    
    # Step 1: AWS Credentials
    if not configure_aws_credentials():
        print("\n[ERROR] No se pudieron configurar las credenciales")
        return 1
    
    # Step 2: Test Matrices
    if not generate_or_use_matrices():
        print("\n[ERROR] No se pudieron preparar las matrices de prueba")
        return 1
    
    # Step 3: Deploy Infrastructure (creates S3 bucket)
    if not deploy_infrastructure():
        print("\n[ERROR] El despliegue no se completó correctamente")
        return 1
    
    # Step 4: Upload to S3 (now that bucket exists)
    if not upload_matrices_to_s3():
        print("\n[ERROR] No se pudieron subir las matrices a S3")
        print("[!] Los EC2 instances están corriendo pero sin matrices")
        print("[!] Sube manualmente o ejecuta: python utils/start/upload_to_s3.py")
        if not yes_no("\n¿Deseas continuar de todas formas?", default_yes=False):
            return 1
    
    # Success!
    print_header("EXPERIMENTO INICIADO EXITOSAMENTE")
    print("Próximos pasos:")
    print("  1. Ejecuta 'python scripts/2_monitor.py' para monitorear progreso")
    print("  2. Cuando termine, usa 'python scripts/3_results.py' para analizar")
    print("\nPara destruir infraestructura después:")
    print("  python utils/start/deploy.py destroy")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario")
        sys.exit(130)
