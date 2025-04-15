#!/bin/bash

# Prompt the user to input the dummy interface name
read -p "Enter the name for the dummy interface: " INT_NAME

# Check if the dummy interface name is provided
if [ -z "$INT_NAME" ]; then
    echo "Dummy interface name cannot be empty."
    exit 1
fi

# Create the dummy interface
/sbin/ip link add $INT_NAME type dummy
/sbin/ip link set $INT_NAME up

echo "Dummy interface '$INT_NAME' has been created successfully."