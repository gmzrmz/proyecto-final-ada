# Estructura de Resultados - Matrix Crossing Benchmark

## Ubicación
Todos los resultados descargados están en: `benchmark_results/`

## Estructura de Archivos

```
benchmark_results/
├── backtracking_20251207_050340/
│   └── benchmark_backtracking_20251207_050340.json
├── brute_force_20251207_064356/
│   └── benchmark_brute_force_20251207_064356.json
├── divide_and_conquer_20251207_065014/
│   └── benchmark_divide_and_conquer_20251207_065014.json
├── memoization_20251207_044535/
│   └── benchmark_memoization_20251207_044535.json
└── tabulation_20251207_044534/
    └── benchmark_tabulation_20251207_044534.json
```

## Formato de Datos (JSON)

Cada archivo JSON contiene:

```json
{
  "metadata": {
    "generated_at": "2025-12-10T23:08:14.870800",
    "total_results": 104
  },
  "results": [
    {
      "algorithm": "brute_force",
      "matrix_type": "random_small_seed42",
      "matrix_rows": 7,
      "matrix_cols": 15,
      "start_position": 0,
      "execution_time_seconds": 12.139556313,
      "path": [[0,0], [1,0], [2,0], [3,0], [4,6], [5,6], [6,5], [7,4], [8,4], [9,4], [10,4], [11,3], [12,2], [13,3], [14,2]],
      "path_cost": -416.09253825597295,
      "timestamp": "2025-12-10T21:02:33.080439",
      "instance_id": "72c0a02e7352",
      "timed_out": false,
      "error_message": null,
      "peak_memory_kb": 2.65
    },
    {
      "algorithm": "backtracking",
      "matrix_type": "random_medium_seed42",
      "matrix_rows": 15,
      "matrix_cols": 31,
      "start_position": 0,
      "execution_time_seconds": 120.0,
      "path": null,
      "path_cost": null,
      "timestamp": "2025-12-10T21:02:33.080439",
      "instance_id": "72c0a02e7352",
      "timed_out": true,
      "error_message": "Execution timed out after 120.0 seconds",
      "peak_memory_kb": null
    }
  ]
}
```

## Campos por Resultado

### Metadatos Globales (metadata)
- `generated_at`: Timestamp de generación del archivo
- `total_results`: Número total de tests ejecutados (104)

### Campos de Cada Test (results[])
- `algorithm`: Nombre del algoritmo ejecutado
- `matrix_type`: Tipo y semilla de la matriz (ej: "random_small_seed42")
- `matrix_rows`: Número de filas de la matriz
- `matrix_cols`: Número de columnas de la matriz
- `start_position`: Posición inicial (siempre 0)

### Estado de Ejecución
- `execution_time_seconds`: Tiempo de ejecución en segundos
- `timed_out`: `true` si hubo timeout, `false` si completó
- `error_message`: Mensaje de error (null si no hay error)
- `timestamp`: Momento exacto de ejecución
- `instance_id`: ID de la instancia EC2 que ejecutó el test

### Resultados del Camino
- `path`: Lista de coordenadas [fila, columna] del camino óptimo (null si timeout)
- `path_cost`: Costo total del camino encontrado (null si timeout)

### Métricas de Memoria
- `peak_memory_kb`: Consumo máximo de memoria durante la ejecución en KB con precisión de 2 decimales

## Métricas de Rendimiento

### Uso de Memoria
Se registra el consumo máximo de memoria durante la ejecución mediante el módulo `tracemalloc` de Python. Se reporta en **kilobytes (KB)** con precisión de dos decimales.

**Implementación técnica:**
- Usa `tracemalloc.start()` al inicio de cada ejecución
- Mide `tracemalloc.get_traced_memory()` para obtener el pico
- Convierte de bytes a KB: `peak / 1024`
- Redondea a 2 decimales para consistencia

## Procesamiento de Resultados

### Script Automatizado (Recomendado)

```bash
# Pipeline completo: descargar + analizar + visualizar + verificar
python scripts/3_results.py --pipeline --verify

# O comandos individuales:
python scripts/3_results.py --download    # Solo descargar
python scripts/3_results.py --analyze     # Solo analizar
python scripts/3_results.py --visualize   # Solo visualizar
python scripts/3_results.py --verify      # Solo verificar
```

### Menú Interactivo

```bash
python scripts/3_results.py
# Menú con opciones:
# 1. Descargar resultados desde S3
# 2. Analizar resultados (estadísticas)
# 3. Generar visualizaciones
# 4. Verificar integridad de datos
# 5. Pipeline completo
```

## Análisis y Visualizaciones

### Generar Visualizaciones

Después de descargar los resultados, genera gráficos comparativos:

```bash
# Generar todas las visualizaciones
python src/visualization/generate_visualizations.py
```

Esto crea gráficos en `visualizations/`:
- **PNG**: 5 gráficos de comparación (`1_` to `5_`)
- **PDF**: 4 gráficos detallados (boxplots, speedup, etc.)
- **CSV**: `statistics_summary.csv` con estadísticas detalladas

### Ideas de Análisis

- **Rendimiento por tamaño**: Tiempo vs dimensión de matriz
- **Tasa de éxito**: % completadas por algoritmo y tamaño
- **Distribución de timeouts**: Qué tipos de matrices causan timeouts
- **Comparación de caminos**: Verificar que todos encuentran el mismo `min_cost`
- **Escalabilidad**: Cómo crece el tiempo con el tamaño (complejidad empírica)

## Acceso Programático

### Python Example

```python
import json

# Cargar resultados de un algoritmo
with open('benchmark_results/benchmark_backtracking_20251207_050340.json') as f:
    data = json.load(f)

# Acceder a metadatos
total = data['metadata']['total_results']  # 104
generated = data['metadata']['generated_at']

# Filtrar tests exitosos (sin timeout)
successful = [r for r in data['results'] if not r['timed_out']]
print(f"Tests completados: {len(successful)}/{total}")

# Análisis por tipo de matriz
by_type = {}
for test in data['results']:
    mtype = test['matrix_type'].split('_seed')[0]  # "random_small"
    if mtype not in by_type:
        by_type[mtype] = {'completed': 0, 'total': 0, 'times': []}
    
    by_type[mtype]['total'] += 1
    if not test['timed_out']:
        by_type[mtype]['completed'] += 1
        by_type[mtype]['times'].append(test['execution_time_seconds'])

# Estadísticas por tipo
for mtype, stats in sorted(by_type.items()):
    if stats['times']:
        avg = sum(stats['times']) / len(stats['times'])
        success_rate = (stats['completed'] / stats['total']) * 100
        print(f"{mtype}: {success_rate:.1f}% success, {avg*1000:.2f} ms avg")
```

## Verificación de Integridad

El sistema incluye verificación automática de integridad de datos:

```bash
# Verificar datos existentes
python scripts/3_results.py --verify

# Verificar después del pipeline completo
python scripts/3_results.py --pipeline --verify
```

### Verificaciones realizadas:

- **Archivos de visualización**: Existencia de todos los archivos requeridos
- **Datos de benchmark**: Consistencia de resultados JSON
- **Estadísticas**: Coincidencia entre algoritmos en datos y CSV
- **Tamaños de archivo**: Detección de archivos corruptos

### Salida de ejemplo:
```
[+] Verificando datos de visualizaciones...
  [OK] Directorio de visualizaciones encontrado
  [OK] Todos los 9 archivos de visualizacion existen
  [OK] Estadisticas consistentes con datos originales

============================================================
RESUMEN DE VERIFICACION
============================================================
[OK] Todas las verificaciones pasaron exitosamente!
```

## Notas Importantes

1. **Timeouts**: Configurados en 60-240s según tamaño de matriz
2. **Matrices de prueba**: 104 total (39 presets + 65 complexity variants)
3. **Reproducibilidad**: Cada test tiene seed fija para reproducir resultados
4. **Path format**: Coordenadas en formato [fila, columna] siguiendo convención Python
5. **Verificación**: Usa `--verify` para validar integridad de datos y visualizaciones
