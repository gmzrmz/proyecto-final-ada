#!/usr/bin/env python3
"""
Check detailed progress of running instances via SSM.
Shows which test they're currently running.
"""
import boto3
import time

ssm = boto3.client('ssm')
ec2 = boto3.client('ec2')

def get_running_instances():
    """Get all running benchmark instances"""
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Environment', 'Values': ['benchmark']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for inst in reservation['Instances']:
            tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
            instances.append({
                'id': inst['InstanceId'],
                'algorithm': tags.get('Algorithm', 'N/A'),
                'launch_time': inst['LaunchTime']
            })
    
    return instances

def check_progress(instance_id, algorithm):
    """Check progress via SSM"""
    print(f"\n{'='*80}")
    print(f">> {algorithm.upper()} - {instance_id}")
    print('='*80)
    
    # Command to get all test results
    command = """
    tail -1000 /var/log/cloud-init-output.log | grep -E "semilla=" | tail -100
    """
    
    try:
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [command]}
        )
        
        command_id = response['Command']['CommandId']
        
        # Wait for command
        time.sleep(2)
        
        # Get output
        output = ssm.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id
        )
        
        stdout = output['StandardOutputContent']
        
        if stdout.strip():
            lines = stdout.strip().split('\n')
            
            # Parse tests
            tests = []
            for line in lines:
                if 'TIMEOUT' in line:
                    # Extract test name
                    test_name = line.split('(')[0].strip()
                    tests.append((test_name, 'TIMEOUT', line))
                elif 'semilla=' in line and ':' in line:
                    # Extract test name and time
                    test_name = line.split('(')[0].strip()
                    time_part = line.split(':')[-1].strip()
                    tests.append((test_name, 'SUCCESS', time_part))
            
            print(f"\nProgreso: {len(tests)} pruebas procesadas")
            print("-" * 80)
            
            # Group by test type
            current_type = None
            success_count = 0
            timeout_count = 0
            
            for test_name, status, info in tests:
                # Detect test type change
                base_name = test_name.split('_seed')[0] if '_seed' in test_name else test_name
                
                if current_type != base_name:
                    if current_type is not None:
                        print()  # New line between groups
                    current_type = base_name
                
                # Display with checkbox
                if status == 'TIMEOUT':
                    print(f"  [X] {test_name:40} TIMEOUT")
                    timeout_count += 1
                else:
                    print(f"  [OK] {test_name:40} {info}")
                    success_count += 1
            
            print(f"\n{'='*80}")
            print(f"[OK] Completadas: {success_count}")
            print(f"[X] Timeouts: {timeout_count}")
            print(f"Total procesadas: {len(tests)}/104")
            
        else:
            # No parsed test results yet — show the last 30 log lines instead
            alt_command = "tail -30 /var/log/cloud-init-output.log"
            response = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName='AWS-RunShellScript',
                Parameters={'commands': [alt_command]}
            )
            
            time.sleep(2)
            
            output = ssm.get_command_invocation(
                CommandId=response['Command']['CommandId'],
                InstanceId=instance_id
            )
            
            print("\nÚltimas 30 líneas de log:")
            print("-" * 80)
            for line in output['StandardOutputContent'].strip().split('\n')[-30:]:
                print(f"  {line}")
        
    except ssm.exceptions.InvalidInstanceId:
        print("  [!] Instancia no disponible para SSM (aún inicializando)")
    except Exception as e:
        print(f"  [ERROR] {e}")

def main():
    """Main function"""
    print("\n" + "="*80)
    print("  PROGRESO DETALLADO DE INSTANCIAS")
    print("="*80)
    
    instances = get_running_instances()
    
    if not instances:
        print("\n[!] No hay instancias corriendo")
        return
    
    print(f"\n[OK] Encontradas {len(instances)} instancia(s) corriendo\n")
    
    for inst in instances:
        check_progress(inst['id'], inst['algorithm'])
    
    print("\n" + "="*80)
    print("[TIP] Ejecuta este script cada 5-10 minutos para ver progreso")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
