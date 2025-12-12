#!/usr/bin/env python3
"""
Script 3: PROCESAR RESULTADOS
Descarga, analiza y visualiza los resultados del benchmark.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.results.verify_visualizations import verify_visualizations

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_menu():
    """Print results menu"""
    print("\n" + "-"*70)
    print("OPCIONES DE RESULTADOS:")
    print("-"*70)
    print("  1. Descargar resultados desde S3")
    print("  2. Analizar resultados (estadísticas)")
    print("  3. Generar visualizaciones")
    print("  4. Verificar datos de visualizaciones")
    print("  5. Pipeline completo (descargar + analizar + visualizar)")
    print("  6. Abrir carpeta de resultados")
    print("  7. Abrir carpeta de visualizaciones")
    print("  0. Salir")
    print("-"*70)

def run_command(cmd, description):
    """Run a command and show output, return exit code"""
    print(f"\n[+] {description}...\n")
    try:
        result = subprocess.run(cmd, shell=True, check=False)  # Don't raise exception
        if result.returncode == 0:
            print(f"\n[OK] {description} completado")
            return True
        else:
            print(f"\n[ERROR] {description} falló con código {result.returncode}")
            return False
    except Exception as e:
        print(f"\n[ERROR] {description} falló: {e}")
        return False

def download_results(auto_mode=False):
    """Download results from S3"""
    script = str(Path(__file__).parent.parent / "utils" / "results" / "download_results.py")
    if not os.path.exists(script):
        print(f"[ERROR] No se encontró {script}")
        return False
    
    if auto_mode:
        # In auto mode, download immediately without waiting
        return run_command(f"python {script} --auto", "Descargar resultados")
    
    print("\nOpciones de descarga:")
    print("  1. Descargar inmediatamente (si ya están listos)")
    print("  2. Esperar a que terminen y luego descargar")
    
    try:
        choice = input("\nSelecciona opción [1-2]: ").strip()
    except EOFError:
        print("\n[INFO] Modo automático: descargando inmediatamente")
        return run_command(f"python {script}", "Descargar resultados")
    
    if choice == "1":
        return run_command(f"python {script}", "Descargar resultados")
    elif choice == "2":
        return run_command(f"python {script} --wait", 
                         "Esperar y descargar resultados")
    else:
        print("[ERROR] Opción inválida")
        return False

def analyze_results():
    """Analyze downloaded results"""
    script = str(Path(__file__).parent.parent / "utils" / "results" / "analyze_results.py")
    if not os.path.exists(script):
        print(f"[ERROR] No se encontró {script}")
        return False
    
    if not os.path.exists("benchmark_results"):
        print("\n[ERROR] No se encontró la carpeta benchmark_results/")
        print("[!] Ejecuta primero la opción 1 para descargar resultados")
        return False
    
    return run_command(f"python {script} --no-download", "Analizar resultados")

def generate_visualizations():
    """Generate visualizations from results"""
    script = str(Path(__file__).parent.parent / "src" / "visualization" / "generate_visualizations.py")
    if not os.path.exists(script):
        print(f"[ERROR] No se encontró {script}")
        return False
    
    if not os.path.exists("benchmark_results"):
        print("\n[ERROR] No se encontró la carpeta benchmark_results/")
        print("[!] Ejecuta primero la opción 1 para descargar resultados")
        return False
    
    return run_command(f"python {script}", "Generar visualizaciones")

def run_full_pipeline(auto_confirm=False):
    """Run complete pipeline: download + analyze + visualize"""
    print_header("PIPELINE COMPLETO DE RESULTADOS")
    
    if not auto_confirm:
        print("\nEste proceso ejecutará:")
        print("  1. Descarga de resultados desde S3")
        print("  2. Análisis estadístico")
        print("  3. Generación de visualizaciones")
        print("  4. Verificación de datos")
        
        try:
            response = input("\n¿Continuar? [S/n]: ").strip().lower()
        except EOFError:
            print("\n[INFO] Modo automático: ejecutando pipeline completo")
            auto_confirm = True
        else:
            if response and response not in ['s', 'si', 'y', 'yes']:
                print("[!] Pipeline cancelado")
                return False
            auto_confirm = True
    
    if auto_confirm:
        # Step 1: Download
        print("\n" + "="*70)
        print("PASO 1/4: DESCARGA DE RESULTADOS")
        print("="*70)
        if not download_results(auto_mode=True):
            print("[ERROR] La descarga falló o fue cancelada. Abortando pipeline.")
            return False
        
        # Step 2: Analyze
        print("\n" + "="*70)
        print("PASO 2/4: ANÁLISIS ESTADÍSTICO")
        print("="*70)
        if not run_command(f"python {Path(__file__).parent.parent / 'utils' / 'results' / 'analyze_results.py'} --no-download", "Analizar resultados"):
            print("[!] El análisis falló, pero continuando...")
        
        # Step 3: Visualize
        print("\n" + "="*70)
        print("PASO 3/4: GENERACIÓN DE VISUALIZACIONES")
        print("="*70)
        if not generate_visualizations():
            print("[!] La visualización falló, pero continuando...")
        
        # Step 4: Verify
        print("\n" + "="*70)
        print("PASO 4/4: VERIFICACIÓN DE DATOS")
        print("="*70)
        verify_visualizations()
        
        print_header("PIPELINE COMPLETADO")
        print("Resultados disponibles en:")
        print("  - Datos: benchmark_results/")
        print("  - Gráficos: visualizations/")
        
        return True

def open_results_folder():
    """Open results folder in file explorer"""
    if not os.path.exists("benchmark_results"):
        print("\n[ERROR] La carpeta benchmark_results/ no existe")
        print("[!] Ejecuta primero la opción 1 para descargar resultados")
        return False
    
    try:
        if sys.platform == "win32":
            os.startfile("benchmark_results")
        elif sys.platform == "darwin":
            subprocess.run(["open", "benchmark_results"])
        else:
            subprocess.run(["xdg-open", "benchmark_results"])
        print("\n[OK] Carpeta benchmark_results/ abierta en el explorador")
        return True
    except Exception as e:
        print(f"\n[ERROR] No se pudo abrir la carpeta: {e}")
        return False

def open_figures_folder():
    """Open visualizations folder in file explorer"""
    if not os.path.exists("visualizations"):
        print("\n[ERROR] La carpeta visualizations/ no existe")
        print("[!] Ejecuta primero la opción 3 para generar visualizaciones")
        return False
    
    try:
        if sys.platform == "win32":
            os.startfile("visualizations")
        elif sys.platform == "darwin":
            subprocess.run(["open", "visualizations"])
        else:
            subprocess.run(["xdg-open", "visualizations"])
        print("\n[OK] Carpeta visualizations/ abierta en el explorador")
        return True
    except Exception as e:
        print(f"\n[ERROR] No se pudo abrir la carpeta: {e}")
        return False

def main():
    """Main function with command line support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process benchmark results')
    parser.add_argument('--download', action='store_true', 
                       help='Download results from S3')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze downloaded results')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualizations')
    parser.add_argument('--verify', action='store_true',
                       help='Verify visualization data integrity')
    parser.add_argument('--pipeline', action='store_true',
                       help='Run complete pipeline')
    parser.add_argument('--open-results', action='store_true',
                       help='Open results folder')
    parser.add_argument('--open-figures', action='store_true',
                       help='Open figures folder')
    
    args = parser.parse_args()
    
    # If command line arguments provided, execute them
    if any([args.download, args.analyze, args.visualize, args.verify, args.pipeline, 
            args.open_results, args.open_figures]):
        
        print_header("SCRIPT 3: PROCESAR RESULTADOS DEL BENCHMARK")
        
        if args.download:
            download_results()
        if args.analyze:
            analyze_results()
        if args.visualize:
            generate_visualizations()
        if args.verify:
            verify_visualizations()
        if args.pipeline:
            run_full_pipeline(auto_confirm=True)
        if args.open_results:
            open_results_folder()
        if args.open_figures:
            open_figures_folder()
        
        return 0
    
    # Interactive mode
    print_header("SCRIPT 3: PROCESAR RESULTADOS DEL BENCHMARK")
    
    while True:
        print_menu()
        
        try:
            choice = input("\nSelecciona una opción [0-7]: ").strip()
        except EOFError:
            # No interactive input available, exit gracefully
            print("\n[!] No hay entrada interactiva disponible.")
            print("[INFO] Usa argumentos de línea de comandos:")
            print("       --download    Descargar resultados")
            print("       --analyze     Analizar resultados") 
            print("       --visualize   Generar visualizaciones")
            print("       --verify      Verificar datos de visualizaciones")
            print("       --pipeline    Pipeline completo")
            print("       --open-results Abrir carpeta resultados")
            print("       --open-figures Abrir carpeta figuras")
            break
        
        if choice == "1":
            download_results()
        elif choice == "2":
            analyze_results()
        elif choice == "3":
            generate_visualizations()
        elif choice == "4":
            verify_visualizations()
        elif choice == "5":
            run_full_pipeline()
        elif choice == "6":
            open_results_folder()
        elif choice == "7":
            open_figures_folder()
        elif choice == "0":
            print("\n[!] Saliendo...")
            break
        else:
            print("\n[ERROR] Opción inválida. Intenta de nuevo.")
        
        try:
            input("\nPresiona Enter para continuar...")
        except EOFError:
            # Input from pipe, exit after single operation
            break
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario")
        sys.exit(130)
