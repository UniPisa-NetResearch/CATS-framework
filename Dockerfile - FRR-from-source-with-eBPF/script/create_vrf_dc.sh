#!/bin/bash

# Prompt the user to input the VRF name
read -p "Enter the name for the VRF: " VRF_NAME

# Check if the VRF name is provided
if [ -z "$VRF_NAME" ]; then
    echo "VRF name cannot be empty."
    exit 1
fi

# Prompt the user to input the VRF table id
read -p "Enter the table ID for the VRF: " TABLE_ID

# Check if the table ID is provided
if [ -z "$TABLE_ID" ]; then
    echo "VRF table ID cannot be empty."
    exit 1
fi

# Create the VRF
/sbin/ip link add dev $VRF_NAME type vrf table $TABLE_ID
/sbin/ip link set dev $VRF_NAME up

echo "VRF '$VRF_NAME' has been created successfully."

# RESTART FRR
echo "Restarting FRRouting..."

/usr/lib/frr/frrinit.sh restart

echo "FRRouting has been restarted."
