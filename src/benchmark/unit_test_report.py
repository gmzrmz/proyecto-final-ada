#!/usr/bin/env python3
"""
Run unit tests and generate comprehensive report.
Handles test execution, timing, result parsing, report generation, and S3 upload on failure.
"""
import sys
import os
import subprocess
import time
import zipfile
from datetime import datetime
from pathlib import Path


def run_unit_tests(output_file):
    """Execute pytest and capture output"""
    print("="*70)
    print("EJECUTANDO PRUEBAS UNITARIAS")
    print("="*70)
    
    # Instalar pytest
    print("Instalando pytest...")
    subprocess.run(['pip', 'install', 'pytest'], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)
    
    # Run tests and capture output
    start_time = int(time.time())
    
    result = subprocess.run(
        ['pytest', 'tests/', '-v'],
        capture_output=True,
        text=True
    )
    
    end_time = int(time.time())
    duration = end_time - start_time
    
    # Store output for later use
    pytest_output = result.stdout + result.stderr
    
    # Check if tests passed
    tests_passed = (result.returncode == 0)
    
    if tests_passed:
        print(f"¡Pruebas unitarias completadas exitosamente!")
        print(f"Duración de las pruebas: {duration} segundos")
    else:
        print(f"ERROR: Fallaron las pruebas unitarias!")
        print(f"Duración de las pruebas: {duration} segundos")
    
    print("="*70)
    
    return tests_passed, start_time, end_time, pytest_output


def parse_pytest_output(output_text):
    """Parse pytest output to extract test statistics"""
    # Look for pytest summary line like: "5 passed in 2.34s"
    passed = 0
    failed = 0
    duration = "unknown"
    
    for line in output_text.split('\n'):
        if ' passed' in line:
            # Extract numbers
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'passed':
                    try:
                        passed = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
                elif part == 'failed':
                    try:
                        failed = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
                elif part.startswith('in') and i+1 < len(parts):
                    duration = parts[i+1]
    
    return passed, failed, output_text


def generate_passed_report(algorithm, start_time, end_time, pytest_output, result_path):
    """Generate report for passed unit tests"""
    duration = end_time - start_time
    passed, failed, full_output = parse_pytest_output(pytest_output)
    
    report = f"""Unit Tests - PASSED
===================
Algorithm: {algorithm}
Start: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}
End: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration} seconds
Tests Passed: {passed if passed else 'N/A'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Status: All tests passed successfully

Full Output:
------------
{full_output}
"""
    
    with open(result_path, 'w') as f:
        f.write(report)
    
    print(f"[OK] Reporte de pruebas unitarias creado: {result_path}")


def generate_failed_report(algorithm, start_time, end_time, pytest_output, result_path):
    """Generate report for failed unit tests"""
    duration = end_time - start_time
    passed, failed, full_output = parse_pytest_output(pytest_output)
    
    report = f"""Unit Tests - FAILED
===================
Algorithm: {algorithm}
Start: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}
End: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration} seconds
Tests Failed: {failed if failed else 'N/A'}
Tests Passed: {passed if passed else 'N/A'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Full Output with Errors:
------------------------
{full_output}

BENCHMARK WAS NOT EXECUTED - Unit tests must pass first!
"""
    
    with open(result_path, 'w') as f:
        f.write(report)
    
    print(f"[ERROR] Reporte de fallo de pruebas unitarias creado: {result_path}")


def upload_failure_to_s3(algorithm, result_dir, experiment_id, s3_bucket):
    """Upload failure report to S3 and exit"""
    import zipfile
    
    completion_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"{experiment_id}_{algorithm}_{completion_time}_UNIT_TESTS_FAILED.zip"
    zip_path = f"/tmp/{zip_filename}"
    
    # Create ZIP with all results
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(result_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, result_dir)
                zipf.write(file_path, arcname)
    
    # Upload to S3
    subprocess.run([
        '/usr/local/bin/aws', 's3', 'cp', 
        zip_path, 
        f"s3://{s3_bucket}/"
    ])
    
    print(f"[ERROR] Reporte de fallo subido: {zip_filename}")


def main():
    """Main function - runs tests and generates report"""
    if len(sys.argv) < 5:
        print("Uso: python unit_test_report.py <algoritmo> <directorio_resultados> <id_experimento> <s3_bucket>")
        sys.exit(1)
    
    algorithm = sys.argv[1]
    result_dir = sys.argv[2]
    experiment_id = sys.argv[3]
    s3_bucket = sys.argv[4]
    
    # Ensure result directory exists
    Path(result_dir).mkdir(parents=True, exist_ok=True)
    
    # Run unit tests (no file needed, returns output directly)
    tests_passed, start_time, end_time, pytest_output = run_unit_tests(None)
    
    # Generate appropriate report
    if tests_passed:
        result_path = f"{result_dir}/unit_tests_passed.txt"
        generate_passed_report(algorithm, start_time, end_time, pytest_output, result_path)
        sys.exit(0)  # Success
    else:
        result_path = f"{result_dir}/unit_tests_FAILED.txt"
        generate_failed_report(algorithm, start_time, end_time, pytest_output, result_path)
        upload_failure_to_s3(algorithm, result_dir, experiment_id, s3_bucket)
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
