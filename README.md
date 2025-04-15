# CATSFramework
This is a framework for dynamic computing and network aware traffic steering. It leverages different technologies such as SRv6, MP-BGP, Kubernetes APIs, Docker and GNS3.

# Installation and Configuration Procedure

## 1. Create Docker Images
Build the necessary Docker images using the provided Dockerfiles:

```bash
# Build Docker image for IFs
cd Dockerfile-FRR-from-source-with-eBPF
docker build -t frr-from-source .

# Build Docker image for other routers from package
cd Dockerfile-FRR-from-package
docker build -t frr-from-package .

# Build Docker image for client
cd Dockerfile-debian-client
docker build -t debian-client .

# Build Docker image for server
cd Dockerfile-debian-server
docker build -t debian-server .
```

## 2. Load Docker Images into GNS3
For each image you want to load:
1. Navigate to `Edit -> Preferences -> Docker Containers -> New -> New Image`.
2. Select the image you want to load.
3. Click `Next` and assign a name to your device.

## 3. Create a New Network
- Drag and drop the previously created device types into the network.
- Rename devices according to the reference image.
- Connect them as shown in the reference image.
- To start a device, open the router's CLI and execute:
  ```bash
  docker exec -it <container_name> /bin/sh
  ```
- Open `vtysh` on each device and copy the FRR configuration from the corresponding `<device-name>.txt` file.

## 4. Execute Configuration Scripts

### Open Auxiliary Console
Select all routers in the network and open an auxiliary console.

### Run Configuration for Specific Routers

#### For the following routers:
Client-Edge-1, Client-Edge-2, Ingress-DC-Cloud-1, Ingress-DC-Cloud-2, Ingress-DC-Far-1, Ingress-DC-Far-2, Ingress-DC-Near-1, Ingress-DC-Near-2, PE-1-(core):
```bash
/etc/frr/init.sh
```

#### For PE-2-(ingress):
```bash
cd /etc/frr
./init.sh
./create_vrf_dc.sh near-edge 1
./create_vrf_dc.sh far-edge 2
./create_vrf_dc.sh cloud 3
./create_vrf_client.sh client-edge 4 eth0
./create_dummy_interface.sh lo1
./load_bpf.sh
```

#### For PE-4-(ingress):
```bash
cd /etc/frr
./init.sh
./create_vrf_dc.sh near-edge 1
./create_vrf_dc.sh far-edge 2
./create_vrf_dc.sh cloud 3
./create_vrf_client.sh client-edge 4 eth0
./create_dummy_interface.sh lo1
./load_bpf.sh
```

#### For PE-3-(egress):
```bash
cd /etc/frr
./init.sh
./create_vrf.sh near-1 1 eth0
./create_vrf.sh far-1 2 eth1
./create_vrf.sh cloud-1 3 eth2
./create_dummy_interface.sh lo1
```

#### For PE-5-(egress):
```bash
cd /etc/frr
./init.sh
./create_vrf.sh near-2 1 eth0
./create_vrf.sh far-2 2 eth1
./create_vrf.sh cloud-2 3 eth2
./create_dummy_interface.sh lo1
```

