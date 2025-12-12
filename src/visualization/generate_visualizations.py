#!/usr/bin/env python3
"""
Generate visualizations from benchmark results.
Run this after collecting results from all EC2 instances.

Usage:
    python src/visualization/generate_visualizations.py

Note: Automatically loads all benchmark_*.json files from benchmark_results/ directory.
Supports partial results (works with 1-5 completed algorithms).
"""

import json
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

def setup_matplotlib():
    """Setup matplotlib with custom font and styling"""
    # Try to use custom font from the original code
    try:
        import requests
        url = "http://juamdg.web.app/font/matplotlib.otf"
        data = requests.get(url, timeout=5).content
        with open("font.otf", "wb") as f:
            f.write(data)
        
        fname = "font.otf"
        fm.fontManager.addfont(fname)
        font_name = fm.FontProperties(fname=fname).get_name()
        
        sns.set_theme(rc={"font.family": "serif", "font.serif": [font_name]})
        
        plt.rcParams.update({
            "font.family": "serif",
            "font.serif": [font_name],
            "font.size": 10,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "mathtext.fontset": "dejavuserif",
            "mathtext.rm": font_name,
            "mathtext.it": font_name,
            "mathtext.bf": font_name
        })
    except:
        # Fallback to DejaVu Serif (better math symbol support)
        sns.set(style="whitegrid")
        plt.rcParams.update({
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Latin Modern Roman", "Computer Modern Roman"],
            "font.size": 10,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "mathtext.fontset": "dejavuserif"
        })

def load_benchmark_data():
    """Load all benchmark results from JSON files"""
    results_dir = Path('benchmark_results')
    
    if not results_dir.exists():
        print("[ERROR] No se encontró el directorio benchmark_results/")
        print("[INFO] Ejecuta primero la descarga desde S3")
        return None
    
    # Find all benchmark JSON files (not metadata files)
    benchmark_files = list(results_dir.glob('*/benchmark_*.json'))
    
    if not benchmark_files:
        print("[ERROR] No se encontraron archivos de benchmark (benchmark_*.json)")
        print("[INFO] Resultados parciales solo contienen pruebas unitarias o los benchmarks siguen en ejecución")
        return None
    
    print(f"[OK] Cargando {len(benchmark_files)} archivo(s) de benchmark...")
    
    all_results = []
    for json_file in benchmark_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_results.extend(data['results'])
        except Exception as e:
            print(f"[WARNING] Error al cargar {json_file.name}: {e}")
    
    if not all_results:
        print("[ERROR] No se encontraron datos de benchmark en los archivos")
        return None
    
    print(f"[OK] Se cargaron {len(all_results)} resultados de benchmark")
    return all_results

def generate_comparison_by_type(df_success, algorithm_labels):
    """Generate bar chart comparing algorithms by matrix type"""
    print("  [1/4] Comparación de algoritmos por tipo de matriz...")
    
    # Main matrix types (use what's available)
    main_types = ['random_small', 'random_medium', 'wavy_small', 'wavy_medium',
                  'turbulent_small', 'paraboloid_small', 'valley_small']
    df_main = df_success[df_success['base_type'].isin(main_types)]
    
    if len(df_main) == 0:
        print("  [WARNING] No se encontraron los tipos principales de matriz, usando todos los disponibles")
        df_main = df_success
    
    # Calculate average time
    avg_times = df_main.groupby(['base_type', 'algorithm'])['execution_time_seconds'].mean().reset_index()
    pivot_table = avg_times.pivot(index='base_type', columns='algorithm', values='execution_time_seconds')
    
    # Get available algorithms
    algorithm_order = ['tabulation', 'memoization', 'divide_and_conquer', 'backtracking', 'brute_force']
    available_algos = [a for a in algorithm_order if a in pivot_table.columns]
    pivot_table = pivot_table.reindex(columns=available_algos, fill_value=np.nan)
    
    # Create chart
    fig, ax = plt.subplots(figsize=(14, 8))
    x = np.arange(len(pivot_table.index))
    width = 0.15
    colors = ['#080', '#36c', '#888', '#000', '#f00']
    
    for i, algo in enumerate(available_algos):
        offset = width * (i - len(available_algos)/2 + 0.5)
        values = pivot_table[algo].values
        
        for j, (pos, val) in enumerate(zip(x, values)):
            if not np.isnan(val) and val > 0:
                ax.bar(pos + offset, val, width,
                      color=colors[algorithm_order.index(algo)],
                      edgecolor='white', linewidth=0.5)
                ax.text(pos + offset, val, f'{val*1000:.1f}',
                       ha='center', va='bottom', fontsize=7)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=colors[algorithm_order.index(algo)],
                            edgecolor='white',
                            label=algorithm_labels.get(algo, algo.title()))
                      for algo in available_algos]
    
    ax.set_xlabel('Tipo de Matriz', fontsize=12)
    ax.set_ylabel('Tiempo Promedio (segundos)', fontsize=12)
    ax.set_title('Comparación de Algoritmos por Tipo de Matriz', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([t.replace('_', ' ').title() for t in pivot_table.index], rotation=25, ha='right')
    ax.legend(handles=legend_elements, fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig('visualizations/1_comparison_by_type.png', dpi=150, bbox_inches='tight')
    plt.close()

def generate_complexity_analysis(df_success, algorithm_labels):
    """Generate line chart for complexity analysis"""
    print("  [2/4] Análisis de complejidad...")
    
    df_square = df_success[df_success['matrix_type'].str.contains('square')].copy()
    
    if len(df_square) == 0:
        print("  [WARNING] No se encontraron matrices cuadradas, omitiendo análisis de complejidad")
        return
    
    df_square['matrix_size'] = df_square['matrix_rows']
    complexity_data = df_square.groupby(['algorithm', 'matrix_size'])['execution_time_seconds'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    algorithm_order = ['tabulation', 'memoization', 'divide_and_conquer', 'backtracking', 'brute_force']
    colors = ['#080', '#36c', '#888', '#000', '#f00']
    markers = ['v', 'd', '^', 's', 'o']
    
    for idx, algo in enumerate(algorithm_order):
        algo_data = complexity_data[complexity_data['algorithm'] == algo].sort_values('matrix_size')
        if not algo_data.empty:
            ax.plot(algo_data['matrix_size'],
                   algo_data['execution_time_seconds'],
                   label=algorithm_labels.get(algo, algo.title()),
                   marker=markers[idx],
                   color=colors[idx],
                   linewidth=2,
                   markersize=6)
    
    ax.set_xlabel('Tamaño de Matriz (filas)', fontsize=12)
    ax.set_ylabel('Tiempo de Ejecución (segundos)', fontsize=12)
    ax.set_title('Análisis de Complejidad', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Set y-axis limits to show full range (don't cut off at 10^-2)
    # Let matplotlib choose appropriate range based on data
    ax.set_ylim(bottom=None, top=None)
    
    plt.tight_layout()
    plt.savefig('visualizations/2_complexity_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()

def generate_success_rate(df, algorithm_labels):
    """Generate bar chart for success rate"""
    print("  [3/4] Tasa de éxito por algoritmo...")
    
    success_rate = df.groupby('algorithm').apply(
        lambda x: (x['timed_out'] == False).sum() / len(x) * 100,
        include_groups=False
    ).reset_index(name='success_rate')
    
    algorithm_order = ['tabulation', 'memoization', 'divide_and_conquer', 'backtracking', 'brute_force']
    available_algos = [a for a in algorithm_order if a in success_rate['algorithm'].values]
    success_rate = success_rate.set_index('algorithm').reindex(available_algos).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#080', '#36c', '#888', '#000', '#f00']
    colors_subset = [colors[algorithm_order.index(a)] for a in available_algos]
    
    bars = ax.bar(range(len(success_rate)),
                  success_rate['success_rate'],
                  color=colors_subset,
                  edgecolor='white',
                  linewidth=0.5)
    
    for bar, rate in zip(bars, success_rate['success_rate']):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{rate:.1f}%',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Algoritmo', fontsize=12)
    ax.set_ylabel('Tasa de Éxito (%)', fontsize=12)
    ax.set_title('Tasa de Éxito por Algoritmo', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(success_rate)))
    ax.set_xticklabels([algorithm_labels.get(a, a.title()) for a in success_rate['algorithm']],
                       rotation=15, ha='right')
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('visualizations/3_success_rate.png', dpi=150, bbox_inches='tight')
    plt.close()

def generate_time_summary(df_success, algorithm_labels):
    """Generate horizontal bar chart for average times"""
    print("  [4/4] Resumen de tiempo promedio...")
    
    avg_time = df_success.groupby('algorithm')['execution_time_seconds'].mean().reset_index()
    
    algorithm_order = ['tabulation', 'memoization', 'divide_and_conquer', 'backtracking', 'brute_force']
    available_algos = [a for a in algorithm_order if a in avg_time['algorithm'].values]
    avg_time = avg_time.set_index('algorithm').reindex(available_algos).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#080', '#36c', '#888', '#000', '#f00']
    colors_subset = [colors[algorithm_order.index(a)] for a in available_algos]
    
    bars = ax.barh(range(len(avg_time)),
                   avg_time['execution_time_seconds'],
                   color=colors_subset,
                   edgecolor='white',
                   linewidth=0.5)
    
    for bar, time_val in zip(bars, avg_time['execution_time_seconds']):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f' {time_val*1000:.2f} ms',
               ha='left', va='center', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Algoritmo', fontsize=12)
    ax.set_xlabel('Tiempo Promedio (segundos)', fontsize=12)
    ax.set_title('Tiempo Promedio de Ejecución', fontsize=14, fontweight='bold')
    ax.set_yticks(range(len(avg_time)))
    ax.set_yticklabels([algorithm_labels.get(a, a.title()) for a in avg_time['algorithm']])
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('visualizations/4_time_summary.png', dpi=150, bbox_inches='tight')
    plt.close()


def generate_memory_summary(df_success, algorithm_labels):
    """Generate memory usage summary chart"""
    print("  [5/5] Resumen de uso de memoria...")
    
    if 'peak_memory_kb' not in df_success.columns:
        print("  [SKIP] No hay datos de memoria disponibles")
        return
    
    # Filter out results without memory data
    df_memory = df_success.dropna(subset=['peak_memory_kb'])
    
    if len(df_memory) == 0:
        print("  [SKIP] No hay datos de memoria válidos")
        return
    
    print(f"  [OK] Procesando {len(df_memory)} registros con datos de memoria")
    
    avg_memory = df_memory.groupby('algorithm')['peak_memory_kb'].mean().reset_index()
    print(f"  [OK] Promedio calculado: {avg_memory.iloc[0]['peak_memory_kb']:.2f} KB")
    
    algorithm_order = ['tabulation', 'memoization', 'divide_and_conquer', 'backtracking', 'brute_force']
    available_algos = [a for a in algorithm_order if a in avg_memory['algorithm'].values]
    avg_memory = avg_memory.set_index('algorithm').reindex(available_algos).reset_index()
    
    print("  [OK] Generando gráfica de memoria...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#080', '#36c', '#888', '#000', '#f00']
    colors_subset = [colors[algorithm_order.index(a)] for a in available_algos]
    
    bars = ax.barh(range(len(avg_memory)),
                   avg_memory['peak_memory_kb'],
                   color=colors_subset,
                   edgecolor='white',
                   linewidth=0.5)
    
    for bar, mem_val in zip(bars, avg_memory['peak_memory_kb']):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
               f' {mem_val:.1f} KB',
               ha='left', va='center', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('Algoritmo', fontsize=12)
    ax.set_xlabel('Memoria Promedio (KB)', fontsize=12)
    ax.set_title('Uso Promedio de Memoria', fontsize=14, fontweight='bold')
    ax.set_yticks(range(len(avg_memory)))
    ax.set_yticklabels([algorithm_labels.get(a, a.title()) for a in avg_memory['algorithm']])
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('visualizations/5_memory_summary.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("  [OK] Gráfica de memoria guardada")


def main():
    print("="*60)
    print("GENERANDO VISUALIZACIONES DE LOS RESULTADOS DEL BENCHMARK")
    print("="*60)
    print()
    
    # Setup matplotlib
    setup_matplotlib()
    
    # Load data
    all_results = load_benchmark_data()
    if all_results is None:
        return 1
    
    # Convert to DataFrame
    df = pd.DataFrame(all_results)
    
    # Filter successful results
    df_success = df[df['timed_out'] == False].copy()
    print(f"[OK] {len(df_success)} resultados exitosos (sin timeouts)")
    
    if len(df_success) == 0:
        print("[ERROR] No hay benchmarks exitosos para visualizar (todos timeout o error)")
        return 1
    
    # Algorithm labels
    algorithm_labels = {
        'brute_force': 'Fuerza Bruta',
        'backtracking': 'Backtracking',
        'divide_and_conquer': 'Divide & Conquer',
        'memoization': 'Memorización',
        'tabulation': 'Tabulación'
    }
    
    df_success['algorithm_label'] = df_success['algorithm'].map(
        lambda x: algorithm_labels.get(x, x.title())
    )
    
    # Extract base matrix type
    df_success['base_type'] = df_success['matrix_type'].str.replace(r'_seed\d+', '', regex=True)
    
    # Create output directory
    os.makedirs('visualizations', exist_ok=True)
    
    # Generate visualizations
    print("\n[OK] Generando visualizaciones...")
    
    try:
        generate_comparison_by_type(df_success, algorithm_labels)
        generate_complexity_analysis(df_success, algorithm_labels)
        generate_success_rate(df, algorithm_labels)
        generate_time_summary(df_success, algorithm_labels)
        generate_memory_summary(df_success, algorithm_labels)
        
        # New enhanced visualizations from original code
        generate_enhanced_boxplots(df_success, algorithm_labels)
        generate_individual_boxplots(df_success, algorithm_labels)
        generate_speedup_analysis(df_success, algorithm_labels)
        generate_detailed_statistics(df_success, algorithm_labels)
        
        print("\n" + "="*60)
        print("[OK] ¡Todas las visualizaciones se generaron exitosamente!")
        print(f"[OK] Carpeta de salida: visualizations/")
        print("="*60)
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Visualization generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def generate_enhanced_boxplots(df_success, algorithm_labels):
    """Generate enhanced boxplots with better visibility and statistics"""
    print("  [5/8] Boxplots mejorados con estadísticas...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Algorithm order
    order = sorted(df_success["algorithm"].unique())
    
    # --- GRÁFICO 1: Escala logarítmica ---
    data_to_plot = [df_success[df_success["algorithm"] == alg]["execution_time_seconds"] for alg in order]
    
    bp1 = ax1.boxplot(data_to_plot,
                      tick_labels=[algorithm_labels.get(alg, alg.title()) for alg in order],
                      showmeans=True,
                      meanprops=dict(marker='D', markerfacecolor='red', markersize=8),
                      medianprops=dict(color='blue', linewidth=2),
                      boxprops=dict(linewidth=2),
                      whiskerprops=dict(linewidth=1.5),
                      capprops=dict(linewidth=1.5),
                      flierprops=dict(marker='o', markerfacecolor='gray', markersize=5, alpha=0.5))
    
    ax1.set_yscale('log')
    ax1.set_title("Distribución de tiempos (escala logarítmica)", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Tiempo (s) - escala log", fontsize=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    ax1.tick_params(axis='x', rotation=45)
    
    # --- GRÁFICO 2: Sin outliers extremos ---
    threshold = df_success["execution_time_seconds"].quantile(0.95)
    df_filtered = df_success[df_success["execution_time_seconds"] <= threshold].copy()
    
    data_to_plot_filtered = [df_filtered[df_filtered["algorithm"] == alg]["execution_time_seconds"]
                             for alg in order]
    
    bp2 = ax2.boxplot(data_to_plot_filtered,
                      tick_labels=[algorithm_labels.get(alg, alg.title()) for alg in order],
                      showmeans=True,
                      meanprops=dict(marker='D', markerfacecolor='red', markersize=8),
                      medianprops=dict(color='blue', linewidth=2),
                      boxprops=dict(linewidth=2),
                      whiskerprops=dict(linewidth=1.5),
                      capprops=dict(linewidth=1.5),
                      flierprops=dict(marker='o', markerfacecolor='gray', markersize=5, alpha=0.5))
    
    ax2.set_title(f"Sin outliers extremos (<= p95: {threshold:.2f}s)",
                  fontsize=14, fontweight='bold')
    ax2.set_ylabel("Tiempo (s)", fontsize=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.6)
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('visualizations/enhanced_boxplots.pdf', format='pdf', bbox_inches='tight')
    plt.close()


def generate_individual_boxplots(df_success, algorithm_labels):
    """Generate individual boxplots for each algorithm"""
    print("  [6/8] Boxplots individuales por algoritmo...")
    
    algorithms = sorted(df_success["algorithm"].unique())
    n_algorithms = len(algorithms)
    fig, axes = plt.subplots(1, n_algorithms, figsize=(4*n_algorithms, 6), sharey=False)
    
    if n_algorithms == 1:
        axes = [axes]
    
    for idx, alg in enumerate(algorithms):
        alg_data = df_success[df_success["algorithm"] == alg]["execution_time_seconds"]
        
        axes[idx].boxplot([alg_data],
                          showmeans=True,
                          meanprops=dict(marker='D', markerfacecolor='red', markersize=10),
                          medianprops=dict(color='blue', linewidth=2.5),
                          boxprops=dict(linewidth=2.5, color='darkblue'),
                          whiskerprops=dict(linewidth=2),
                          capprops=dict(linewidth=2),
                          flierprops=dict(marker='o', markerfacecolor='orange',
                                         markersize=6, alpha=0.6))
        
        axes[idx].set_title(f"{algorithm_labels.get(alg, alg.title())}\n(n={len(alg_data)})", 
                           fontsize=12, fontweight='bold')
        axes[idx].set_ylabel("Tiempo (s)", fontsize=11)
        axes[idx].grid(axis='y', linestyle='--', alpha=0.6)
        axes[idx].set_xticks([])
        
        # Add statistics
        stats_text = f"Media: {alg_data.mean():.3f}s\nMediana: {alg_data.median():.3f}s"
        axes[idx].text(0.95, 0.95, stats_text,
                       transform=axes[idx].transAxes,
                       fontsize=9, verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle("Distribución individual por algoritmo", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('visualizations/individual_boxplots.pdf', format='pdf', bbox_inches='tight')
    plt.close()


def generate_speedup_analysis(df_success, algorithm_labels):
    """Generate speedup analysis compared to brute force"""
    print("  [7/8] Análisis de speedup respecto a brute force...")
    
    if "brute_force" not in df_success["algorithm"].unique():
        print("    [SKIP] No existe brute_force en los datos")
        return
    
    # Calculate mean times by algorithm and matrix type
    mean_times = df_success.groupby(["algorithm", "base_type"])["execution_time_seconds"].mean().reset_index()
    bf_times = mean_times[mean_times["algorithm"] == "brute_force"] \
                .set_index("base_type")["execution_time_seconds"]
    
    speedup_data = []
    for _, row in mean_times.iterrows():
        alg = row["algorithm"]
        mtype = row["base_type"]
        t_alg = row["execution_time_seconds"]
        if mtype in bf_times.index and bf_times[mtype] > 0:
            speedup = bf_times[mtype] / t_alg
            speedup_data.append([alg, mtype, speedup])
    
    if not speedup_data:
        print("    [SKIP] No hay datos suficientes para speedup")
        return
    
    speed_df = pd.DataFrame(speedup_data, columns=["algorithm", "matrix_type", "speedup"])
    
    plt.figure(figsize=(12, 6))
    for alg in sorted(speed_df["algorithm"].unique()):
        if alg == "brute_force":
            continue
        subset = speed_df[speed_df["algorithm"] == alg]
        plt.plot(subset["matrix_type"], subset["speedup"],
                marker="o", markersize=8, linewidth=2.5, 
                label=algorithm_labels.get(alg, alg.title()))
    
    plt.yscale("log")
    plt.ylabel("Speedup (escala logarítmica)", fontsize=12)
    plt.xlabel("Tipo de matriz", fontsize=12)
    plt.title("Speedup acumulado por algoritmo respecto a brute force",
              fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/speedup_analysis.pdf', format='pdf', bbox_inches='tight')
    plt.close()


def generate_detailed_statistics(df_success, algorithm_labels):
    """Generate detailed statistics table and save to file"""
    print("  [8/8] Estadísticas detalladas...")
    
    print("\n" + "="*70)
    print("RESUMEN ESTADÍSTICO DETALLADO POR ALGORITMO")
    print("="*70)
    
    summary = df_success.groupby("algorithm")["execution_time_seconds"].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ]).round(4)
    
    # Add algorithm labels
    summary.index = [algorithm_labels.get(alg, alg.title()) for alg in summary.index]
    
    print(summary)
    
    # Save to CSV
    summary.to_csv('visualizations/statistics_summary.csv')
    print(f"\n[OK] Estadísticas guardadas en: visualizations/statistics_summary.csv")


if __name__ == "__main__":
    sys.exit(main())
