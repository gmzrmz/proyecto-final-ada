# Matrix Crossing Benchmark

Sistema de benchmark automatizado para comparar algoritmos que resuelven el problema de cruce de matriz con costo mínimo. Despliega infraestructura en AWS, ejecuta pruebas en paralelo y genera visualizaciones comparativas.

## Inicio Rápido

```bash
# 1. Desplegar infraestructura y ejecutar benchmarks
python scripts/1_iniciar.py

# 2. Monitorear progreso en tiempo real
python scripts/2_monitor.py

# 3. Descargar, analizar y verificar resultados
python scripts/3_results.py --pipeline --verify
```

Para guías completas de uso, consulta **[EJECUCION.md](docs/EJECUCION.md)**.

## Documentación

- **[docs/EJECUCION.md](docs/EJECUCION.md)** - Guía completa de uso, despliegue AWS y flujos de trabajo
- **[docs/RESULTADOS.md](docs/RESULTADOS.md)** - Análisis de resultados y comparación de algoritmos
- **[docs/INFRASTRUCTURE.md](infrastructure/INFRASTRUCTURE.md)** - Arquitectura de infraestructura Terraform

---

## Descripcion del Problema

Dado una matriz de costos `M` de dimensiones `m × n`, encontrar el camino de costo mínimo desde cualquier celda de la primera columna hasta cualquier celda de la última columna, con las siguientes restricciones:

- **Inicio**: Cualquier celda de la columna 0 (primera columna)
- **Fin**: Cualquier celda de la columna n-1 (última columna)
- **Movimientos permitidos**: Desde la celda `(fila, col)` solo se puede mover a:
  - `(fila-1, col+1)` - Diagonal superior
  - `(fila, col+1)` - Derecha
  - `(fila+1, col+1)` - Diagonal inferior
- **Wrapping**: Las filas hacen wrap-around (la fila -1 es la última fila, la fila m es la fila 0)

**Objetivo**: Minimizar la suma de los valores de las celdas visitadas.

### Ejemplo Visual

```
Matriz 4×5:
    0   1   2   3   4
  ┌───┬───┬───┬───┬───┐
0 │ 3 │ 2 │ 1 │ 4 │ 2 │
  ├───┼───┼───┼───┼───┤
1 │ 5 │ 1 │ 3 │ 2 │ 1 │
  ├───┼───┼───┼───┼───┤
2 │ 2 │ 4 │ 2 │ 1 │ 3 │
  ├───┼───┼───┼───┼───┤
3 │ 4 │ 3 │ 1 │ 2 │ 2 │
  └───┴───┴───┴───┴───┘

Camino óptimo: [(0,0), (1,1), (2,2), (2,3), (2,4)]
Costo total: 3 + 1 + 2 + 1 + 3 = 10
```

---

## Objetivo del Proyecto

Implementar, analizar y comparar **5 algoritmos diferentes** para resolver el problema:

1. **Brute Force** - Búsqueda exhaustiva pura (sin poda)
2. **Backtracking** - Búsqueda exhaustiva con poda (branch & bound)
3. **Divide & Conquer** - Recursión sin memoización
4. **Memoization** - Programación dinámica top-down
5. **Tabulation** - Programación dinámica bottom-up

El proyecto incluye:
- [x] Implementacion modular y testeable
- [x] Suite de 140 tests unitarios
- [x] Generadores de matrices de prueba (9 tipos diferentes)
- [x] Sistema de benchmarking automatizado
- [x] Visualizacion de resultados con verificacion de integridad
- [x] Infraestructura AWS/Terraform para ejecucion distribuida

---

## Estructura del Proyecto

```
proyecto-final-ada/
├── README.md                      # Este archivo
├── LICENSE                        # Licencia del proyecto
├── requirements.txt               # Dependencias Python
├── run_benchmark.py               # Script principal para ejecutar benchmarks (usado en EC2)
│
├── docs/                          # Documentación
│   ├── EJECUCION.md              # Guía completa de uso y despliegue AWS
│   ├── RESULTADOS.md             # Análisis de resultados
│   └── INFRASTRUCTURE.md         # Documentación de infraestructura
│
├── scripts/                       # Scripts de automatización (workflow completo)
│   ├── 1_iniciar.py              # Desplegar infraestructura y ejecutar benchmarks
│   ├── 2_monitor.py              # Monitorear progreso en tiempo real
│   └── 3_results.py              # Descargar, analizar y verificar resultados
│
├── src/                           # Código fuente principal
│   ├── algorithms/                # Implementaciones de algoritmos
│   │   ├── __init__.py           # Paquete de algoritmos
│   │   ├── brute_force.py        # O(3^n) búsqueda exhaustiva
│   │   ├── backtracking.py       # O(3^n) con poda
│   │   ├── divide_and_conquer.py # O(3^n) recursivo
│   │   ├── exhaustive.py         # O(3^n) variante
│   │   ├── memoization.py        # O(m×n) top-down DP
│   │   └── tabulation.py         # O(m×n) bottom-up DP
│   │
│   ├── matrix/                    # Generación de matrices
│   │   ├── __init__.py           # Paquete de matrices
│   │   ├── generators.py         # Funciones base (random, from_function)
│   │   └── presets.py            # 9 tipos predefinidos
│   │
│   ├── benchmark/                 # Sistema de benchmarking
│   │   ├── __init__.py           # Paquete de benchmark
│   │   ├── runner.py             # BenchmarkRunner, ejecución de pruebas
│   │   ├── results.py            # BenchmarkResult, exportación JSON/CSV
│   │   ├── unit_test_report.py   # Reportes de pruebas unitarias
│   │   └── upload_results.py     # Subida de resultados a S3
│   │
│   └── visualization/             # Generación de gráficos
│       ├── __init__.py           # Paquete de visualización
│       └── generate_visualizations.py # Generador de visualizaciones (desde benchmark_results/)
│
├── utils/                         # Utilidades auxiliares
│   ├── start/                     # Despliegue
│   │   ├── deploy.py             # Terraform apply/destroy
│   │   ├── generate_test_matrices.py  # Generador de matrices de prueba
│   │   └── upload_to_s3.py       # Subida de matrices a S3
│   │
│   ├── monitor/                   # Monitoreo de instancias
│   │   ├── monitor_progress.py   # Estado general de EC2
│   │   └── check_instance_progress.py  # Logs detallados en tiempo real
│   │
│   └── results/                   # Análisis de resultados
│       ├── analyze_results.py    # Estadísticas y comparaciones
│       ├── download_results.py   # Descarga automática desde S3
│       └── verify_visualizations.py  # Verificación de integridad de datos
│
├── tests/                         # Tests unitarios
│   ├── __init__.py               # Paquete de tests
│   └── test_algorithms.py        # 140 tests (27 matrices × 5 algoritmos + 5 validaciones de robustez)
│
├── infrastructure/                # Infraestructura como código (Terraform)
│   ├── main.tf                   # 5 EC2 + S3 único por experimento
│   ├── terraform.tf              # Configuración de providers AWS
│   └── user_data.sh              # Bootstrap EC2 (instala deps, ejecuta tests, corre benchmark)
│
├── benchmark_results/             # Resultados descargados (generado)
│   └── [timestamp]_[algorithm]/  # Resultados por algoritmo y timestamp
│       ├── benchmark_*.json      # Resultados detallados
│       └── metadata.json         # Información del experimento
│
├── visualizations/                # Visualizaciones generadas (generado)
│   ├── 1_comparison_by_type.png  # Comparación por tipo de matriz
│   ├── 2_complexity_analysis.png # Análisis de complejidad
│   ├── 3_success_rate.png        # Tasa de éxito por algoritmo
│   ├── 4_time_summary.png        # Resumen de tiempos
│   ├── 5_memory_summary.png      # Resumen de uso de memoria
│   ├── enhanced_boxplots.pdf     # Boxplots mejorados
│   ├── individual_boxplots.pdf   # Boxplots individuales
│   ├── speedup_analysis.pdf      # Análisis de speedup
│   └── statistics_summary.csv    # Estadísticas detalladas
│
└── test_matrices/                 # Matrices de prueba generadas
    ├── complexity/               # Matrices para análisis de complejidad
    └── presets/                  # Matrices predefinidas
```

---

## Algoritmos Implementados

### 1. Brute Force (`src/algorithms/brute_force.py`)

**Descripción**: Búsqueda exhaustiva que explora **todos** los caminos posibles sin ninguna optimización.

**Complejidad**:
- Temporal: **O(3^n)** donde n es el número de columnas
- Espacial: **O(n)** por la recursión

**Uso de Memoria**: 
- **Bajo** (~2.7 KB promedio): Solo variables locales y pila de recursión
- **Medición**: Pico máximo durante ejecución usando `tracemalloc`
- **Estadísticas** (62 tests exitosos): Media=2.72 KB, Mediana=2.80 KB, Máx=4.02 KB

**Caracteristicas**:
- [!] No realiza poda de ramas
- [!] Explora caminos suboptimos completos
- [x] Garantiza encontrar el optimo global
- [!] Solo viable para matrices pequenas (n < 12)

**Uso**:
```python
from src.algorithms import brute_force

path = brute_force(matriz, y_start=0)
cost = sum(matriz[p[1]][p[0]] for p in path)
```

---

### 2. Backtracking (`src/algorithms/backtracking.py`)

**Descripción**: Búsqueda exhaustiva con **poda de ramas** (branch & bound) y **transformación de offset** para manejar valores negativos. Convierte todos los valores a positivos sumando el valor absoluto del mínimo, permitiendo pruning efectivo.

**Complejidad**:
- Temporal: **O(3^n)** en peor caso, mucho mejor en promedio
- Espacial: **O(n)** por la recursión

**Uso de Memoria**: 
- **Bajo** (~8.6 KB promedio): Variables locales, pila de recursión, tracking del mejor costo y matriz transformada
- **Medición**: Pico máximo durante ejecución usando `tracemalloc`
- **Estadísticas** (81 tests exitosos): Media=8.55 KB, Mediana=5.17 KB, Máx=36.77 KB

**Caracteristicas**:
- [x] **Transformación de offset**: `valor + abs(min_val)` para valores positivos
- [x] Poda ramas suboptimas: `if costo_actual >= mejor_costo: return`
- [x] 10-20x mas rapido que brute force en la practica
- [x] Garantiza encontrar el optimo global
- [!] Aun exponencial, viable hasta n ~= 15

**Uso**:
```python
from src.algorithms import backtracking

path = backtracking(matriz, y_start=0)
```

---

### 3. Divide & Conquer (`src/algorithms/divide_and_conquer.py`)

**Descripción**: Recursión pura que divide el problema en subproblemas, pero **sin cachear** resultados (tiene overlapping subproblems).

**Complejidad**:
- Temporal: **O(3^n)** - recalcula estados repetidos
- Espacial: **O(n)** por la recursión

**Uso de Memoria**: 
- **Bajo** (~12.2 KB promedio): Solo variables locales y pila de recursión profunda
- **Medición**: Pico máximo durante ejecución usando `tracemalloc`
- **Estadísticas** (62 tests exitosos): Media=12.22 KB, Mediana=11.88 KB, Máx=20.66 KB

**Caracteristicas**:
- [!] No usa memoizacion
- [!] Recalcula subproblemas multiples veces
- [x] Codigo mas simple que backtracking
- [!] Similar rendimiento a brute force

**Uso**:
```python
from src.algorithms import divide_and_conquer

path = divide_and_conquer(matriz, sx=0, sy=0)
```

---

### 4. Memoization (`src/algorithms/memoization.py`)

**Descripción**: Programación dinámica **top-down**. Usa recursión + caché para evitar recalcular subproblemas.

**Complejidad**:
- Temporal: **O(m × n)** - cada estado se calcula una vez
- Espacial: **O(m × n)** - tabla de memoización

**Uso de Memoria**: 
- **Variable** (~294 KB promedio): Tabla de memoización (m×n elementos) + pila de recursión
- **Medición**: Pico máximo durante ejecución usando `tracemalloc`
- **Estadísticas** (104 tests exitosos): Media=294.31 KB, Mediana=20.21 KB, Máx=3332.28 KB

**Caracteristicas**:
- [x] Cache de resultados: `data[sy][sx]`
- [x] Calcula solo estados necesarios (lazy)
- [x] Optimo para matrices dispersas
- [x] 1000x+ mas rapido que backtracking para n > 15

**Uso**:
```python
from src.algorithms import memoization

path = memoization(matriz, sx=0, sy=0)
```

---

### 5. Tabulation (`src/algorithms/tabulation.py`)

**Descripción**: Programación dinámica **bottom-up**. Llena tabla de costos desde el final hacia el inicio.

**Complejidad**:
- Temporal: **O(m × n)** - itera toda la matriz
- Espacial: **O(m × n)** - tabla de costos

**Uso de Memoria**: 
- **Medio** (~33.7 KB promedio): Tabla de costos (m×n elementos) + variables auxiliares
- **Medición**: Pico máximo durante ejecución usando `tracemalloc`
- **Estadísticas** (208 tests exitosos): Media=33.67 KB, Mediana=3.79 KB, Máx=324.67 KB

**Caracteristicas**:
- [x] Llena tabla de derecha a izquierda: `for i in range(w-2, -1, -1)`
- [x] Calcula todos los estados (eager)
- [x] No usa recursion (evita stack overflow)
- [x] Generalmente el mas rapido en la practica

**Uso**:
```python
from src.algorithms import tabulation

path = tabulation(matriz, y_start=0)
```

---

## Generadores de Matrices

### 9 Tipos Implementados (`src/matrix/presets.py`)

#### 1. **Random** - Valores aleatorios
```python
from src.matrix import create_random_matrix

M = create_random_matrix(rows=7, cols=15, value_min=-50, value_max=50)
```

#### 2. **Wavy** - Función sinusoidal
```python
from src.matrix import create_wavy_matrix

M = create_wavy_matrix(x_range=(0, 12), y_range=(0, 8))
# f(x,y) = 10*sin(x/2)*cos(y/2) + 15
```

#### 3. **Turbulent** - Oscilaciones múltiples
```python
M = create_turbulent_matrix(x_range=(-10, 10), y_range=(-8, 8))
# f(x,y) = 10*sin(x) + 8*cos(y*1.5) + 5*sin(x*y/10) + 20
```

#### 4. **Gaussian** - Picos gaussianos
```python
M = create_gaussian_matrix(x_range=(0, 12), y_range=(0, 5))
# Dos picos gaussianos superpuestos
```

#### 5. **Valley** - Patrón de valle
```python
M = create_valley_matrix(x_range=(0, 10), y_range=(0, 6))
# f(x,y) = abs(y - 3) * 5 + x
```

#### 6. **Paraboloid** - Superficie parabólica
```python
M = create_paraboloid_matrix(x_range=(0, 10), y_range=(0, 6))
# f(x,y) = (x-5)² + (y-3)²
```

#### 7. **Inclined Plane** - Plano inclinado
```python
M = create_inclined_plane_matrix(x_range=(0, 8), y_range=(0, 5))
# f(x,y) = x + 2*y
```

#### 8. **Checkerboard** - Patrón de ajedrez
```python
M = create_checkerboard_matrix(x_range=(0, 10), y_range=(0, 6))
# Valores alternados según paridad
```

#### 9. **Stairs** - Patrón de escaleras
```python
M = create_stairs_matrix(x_range=(0, 12), y_range=(0, 6))
# f(x,y) = int(x/3)*10 + int(y/2)*5
```

### Matriz desde función personalizada

```python
from src.matrix import matrix_from_function

# Definir función matemática
f = lambda x, y: x**2 + y**2

# Generar matriz
M = matrix_from_function(
    f, 
    x_range=(0, 10), 
    y_range=(0, 6),
    h_x=1.0,  # Step en X
    h_y=1.0,  # Step en Y
    round_values=True
)
```

---

## Sistema de Benchmarking

### Diseño Experimental 

El sistema de benchmarking está diseñado para garantizar **rigor científico** y **reproducibilidad**:

#### Caracteristicas Clave:

1. **Matrices Pre-generadas Compartidas**
   - TODOS los algoritmos usan EXACTAMENTE las mismas matrices
   - Generadas una vez, almacenadas en JSON, reutilizadas por todas las instancias
   - Elimina variabilidad entre algoritmos

2. **Timeout Adaptativo**
   - Tamaños ≤12: **1 minuto**
   - Tamaños 13-20: **2 minutos**
   - Tamaños 21-50: **3 minutos**
   - Tamaños >50: **4 minutos**
   - Algoritmos lentos se marcan como TIMEOUT (no completado)

3. **Cobertura Exhaustiva**
   - **TODOS los algoritmos** prueban **TODOS los tamaños**
   - Demuestra empíricamente dónde fallan los algoritmos exponenciales
   - 104 matrices únicas de prueba

#### Configuracion de Pruebas:

**Análisis de Complejidad:**
- Tamaños: [5, 7, 9, 10, 11, 12, 15, 18, 20, 30, 50, 75, 100]
- Seeds: [42, 123, 456, 789, 1011] (5 seeds)
- Formas: Solo matrices cuadradas (n×n)
- **Total: 65 matrices**

**Benchmarks de Presets:**
- 13 tipos de matrices predefinidas
- Seeds: [42, 123, 456] (3 seeds)
- Posición de inicio: Solo fila 0
- **Total: 39 matrices**

**Total por Algoritmo: 104 pruebas**
**Total proyecto: 520 pruebas (104 × 5 algoritmos)**

### Validaciones de Robustez

Además de las pruebas funcionales básicas, el proyecto incluye **5 validaciones avanzadas de robustez** que aseguran la corrección algorítmica:

#### 1. **Consistencia entre Algoritmos** (`test_algorithm_consistency`)
- Verifica que todos los algoritmos encuentren el mismo costo mínimo para cada matriz
- Manejo específico de excepciones (RecursionError, TimeoutError) con requisitos estrictos
- Asegura que algoritmos DP (memoization, tabulation) sean consistentes entre sí

#### 2. **Optimalidad de Programación Dinámica** (`test_dp_optimality`)
- Verifica que memoization y tabulation produzcan resultados óptimos
- Compara costos DP contra el mejor resultado de algoritmos exhaustivos
- Garantiza que las soluciones DP no sean subóptimas

#### 3. **Propiedades de Caminos** (`test_path_properties`)
- Valida estructura básica de caminos: inicio en columna 0, fin en columna n-1
- Verifica que los caminos tengan exactamente n+1 posiciones (n columnas)
- Asegura conectividad: cada paso avanza exactamente una columna

#### 4. **Sanidad Numérica** (`test_cost_sanity`)
- Detecta valores NaN, infinito positivo/negativo en costos
- Verifica rangos numéricos razonables (±1e6)
- Previene errores de overflow/underflow en cálculos

#### 5. **Unicidad de Movimientos** (`test_path_uniqueness`)
- Valida que cada posición en el camino sea única (no ciclos)
- Verifica movimientos legales: solo diagonales y derecha
- Asegura que no haya movimientos inválidos o posiciones fuera de límites

**Total: 140 pruebas unitarias (135 funcionales + 5 de robustez)**

### Uso de `run_benchmark.py`

#### Generar matrices de prueba (una sola vez)

```bash
python utils/start/generate_test_matrices.py --output ./test_matrices
```

**Output:**
- `test_matrices/complexity/` - 65 matrices para análisis de complejidad
- `test_matrices/presets/` - 39 matrices preset
- `test_matrices/manifest.json` - Metadatos de configuración

#### Ejecutar benchmarks con matrices pre-generadas

```bash
python run_benchmark.py \
  --algorithm tabulation \
  --matrices-dir ./test_matrices \
  --output benchmark_results/
```

**Ventajas:**
- Todos los algoritmos usan exactamente los mismos datos
- Resultados reproducibles
- Timeout adaptativo automático

#### Análisis de complejidad (con matrices pre-generadas)

```bash
python run_benchmark.py \
  --algorithm tabulation \
  --matrices-dir ./test_matrices/complexity \
  --output benchmark_results/
```

**Salida**:
- JSON con tiempos de ejecución para cada tamaño
- CSV con análisis de complejidad
- Indicadores de TIMEOUT para pruebas no completadas

#### Benchmark solo de presets

```bash
python run_benchmark.py \
  --algorithm memoization \
  --presets-only \
  --matrices-dir ./test_matrices
```

#### Opciones de timeout personalizado

```bash
# Timeout fijo de 10 minutos para todas las pruebas
python run_benchmark.py \
  --algorithm backtracking \
  --timeout 600
```

#### Comparar todos los algoritmos

```bash
# Generar matrices primero
python utils/start/generate_test_matrices.py --output ./test_matrices

# Ejecutar cada algoritmo con matrices compartidas
python run_benchmark.py --algorithm brute_force --matrices-dir ./test_matrices --output benchmark_results/
python run_benchmark.py --algorithm backtracking --matrices-dir ./test_matrices --output benchmark_results/
python run_benchmark.py --algorithm divide_and_conquer --matrices-dir ./test_matrices --output benchmark_results/
python run_benchmark.py --algorithm memoization --matrices-dir ./test_matrices --output benchmark_results/
python run_benchmark.py --algorithm tabulation --matrices-dir ./test_matrices --output benchmark_results/
```

---

## Visualización de Resultados

### Generar gráficos desde resultados descargados

```bash
# Usar el script integrado de visualización
python src/visualization/generate_visualizations.py
```

**Gráficos generados** (en `visualizations/`):

#### 1. `complexity_analysis.png`
Tiempo vs tamaño de matriz (escala logarítmica) para todos los algoritmos.

#### 2. `algorithm_comparison.png`
Comparación de tiempos por tipo de matriz (barras agrupadas).

#### 3. `speedup_analysis.png`
Speedup relativo vs brute force.

### Visualización 3D de matriz con camino

```python
from src.visualization import plot_matrix_3d, setup_plotting_style
from src.algorithms import tabulation

# Configurar estilo
setup_plotting_style()

# Generar matriz
M = create_wavy_matrix()

# Encontrar camino
path = tabulation(M, 0)

# Visualizar
plot_matrix_3d(
    matrix=M,
    title="Wavy Matrix - Optimal Path",
    path=path,
    save_path="visualizations/wavy_3d.png"
)
```

---

## Testing

### Ejecutar tests

```bash
# Todos los tests (135 casos)
pytest tests/

# Con verbosidad
pytest tests/ -v

# Solo un algoritmo
pytest tests/test_algorithms.py -k "memoization"
```

### Estructura de tests

**27 matrices de prueba** × **5 algoritmos** = **135 casos de prueba**

Cada test verifica:
- [x] Camino valido (conectado, dentro de limites)
- [x] Costo correcto
- [x] Costo optimo (comparado con resultado esperado)

---

## Ejecución en AWS (Automatizada)

Ver **[EJECUCION.md](docs/EJECUCION.md)** para guía completa.

### Workflow Automatizado con Scripts

```bash
# 1. Desplegar infraestructura y ejecutar benchmarks
python scripts/1_iniciar.py

# 2. Monitorear progreso en tiempo real
python scripts/2_monitor.py

# 3. Pipeline completo: descargar + analizar + visualizar + verificar
python scripts/3_results.py --pipeline --verify

# O comandos individuales:
python scripts/3_results.py --download    # Solo descargar
python scripts/3_results.py --analyze     # Solo analizar
python scripts/3_results.py --visualize   # Solo visualizar
python scripts/3_results.py --verify      # Solo verificar
```

### Comandos Manuales con Terraform

```bash
# Configurar
cd infrastructure
terraform init

# Desplegar (crea 5 EC2, ejecuta benchmarks, sube a S3)
terraform apply

# Limpiar
terraform destroy
```

Ver **[infrastructure/INFRASTRUCTURE.md](infrastructure/INFRASTRUCTURE.md)** para detalles técnicos.

### Comandos Manuales con Deploy Script

```bash
# Desplegar
python utils/start/deploy.py deploy

# Ver estado
python utils/start/deploy.py status

# Destruir
python utils/start/deploy.py destroy
```

**Ventajas**:
- [x] Ejecucion paralela de 5 algoritmos
- [x] Costo: ~$0.30 USD por ejecucion completa
- [x] Resultados en S3 como artefactos .zip
- [x] Totalmente repetible

---

## Instalacion y Setup Local

### Requisitos

- Python 3.10+
- pip
- virtualenv (recomendado)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/gmzrmz/proyecto-final-ada
cd proyecto-final-ada

# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Verificar instalación

```bash
# Ejecutar tests
pytest tests/

# Generar matrices de prueba
python utils/start/generate_test_matrices.py --output ./test_matrices

# Benchmark rápido con timeout adaptativo
python run_benchmark.py --algorithm tabulation --matrices-dir ./test_matrices --sizes 5 10

# Generar visualizaciones (si hay resultados previos)
python src/visualization/generate_visualizations.py

# Verificar pipeline completo
python scripts/3_results.py --verify
```

---

## Verificación de Integridad de Datos

El sistema incluye verificación automática de integridad para asegurar que los datos de benchmark y visualizaciones sean consistentes y completos.

### Qué verifica:

- **Existencia de archivos**: Todos los archivos de visualización requeridos
- **Integridad de datos**: Resultados JSON válidos y consistentes
- **Consistencia algorítmica**: Mapeo correcto entre datos y estadísticas
- **Tamaños de archivo**: Archivos no corruptos (tamaños razonables)

### Uso:

```bash
# Verificar datos existentes
python scripts/3_results.py --verify

# Verificar después del pipeline completo
python scripts/3_results.py --pipeline --verify
```

### Salida de ejemplo:

```
[+] Verificando datos de visualizaciones...
  [OK] Directorio de visualizaciones encontrado
  [OK] Todos los 9 archivos de visualizacion existen
  [OK] Directorio de resultados encontrado
  [OK] Datos cargados: 520 resultados totales
  [OK] Resultados exitosos: 413 (79.4%)
  [OK] Algoritmos encontrados: backtracking, brute_force, divide_and_conquer, memoization, tabulation
  [OK] Estadisticas consistentes con datos originales

============================================================
RESUMEN DE VERIFICACION
============================================================
[OK] Todas las verificaciones pasaron exitosamente!
[OK] 5 verificacion(es) completada(s)

[INFO] Estado de las visualizaciones:
   • 9 archivos generados
   • 5 algoritmos analizados
   • 413/520 benchmarks exitosos
```

---

## Casos de Uso

### 1. Comparar algoritmos en matriz personalizada

```python
from src.matrix import matrix_random
from src.algorithms import backtracking, memoization, tabulation
import time

# Crear matriz
M = matrix_random(10, 20, -50, 50, seed=42)

# Comparar algoritmos
algorithms = {
    'Backtracking': backtracking,
    'Memoization': memoization,
    'Tabulation': tabulation
}

for name, algo in algorithms.items():
    start = time.perf_counter()
    path = algo(M, 0)
    elapsed = time.perf_counter() - start
    cost = sum(M[p[1]][p[0]] for p in path)
    print(f"{name}: {elapsed:.6f}s, cost={cost}")
```

### 2. Análisis de escalabilidad

```python
from src.benchmark import BenchmarkRunner

runner = BenchmarkRunner()
results = runner.run_complexity_analysis(
    algorithm='tabulation',
    sizes=[10, 20, 30, 40, 50],
    repeats=5
)

results.save_json('escalabilidad.json')
results.save_csv('escalabilidad.csv')
```

### 3. Encontrar peor caso para backtracking

```python
import numpy as np
from src.algorithms import backtracking

# Matriz adversarial (costos crecientes)
M = [[i+j for j in range(20)] for i in range(10)]

# Medir tiempo
import time
start = time.perf_counter()
path = backtracking(M, 0)
elapsed = time.perf_counter() - start

print(f"Tiempo en peor caso: {elapsed:.4f}s")
```

---

## Resultados Esperados

### Interpretación de Resultados

**Algoritmos Exponenciales (Brute Force, Backtracking, Divide & Conquer):**
- Viables solo hasta ~12×12
- TIMEOUT en tamaños ≥15 demuestra complejidad O(3^n)
- Backtracking mejor que otros exponenciales por poda

**Algoritmos de Programación Dinámica (Memoization, Tabulation):**
- Completan TODOS los tamaños en segundos
- Escalabilidad lineal demuestra O(m×n)
- Tabulation ligeramente más rápido (no usa recursion)

### Speedup sobre Brute Force (tamaño 10×10)

- Backtracking: **16.7x**
- Memoization: **8,333x**
- Tabulation: **12,500x**

---

## Troubleshooting

### ImportError al ejecutar scripts

```bash
# Asegúrate de estar en el directorio raíz
cd proyecto-final-ada/

# Ejecutar con -m
python -m pytest tests/
```

### RecursionError en matrices grandes

```python
import sys
sys.setrecursionlimit(10000)  # Aumentar límite (memoization/divide_and_conquer)
```

### MemoryError con brute force

Brute force solo es viable hasta n≈12. Usa backtracking o DP para matrices más grandes.

---

## Contribuir

### Agregar nuevo algoritmo

1. Crear `src/algorithms/nuevo_algoritmo.py`
2. Implementar función con firma: `def nuevo_algoritmo(matriz, y=0) -> List[List[int]]`
3. Exportar en `src/algorithms/__init__.py`
4. Agregar tests en `tests/test_algorithms.py`
5. Actualizar variable `algorithms` en `infrastructure/main.tf`

### Agregar nuevo tipo de matriz

1. Agregar función en `src/matrix/presets.py`
2. Agregar preset en diccionario `MATRIX_PRESETS`
3. Actualizar `get_matrix_by_preset()` con nuevo tipo
4. Exportar en `src/matrix/__init__.py`

---

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia **GNU General Public License v3.0 (GPLv3)**.

---
