#!/usr/bin/env python3
"""
Visualization Data Verification Module
Provides functions to verify integrity and consistency of benchmark visualization data.
"""

import os
import json
import pandas as pd
from pathlib import Path


def verify_visualizations():
    """Verify visualization data integrity and consistency"""
    print("\n[+] Verificando datos de visualizaciones...")

    issues_found = []
    checks_passed = 0

    # Check 1: Verify visualizations directory exists
    viz_dir = Path("visualizations")
    if not viz_dir.exists():
        issues_found.append("Directorio 'visualizations/' no existe")
        return False
    else:
        print("  [OK] Directorio de visualizaciones encontrado")
        checks_passed += 1

    # Check 2: Verify expected visualization files exist
    expected_files = [
        "1_comparison_by_type.png",
        "2_complexity_analysis.png",
        "3_success_rate.png",
        "4_time_summary.png",
        "5_memory_summary.png",
        "enhanced_boxplots.pdf",
        "individual_boxplots.pdf",
        "speedup_analysis.pdf",
        "statistics_summary.csv"
    ]

    missing_files = []
    for filename in expected_files:
        if not (viz_dir / filename).exists():
            missing_files.append(filename)

    if missing_files:
        issues_found.append(f"Archivos faltantes: {', '.join(missing_files)}")
    else:
        print(f"  [OK] Todos los {len(expected_files)} archivos de visualizacion existen")
        checks_passed += 1

    # Check 3: Verify benchmark_results directory exists
    results_dir = Path("benchmark_results")
    if not results_dir.exists():
        issues_found.append("Directorio 'benchmark_results/' no existe")
        return False
    else:
        print("  [OK] Directorio de resultados encontrado")
        checks_passed += 1

    # Check 4: Load and verify data consistency
    try:
        # Load JSON data
        benchmark_files = list(results_dir.glob("*/benchmark_*.json"))
        if not benchmark_files:
            issues_found.append("No se encontraron archivos JSON de benchmark")
        else:
            all_results = []
            for json_file in benchmark_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_results.extend(data['results'])
                except Exception as e:
                    issues_found.append(f"Error cargando {json_file.name}: {e}")

            if all_results:
                df = pd.DataFrame(all_results)
                df_success = df[df['timed_out'] == False].copy()

                # Check data integrity
                total_results = len(df)
                success_results = len(df_success)
                algorithms = df['algorithm'].unique()

                print(f"  [OK] Datos cargados: {total_results} resultados totales")
                print(f"  [OK] Resultados exitosos: {success_results} ({success_results/total_results*100:.1f}%)")
                print(f"  [OK] Algoritmos encontrados: {', '.join(sorted(algorithms))}")
                checks_passed += 1

                # Check 5: Verify statistics consistency
                if (viz_dir / "statistics_summary.csv").exists():
                    try:
                        stats_df = pd.read_csv(viz_dir / "statistics_summary.csv", index_col=0)

                        # Verify algorithms match (normalize names)
                        # Map Spanish labels back to English algorithm names
                        spanish_to_english = {
                            'fuerza_bruta': 'brute_force',
                            'backtracking': 'backtracking',
                            'divide_and_conquer': 'divide_and_conquer',
                            'memorizacion': 'memoization',
                            'tabulacion': 'tabulation'
                        }

                        csv_algorithms = set()
                        for alg in stats_df.index:
                            # Normalize: lowercase, remove accents, replace spaces/underscores
                            normalized = alg.lower()
                            normalized = normalized.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                            normalized = normalized.replace(' ', '_').replace('&', 'and')
                            # Map Spanish to English if needed
                            if normalized in spanish_to_english:
                                normalized = spanish_to_english[normalized]
                            csv_algorithms.add(normalized)

                        data_algorithms_normalized = set()
                        for alg in algorithms:
                            normalized = alg.lower()
                            data_algorithms_normalized.add(normalized)

                        if csv_algorithms == data_algorithms_normalized:
                            print("  [OK] Estadisticas consistentes con datos originales")
                            checks_passed += 1
                        else:
                            issues_found.append(f"Discrepancia en algoritmos: CSV={csv_algorithms}, Datos={data_algorithms_normalized}")

                    except Exception as e:
                        issues_found.append(f"Error verificando estadisticas CSV: {e}")
                else:
                    issues_found.append("Archivo statistics_summary.csv no encontrado")

    except Exception as e:
        issues_found.append(f"Error verificando consistencia de datos: {e}")

    # Check 6: Verify file sizes are reasonable
    try:
        for filename in expected_files:
            filepath = viz_dir / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                if size_kb < 0.1:  # Less than 0.1KB might indicate corruption
                    issues_found.append(f"Archivo {filename} muy pequeno ({size_kb:.1f} KB) - posible corrupcion")
                elif size_kb > 10000:  # More than 10MB might indicate issues
                    issues_found.append(f"Archivo {filename} muy grande ({size_kb:.1f} KB)")

    except Exception as e:
        issues_found.append(f"Error verificando tamanos de archivo: {e}")

    # Summary
    print(f"\n{'='*60}")
    print("RESUMEN DE VERIFICACION")
    print(f"{'='*60}")

    if issues_found:
        print(f"[ERROR] {len(issues_found)} problema(s) encontrado(s):")
        for issue in issues_found:
            print(f"   {issue}")
        print(f"\n[OK] {checks_passed} verificacion(es) exitosa(s)")
        return False
    else:
        print("[OK] Todas las verificaciones pasaron exitosamente!")
        print(f"[OK] {checks_passed} verificacion(es) completada(s)")
        print("\n[INFO] Estado de las visualizaciones:")
        print(f"   • {len(expected_files)} archivos generados")
        print(f"   • {len(benchmark_files)} archivos de datos procesados")
        print(f"   • {len(algorithms)} algoritmos analizados")
        print(f"   • {success_results}/{total_results} benchmarks exitosos")
        return True