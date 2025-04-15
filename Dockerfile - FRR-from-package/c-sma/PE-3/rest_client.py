from kubernetes import client, config, watch
import sys
import re
import subprocess
import csv
from datetime import datetime
import os

namespace = 'default'

def bgp_update_csv(replicas):
    now = datetime.now()
    timestamp_number = now.minute + now.second / 60 + now.microsecond / 60000000
    timestamp = datetime.now().strftime("%M:%S.%f")
    with open('/tmp/bgp_updates.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, timestamp_number, replicas])
        file.flush()

def update_frr_conf(service_name, replicas):
    try:
        conf_file_path = '/etc/frr/frr.conf'
        command_file_path = '/etc/frr/command.txt'

        commands = [
            'configure terminal\n',
            'end\n',
            'write memory\n'
        ]

        with open(conf_file_path, 'r') as f:
            lines = f.readlines()

        pattern = re.compile(r'\s+match ipv6 address prefix-list {}'.format(re.escape(service_name)))
        for i, line in enumerate(lines):
            if pattern.match(line):
                print("Find route-map to update")
                commands.insert(1, lines[i - 1])
                commands.insert(2, f'set extcommunity bandwidth {replicas}\n')

                with open(command_file_path, 'w') as f:
                    for command in commands:
                        f.write(command )

                print("Write command file")
                write_new_config(command_file_path)
                bgp_update_csv(replicas)
    except Exception as e:
        print(f"Error while updating frr configuration for service '{service_name}': {e}")

def write_new_config(command_file):
    try:
        result = subprocess.run(['vtysh'], stdin=open(command_file), check=True, text=True)
        print('Commands successfully executed')
    except subprocess.CalledProcessError as e:
        print(f'Errore during commands execution: {e}')

def get_deployments(apps_v1, namespace):
    try:
        deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
        return deployments
    except client.exceptions.ApiException as e:
        print(f"Error during get deployment list: {e}")
        return None
    
def get_services(core_v1, namespace):
    try:
        services = core_v1.list_namespaced_service(namespace=namespace)
        return services
    except client.exceptions.ApiException as e:
        print(f"Error during get service list: {e}")
        return None

#def get_deployment_current_state(apps_v1, namespace, deployment_name, ip):
#    try:
#        deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
#        print(f"Current state of the deployment '{deployment_name}': {deployment.status.replicas} replica")
#    except client.exceptions.ApiException as e:
#        print(f"Error during get current state: {e}")
    
def watch_deployment(apps_v1, namespace, deployment_ip_map):
    # start watch deployments
    print(f"Start watch deployments of namespace '{namespace}'...")
    w = watch.Watch()
    try:
        for event in w.stream(apps_v1.list_namespaced_deployment, namespace=namespace):
            deployment = event['object']
            deployment_name = deployment.metadata.name
            current_replicas = deployment.status.replicas
            ip = deployment_ip_map.get(deployment_name)
            print(f"Deployment: {deployment_name}, Event: {event['type']}, Current number of active replicas: {current_replicas}, IP: {ip}")
            update_frr_conf(deployment_name, current_replicas)
    except Exception as e:
        print(f"Error during watch deployment: {e}")
    finally:
        w.stop()

def main():
    args = len(sys.argv)
    
    if args != 2:
        print("Error, incorrect number of arguments")
        sys.exit(0)
    else:
        config_filename = sys.argv[1]

    # Initialize CSV file for bgp updates with headers
    with open('/tmp/bgp_updates.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Timestamp Number','Replicas'])
        file.flush()
    os.chmod('/tmp/bgp_updates.csv', 0o666)  # Set permissions to rw-rw-rw-

    # load configuration
    config.load_kube_config(config_file=config_filename)

    # create kubernetes client instance
    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()

    # get deployments list
    print("Get deployment list...")
    deployments = get_deployments(apps_v1, namespace)

    if deployments is None or not deployments.items:
        print("No deployments found")
        return

    # get services list
    print("Get services list...")
    services = get_services(core_v1, namespace)

    if services is None or not services.items:
        print("No services found")
        return
    
    # Create a dictionary to map deployments to their IP addresses
    deployment_ip_map = {}
    for service in services.items:
        service_name = service.metadata.labels.get('app')
        if service_name:
            deployment_ip_map[service_name] = service.spec.cluster_ip

    for deployment in deployments.items:
        deployment_name = deployment.metadata.name
        ip = deployment_ip_map.get(deployment_name)
        current_replicas = deployment.status.replicas
        print(f"Current state of the deployment '{deployment_name}': {current_replicas} replica, IP: {ip}")
        update_frr_conf(deployment_name, current_replicas)

    # do watch request to observe deployments status changes
    watch_deployment(apps_v1, namespace, deployment_ip_map)

if __name__ == "__main__":
    main()