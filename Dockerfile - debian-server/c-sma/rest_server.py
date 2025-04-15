from flask import Flask, jsonify, Response, request, stream_with_context
import json
import time
import sys

app = Flask(__name__)

# Initial deployment state
deployment_states = {}
service_states = {}

def load_configuration(config_file, server_name):
    global deployment_states, service_states
    with open(config_file, 'r') as file:
        config = json.load(file)
        server_config = config.get(server_name, {})
        deployment_states = server_config.get('deployment_states', {})
        service_states = server_config.get('service_states', {})

# Route to obtain the list of deployments or to watch deployments changes
@app.route('/apis/apps/v1/namespaces/<namespace>/deployments', methods=['GET'])
def get_deployment_list(namespace):
    watch = request.args.get('watch')
    if namespace == 'default':
        if watch != 'True':
            # return the deployment list
            return jsonify({"items": list(deployment_states.values())})
        else:
            # watch deployments changes
            return Response(stream_with_context(generate_events()), content_type='text/event-stream')
    else:
        return jsonify({"error": "Namespace not found"}), 404

# Route to obtain the list of services
@app.route('/api/v1/namespaces/<namespace>/services', methods=['GET'])
def get_service_list(namespace):
    if namespace == 'default':
        return jsonify({"items": list(service_states.values())})
    else:
        return jsonify({"error": "Namespace not found"}), 404

# Route to obtain current deployment state
@app.route('/apis/apps/v1/namespaces/<namespace>/deployments/<name>', methods=['GET'])
def get_deployment(namespace, name):
    if namespace == 'default' and name in deployment_states:
        return jsonify(deployment_states[name])
    else:
        return jsonify({"error": "Deployment/Namespace not found"}), 404

def generate_events():
    while True:
        time.sleep(1800)  # Simulate a change every 60 seconds
        for deployment in deployment_states.values():
            deployment['status']['replicas'] += 1
            event = {
                'type': 'MODIFIED',
                'object': deployment
            }
            yield f"{json.dumps(event)}\n"

if __name__ == '__main__':

    args = len(sys.argv)
    
    if args != 2:
        print("Error, incorrect number of arguments")
        sys.exit(0)
    else:
        server_name = sys.argv[1]

    load_configuration('/home/c-sma/config.json', server_name)

    host = '::'  # listen on all available IP addresses
    port = 5050
    # Start server Flask
    app.run(host=host, port=port, debug=True)
