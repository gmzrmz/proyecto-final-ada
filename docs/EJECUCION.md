# Guía de Ejecución - Matrix Crossing Benchmark

Guía completa para ejecutar benchmarks automatizados en AWS EC2.

## Pre-requisitos

### 1. Herramientas necesarias

- **Git** - Control de versiones
- **Python 3.10+** - Runtime del proyecto  
- **AWS CLI** - Configurado con credenciales válidas
- **Terraform 1.0+** - Para gestionar infraestructura

### 2. AWS Academy o Cuenta AWS

- Credenciales configuradas (AWS CLI o variables de entorno)
- Permisos para EC2, S3, IAM
- **Nota**: AWS Academy tiene límite de 4 horas por sesión

---

## Inicio Rápido

El proyecto incluye **3 scripts automatizados** que simplifican todo el workflow:

### Workflow Automatizado (Recomendado)

```bash
# Script 1: Iniciar experimento (configura credenciales, genera matrices, despliega)
python scripts/1_iniciar.py

# Script 2: Monitorear progreso (estado de instancias y S3)
python scripts/2_monitor.py

# Script 3: Procesar resultados (descargar, analizar, visualizar, verificar)
python scripts/3_results.py
```

### Workflow Manual (Avanzado)

Si prefieres control detallado sobre cada paso:

### 1. Clonar repositorio e instalar dependencias

```bash
git clone https://github.com/gmzrmz/proyecto-final-ada.git
cd proyecto-final-ada
pip install -r requirements.txt
```

**Nota:** Si usas el workflow automatizado, el script `1_iniciar.py` te guiará en los siguientes pasos.

### 2. Configurar Terraform

Terraform crea automáticamente un bucket S3 único para cada experimento. No se requiere configuración manual del bucket.

**Nota**: Si deseas usar un bucket existente, edita `infrastructure/main.tf` para modificar la lógica de creación del bucket.

### 3. Generar matrices de prueba y desplegar

```bash
# Generar 104 matrices de prueba
python utils/start/generate_test_matrices.py

# Desplegar infraestructura (crea bucket, sube matrices, lanza 5 instancias)
python utils/start/deploy.py deploy
```

### 4. Monitorear progreso

**Opción 1: Script automatizado (Recomendado)**
```bash
python scripts/2_monitor.py
# Menú interactivo con opciones:
# - Monitor general (estado de instancias y S3)
# - Monitor detallado (logs y pruebas)
# - Monitor continuo (auto-refresh cada 60s)
# - Verificar finalización
```

**Opción 2: Comandos individuales**
```bash
# Ver estado de instancias y resultados en S3
python utils/monitor/monitor_progress.py

# Ver progreso detallado (qué prueba están ejecutando, con resumen de completadas/timeout)
python utils/monitor/check_instance_progress.py
```

### 5. Descargar y analizar resultados

**Opción 1: Script automatizado (Recomendado)**

#### Menú interactivo:
```bash
python scripts/3_results.py
# Menú interactivo con opciones:
# - Descargar resultados desde S3
# - Analizar resultados (estadísticas)
# - Generar visualizaciones
# - Verificar integridad de datos
# - Pipeline completo (todo en uno)
```

#### Línea de comandos (sin interacción):
```bash
# Pipeline completo con verificación
python scripts/3_results.py --pipeline --verify

# Solo descargar
python scripts/3_results.py --download

# Solo analizar
python scripts/3_results.py --analyze

# Solo visualizar
python scripts/3_results.py --visualize

# Solo verificar
python scripts/3_results.py --verify
```

### Verificación de Integridad

La opción `--verify` realiza comprobaciones automáticas de integridad:

- **Archivos de visualización**: Verifica que todos los archivos requeridos existan
- **Datos de benchmark**: Valida que los resultados JSON sean consistentes
- **Estadísticas**: Confirma que los algoritmos en CSV coincidan con los datos
- **Tamaños de archivo**: Detecta archivos potencialmente corruptos

**Ejemplo de salida:**
```
[+] Verificando datos de visualizaciones...
  [OK] Directorio de visualizaciones encontrado
  [OK] Todos los 9 archivos de visualizacion existen
  [OK] Datos cargados: 520 resultados totales
  [OK] Estadisticas consistentes con datos originales

============================================================
RESUMEN DE VERIFICACION
============================================================
[OK] Todas las verificaciones pasaron exitosamente!
```

**Opción 2: Comandos individuales**
```bash
# Descargar resultados disponibles inmediatamente
python utils/results/download_results.py

# Analizar resultados descargados
python utils/results/analyze_results.py

# Generar gráficas comparativas
python src/visualization/generate_visualizations.py
```

### 6. Limpiar infraestructura

**Opción 1: Desde el script de inicio**
```bash
python scripts/1_iniciar.py
# Selecciona opción "Destruir infraestructura" del menú
```

**Opción 2: Comando directo**
```bash
python utils/start/deploy.py destroy
```

**Opción 3: Terraform manual**
```bash
cd infrastructure
terraform destroy
```

**Nota**: El bucket S3 y sus objetos NO se eliminan automáticamente (contienen resultados).

---

## Arquitectura del Sistema

### Componentes:

1. **Generación Local de Matrices**
   - `utils/start/generate_test_matrices.py` crea 104 matrices únicas
   - Se comprimen en `test_matrices.tar.gz`
   - Se suben a S3 automáticamente durante el deploy

2. **Terraform Deploy**
   - Crea bucket S3 (si no existe)
   - Sube `test_matrices.tar.gz` a S3
   - Lanza 5 instancias EC2 t3.medium en paralelo
   - Configura roles IAM y security groups

3. **EC2 Instances** (5 en paralelo)
   - brute_force
   - backtracking  
   - divide_and_conquer
   - memoization
   - tabulation
   - Cada instancia:
     * Descarga matrices desde S3
     * Ejecuta benchmarks con timeouts optimizados
     * Sube resultados a S3 como ZIP
     * Se auto-termina al completar

4. **S3 Bucket**
   - `test_matrices.tar.gz` (entrada compartida)
   - `brute_force_TIMESTAMP.zip` (resultados)
   - `backtracking_TIMESTAMP.zip`
   - `divide_and_conquer_TIMESTAMP.zip`
   - `memoization_TIMESTAMP.zip`
   - `tabulation_TIMESTAMP.zip`

5. **Descarga Local + Análisis Completo**
   - Resultados JSON/CSV extraídos
   - Visualizaciones PNG/PDF generadas
   - Verificación de integridad automática

### Flujo de Ejecución:


1. Usuario genera matrices localmente y las sube a S3 (ANTES de terraform)
2. Terraform crea 5 EC2 instances (una por algoritmo)
3. Todas las instancias descargan matrices pre-generadas desde S3
4. Todas las instancias realizan pruebas unitarias sobre el código
5. Todas las instancias ejecutan benchmarks EN PARALELO con las MISMAS matrices
6. Al finalizar, los resultados (y logs) se comprimen y suben a S3
7. Instancias se auto-terminan al finalizar
8. Usuario descarga resultados de S3
9. Usuario genera visualizaciones y verifica integridad localmente

---

## Opción Rápida: Scripts Automatizados

**El proyecto incluye 3 scripts interactivos que automatizan TODO el proceso:**

### 1. Iniciar Experimento
```bash
python scripts/1_iniciar.py
```
**Funcionalidades:**
- Configura credenciales AWS
- Genera 104 matrices de prueba
- Sube matrices a S3
- Inicializa Terraform
- Despliega infraestructura
- Menú interactivo para todas las operaciones

### 2. Monitorear Progreso
```bash
python scripts/2_monitor.py
```
**Funcionalidades:**
- Monitor general de instancias y S3
- Monitor detallado con logs
- Monitor continuo (auto-refresh)
- Verificación de finalización

### 3. Procesar Resultados
```bash
python scripts/3_results.py
```
**Funcionalidades:**
- Descarga de resultados desde S3
- Análisis estadístico
- Generación de visualizaciones
- Verificación de integridad de datos
- Pipeline completo automatizado

**Tiempo total: ~5-10 minutos setup + 1-3 horas de ejecución en AWS**

---

## Flujo Manual Detallado (Avanzado)

Si prefieres control total sobre cada paso o quieres entender el proceso interno:

## Paso 0: Generacion Local de Matrices (OBLIGATORIO)

[!] **ESTE PASO DEBE COMPLETARSE ANTES DE `terraform apply`**

### 0.1 Generar matrices de prueba

```bash
# Generar 104 matrices únicas (65 complejidad + 39 presets)
python utils/start/generate_test_matrices.py --output ./test_matrices
```

Esto crea:
- 65 matrices de análisis de complejidad (13 tamaños × 5 seeds)
- 39 matrices de casos especiales (13 presets × 3 seeds)
- **Total: 104 matrices únicas** para garantizar reproducibilidad científica

### 0.2 Comprimir y subir a S3

```bash
# Comprimir directorio de matrices
tar -czf test_matrices.tar.gz test_matrices/

# Subir a S3 (el bucket se crea automáticamente por Terraform)
# Nota: Ejecuta terraform apply primero para crear el bucket
aws s3 cp test_matrices.tar.gz s3://$(terraform output -raw s3_bucket_name)/test_matrices.tar.gz
```

**Nota para Windows PowerShell:**
```
$BUCKET = terraform output -raw s3_bucket_name
aws s3 ls "s3://$BUCKET/test_matrices.tar.gz"

# Subir a S3
$BUCKET = terraform output -raw s3_bucket_name
aws s3 cp test_matrices.tar.gz "s3://$BUCKET/test_matrices.tar.gz"
```

[x] **Verificar que las matrices esten en S3:**
```bash
aws s3 ls s3://matrix-crossing-benchmark-XXXXX/test_matrices.tar.gz
```

---

## Paso 1: Configuracion Inicial

### 1.1 Crear repositorio en GitHub

```bash
# Inicializar Git en el proyecto
git init

# Agregar todos los archivos
git add .

# Commit inicial
git commit -m "Initial commit: Matrix crossing benchmark project"

# Renombrar rama principal
git branch -M main

# Agregar remote
git remote add origin https://github.com/gmzrmz/proyecto-final-ada.git

# Push al repositorio
git push -u origin main
```

### 1.2 Configurar AWS CLI

```bash
# Instalar AWS CLI (si no lo tienes)
# Descargar desde: https://aws.amazon.com/cli/

# Configurar credenciales
aws configure

# Se te pedirá:
# AWS Access Key ID [None]: TU_ACCESS_KEY_ID
# AWS Secret Access Key [None]: TU_SECRET_ACCESS_KEY
# Default region name [None]: us-east-1
# Default output format [None]: json
```

### 1.3 Actualizar configuración de Terraform

Editar `infrastructure/main.tf` y actualizar la URL del repositorio:

```hcl
variable "github_repo" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/gmzrmz/proyecto-final-ada.git"
}
```

---

## Paso 2: Ejecutar Benchmarks

### 2.1 Inicializar Terraform

```bash
# Navegar al directorio de infraestructura
cd infrastructure

# Inicializar Terraform (descargar providers)
terraform init
```

**Output esperado:**
```
Initializing the backend...
Initializing provider plugins...
Terraform has been successfully initialized!
```

### 2.2 Revisar el plan (Opcional)

```bash
# Ver qué recursos se van a crear
terraform plan
```

Esto mostrará:
- 5 EC2 instances
- 1 S3 bucket
- IAM roles y políticas
- Security groups

### 2.3 Aplicar la infraestructura

```bash
# Crear recursos y ejecutar benchmarks
terraform apply

# Terraform preguntará confirmación
# Escribir: yes
```

**Tiempo estimado:** 3-5 horas (depende de cuántos TIMEOUT)

**Costo estimado:** $1.50 - $2.50 USD

**¿Qué pasa ahora?**
1. Terraform crea 5 EC2 instances en AWS
2. Instancia `brute_force` (primera) ejecuta:
   - Genera 104 matrices de prueba únicas
   - Sube matrices a S3 como test_matrices.tar.gz
   - Ejecuta benchmarks con timeout adaptativo
3. Otras 4 instancias ejecutan:
   - Descargan matrices desde S3 (esperan si es necesario)
   - Ejecutan benchmarks con LAS MISMAS matrices
   - Timeout adaptativo: 1min/2min/3min/4min según tamaño
4. Todas las instancias:
   - Generan archivos JSON/CSV con resultados
   - Comprimen resultados en un .zip
   - Suben el .zip a S3
   - Se apagan automáticamente

---

## Paso 3: Monitorear Ejecucion (Opcional)

### 3.1 Ver instancias corriendo

```bash
# Listar instancias de benchmark
aws ec2 describe-instances `
  --filters "Name=tag:Environment,Values=benchmark" `
  --query "Reservations[].Instances[].[InstanceId,State.Name,Tags[?Key=='Algorithm'].Value|[0]]" `
  --output table
```

**Estados posibles:**
- `pending` - Iniciando
- `running` - Ejecutando benchmarks
- `shutting-down` - Subió resultados, apagándose
- `terminated` - Completado

### 3.2 Ver nombre del bucket S3

```bash
terraform output s3_bucket_name
```

### 3.3 Listar archivos en S3

```bash
# Obtener nombre del bucket
$BUCKET = terraform output -raw s3_bucket_name

# Listar contenido
aws s3 ls "s3://$BUCKET/"
```

---

## Paso 4: Descargar Resultados

### 4.1 Esperar a que terminen todas las instancias

```bash
# Verificar que todas estén en estado 'terminated'
aws ec2 describe-instances `
  --filters "Name=tag:Environment,Values=benchmark" `
  --query "Reservations[].Instances[].State.Name" `
  --output text
```

Debe mostrar 5 veces `terminated`.

### 4.2 Descargar todos los resultados

```bash
# Volver al directorio raíz del proyecto
cd ..

# Crear directorio para resultados
New-Item -ItemType Directory -Force -Path benchmark_results

# Obtener nombre del bucket
cd infrastructure
$BUCKET = terraform output -raw s3_bucket_name

# Descargar todo desde S3
aws s3 sync "s3://$BUCKET" ..\benchmark_results\

# Volver al directorio raíz
cd ..
```

### 4.3 Extraer archivos .zip

```bash
# Entrar al directorio de resultados
cd benchmark_results

# Extraer todos los .zip
Get-ChildItem *.zip | ForEach-Object {
    Expand-Archive -Path $_.FullName -DestinationPath "extracted/$($_.BaseName)" -Force
}

# Volver al directorio raíz
cd ..
```

**Estructura de resultados:**
```
benchmark_results/
├── brute_force_20251206_143022.zip
├── backtracking_20251206_143045.zip
├── divide_and_conquer_20251206_143110.zip
├── memoization_20251206_143015.zip
└── tabulation_20251206_143008.zip
```

---

## Paso 5: Generar Visualizaciones

### 5.1 Combinar resultados

```bash
# Ejecutar script de visualización
python src/visualization/generate_visualizations.py
```

Esto genera en `visualizations/`:
- `complexity_analysis.png` - Comparación de complejidad
- `algorithm_comparison.png` - Comparación por tipo de matriz
- `execution_times.png` - Tiempos de ejecución

### 5.2 Ver resultados

```bash
# Abrir carpeta de visualizaciones
explorer visualizations
```

---

## Paso 6: Limpiar Recursos

### 6.1 Destruir infraestructura

```bash
cd infrastructure

# Eliminar todos los recursos de AWS
terraform destroy

# Confirmar escribiendo: yes
```

**IMPORTANTE:** Esto elimina:
- [x] EC2 instances (ya terminadas)
- [x] Security groups
- [x] IAM roles
- [!] **S3 bucket (SE CONSERVA con los resultados)**

### 6.2 Eliminar bucket S3 (opcional)

Si quieres eliminar también los resultados almacenados:

```bash
# Obtener nombre del bucket
$BUCKET = terraform output -raw s3_bucket_name

# Vaciar bucket
aws s3 rm "s3://$BUCKET" --recursive

# Eliminar bucket
aws s3 rb "s3://$BUCKET"
```

---

## Re-ejecutar Benchmarks

Para crear un nuevo conjunto de resultados:

```bash
cd infrastructure
terraform apply
# Escribir: yes

# Esperar 30-60 min...

# Descargar nuevos resultados
# (Se creará un bucket S3 con timestamp diferente)
```

---

## Configuracion Avanzada

### Timeout Adaptativo

El sistema usa timeout adaptativo automático:
- Tamaños ≤12: 1 minuto (60s)
- Tamaños 13-20: 2 minutos (120s)
- Tamaños 21-50: 3 minutos (180s)
- Tamaños >50: 4 minutos (240s)

Si un algoritmo no completa en el tiempo límite, se marca como TIMEOUT (no completado).

### Cambiar tipo de instancia

```bash
terraform apply -var="instance_type=c5.xlarge"
```

**Opciones:**
- `t3.medium` (default) - $0.0416/hora, 2 vCPUs, 4 GB RAM
- `t3.large` - $0.0832/hora, 2 vCPUs, 8 GB RAM
- `c5.large` - $0.085/hora, 2 vCPUs, 4 GB RAM

### Cambiar región de AWS

```bash
terraform apply -var="aws_region=us-west-2"
```

### Ejecutar solo algunos algoritmos

Editar `infrastructure/main.tf`:

```hcl
variable "algorithms" {
  default = ["backtracking", "memoization", "tabulation"]  # Solo 3
}
```

Luego:
```bash
terraform apply
```

### Cambiar tamaños de matrices para complejidad
82:

```bash
python run_benchmark.py --algorithm "$ALGORITHM" --output /results --matrices-dir /matrices/test_matrices
```

**Opciones disponibles:**
- `--sizes 5 10 15 20 25 30` - Tamaños personalizados para análisis de complejidad (agregar al comando si deseas sobrescribir)
- `--presets-only` - Solo ejecutar benchmarks de matrices preset
- `--complexity-only` - Solo ejecutar análisis de complejidad
- Sin flags adicionales - Ejecutar suite completa (presets + complejidad)
- `--sizes 5 10 15 20 25 30` - Tamaños personalizados para análisis de complejidad
- `--presets-only` - Solo ejecutar benchmarks de matrices preset
- `--complexity-only` - Solo ejecutar análisis de complejidad
- Sin flags adicionales - Ejecutar suite completa (presets + complejidad)

---

## Troubleshooting

### Las instancias no se terminan

```bash
# Terminar manualmente
aws ec2 terminate-instances --instance-ids i-xxxxx i-yyyyy
```

### No se suben resultados a S3

```bash
# Verificar permisos IAM
terraform output

# Revisar logs de la instancia (requiere SSH configurado)
# Crear key pair en AWS Console primero
ssh -i tu_key.pem ubuntu@<PUBLIC_IP>
tail -f /var/log/user-data.log
```

### Error "bucket already exists"

El nombre del bucket usa timestamp, pero si ejecutas muy rápido:

```bash
# Esperar 1 minuto y volver a intentar
terraform apply
```

### Error de credenciales AWS

```bash
# Re-configurar AWS CLI
aws configure

# Verificar que funcionan
aws sts get-caller-identity
```

---

## Tips y Mejores Practicas

### 1. Mantener histórico de resultados

Los resultados en S3 se conservan con versionado habilitado. Puedes:

```bash
# Listar todas las versiones
aws s3api list-object-versions --bucket $BUCKET
```

### 2. Costos

**Estimación por ejecución completa:**

| Componente | Detalle | Costo Estimado |
|------------|---------|----------------|
| EC2 (5 instancias) | t3.medium @ $0.0416/hr × 5 × 4hr | $0.83 |
| S3 Storage | <1 GB | $0.02 |
| S3 Transfer | <1 GB | $0.09 |
| **TOTAL** | | **~$1.80 USD** |

**Notas:**
- Tiempo real varía según cuántos benchmarks lleguen a TIMEOUT
- Algoritmos DP terminan rápido (~30 min)
- Algoritmos exponenciales pueden tardar 4-5 horas (muchos TIMEOUT)

- **Monitorear costos:** AWS Console → Billing Dashboard
- **Configurar alarmas:** CloudWatch → Billing Alarms
- **Siempre ejecutar `terraform destroy`** después de descargar resultados

### 3. Reproducibilidad

Cada ejecución crea un bucket nuevo con timestamp, permitiendo:
- Comparar resultados de diferentes fechas
- Rollback a versiones anteriores
- Compartir resultados específicos

### 4. Paralelización

Las 5 instancias corren en paralelo, pero si quieres más control:

```bash
# Ejecutar solo backtracking y memoization
terraform apply -target=aws_instance.benchmark[1] -target=aws_instance.benchmark[3]
```

---

## Recursos Adicionales

- [Documentación de Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS EC2 Pricing](https://aws.amazon.com/ec2/pricing/on-demand/)
- [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)

---

## Soporte

Si encuentras problemas:

1. Revisar logs: `infrastructure/terraform.log`
2. Verificar estado: `terraform show`
3. Validar sintaxis: `terraform validate`
4. Consultar outputs: `terraform output`

---

## Checklist de Ejecucion

- [ ] Git configurado y repo en GitHub
- [ ] AWS CLI instalado y configurado
- [ ] Terraform instalado
- [ ] URL del repo actualizada en `main.tf`
- [ ] `terraform init` ejecutado
- [ ] `terraform apply` ejecutado y confirmado
- [ ] Instancias terminadas (estado: terminated)
- [ ] Resultados descargados de S3
- [ ] Visualizaciones generadas
- [ ] `terraform destroy` ejecutado
- [ ] Costos verificados en AWS Console

