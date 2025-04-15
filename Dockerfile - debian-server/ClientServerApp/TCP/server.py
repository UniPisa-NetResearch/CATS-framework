import socket
from datetime import datetime
import sys
import threading
import csv
import os
import time

buffer_size = 1028

MAX_CONN_NUM = 1000

connection = 0

total_bytes = 0
INTERVAL = 10 

lock_connection = threading.Lock()
lock_throughput = threading.Lock()

def update_connections_csv(active_connection):    
    now = datetime.now()
    timestamp_number = now.minute + now.second / 60 + now.microsecond / 60000000
    timestamp = datetime.now().strftime("%M:%S.%f")
    with open('/home/TCP/connections.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, timestamp_number, active_connection])
        file.flush()

def update_throughput_csv(throughput):
    now = datetime.now()
    timestamp_number = now.minute + now.second / 60 + now.microsecond / 60000000
    timestamp = datetime.now().strftime("%M:%S.%f")
    with open('/home/TCP/throughput.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, timestamp_number, throughput])
        file.flush()

def calculate_throughput():
    global total_bytes
    while True:
        time.sleep(INTERVAL)
        with lock_throughput:
            throughput = total_bytes / INTERVAL
            total_bytes = 0
        update_throughput_csv(throughput)

def calculate_connections():
    global connection
    while True:
        time.sleep(INTERVAL)
        with lock_connection:
            temp = connection
            connection = 0
        update_connections_csv(temp)

def handle_client(c, client_address):
    global connection, total_bytes, buffer_size

    print("[INFO]: Connected to client ", client_address)

    with lock_connection:
        connection += 1
    try:
        while True:

            try:
                # read message len
                data = c.recv(4)
                if not data:
                    break
                msg_len = int.from_bytes(data, byteorder='big')
                print(msg_len)

                # read message data
                data = bytearray()
                while len(data) < msg_len:
                    packet = c.recv(min(buffer_size, msg_len - len(data)))
                    if not packet:
                        break
                    data.extend(packet)

                if len(data) < msg_len:
                    print("[INFO] Incomplete message received. Closing connection.")
                    break
                
                with lock_throughput:
                    total_bytes += len(data)
                received_time = datetime.now()

                print("[SERVER][" + received_time.strftime("%H:%M:%S.%f") + "] Received data, from: " + str(client_address[0]) + ", " + str(client_address[1]))

                msg = "[SERVER][" + received_time.strftime("%H:%M:%S.%f") + "] [RESPONSE]" 
                print(msg)
                msg = msg.encode('utf-8')
                c.send(msg)

                sending_time = datetime.now()
                print("[SERVER][" + sending_time.strftime("%H:%M:%S.%f") +"]: [RESP] Sent response")

            except IOError as ioe:
                print(ioe)
                print("[INFO] Client " + str(client_address[0]) + ", " + str(client_address[1]) + " closed connection\n")
                break

            except Exception as e:
                print(e)
                print("[INFO] Client " + str(client_address[0]) + ", " + str(client_address[1]) + " closed connection\n")
                break

    finally:
        print("Closing connection")
        c.close()

def main():
    args = len(sys.argv)
    
    if args != 3:
        print("Error, incorrect number of arguments")
        sys.exit(0)
    else:
        server_ip = sys.argv[1]
        server_tcp_port = int(sys.argv[2])

    print("[INFO] Creating Socket...")
    tcpServerSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    print("[INFO] Socket successfully created")

    tcpServerSocket.bind((server_ip, server_tcp_port))

    print("[INFO] Socket is binded to port", server_tcp_port)

    tcpServerSocket.listen(MAX_CONN_NUM)
    print("[INFO] Socket is listening")

    # Initialize CSV file for number of connections with headers
    with open('/home/TCP/connections.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Timestamp Number', 'Connections'])
        file.flush()
    os.chmod('/home/TCP/connections.csv', 0o666)  # Set permissions to rw-rw-rw-

    # Initialize CSV file for throughput with headers
    with open('/home/TCP/throughput.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Timestamp Number','Throughput (bytes/sec)'])
        file.flush()
    os.chmod('/home/TCP/throughput.csv', 0o666)  # Set permissions to rw-rw-rw-

    # Start throughput calculation thread
    throughput_thread = threading.Thread(target=calculate_throughput, daemon=True)
    throughput_thread.start()

    # Start connections calculation thread
    connections_thread = threading.Thread(target=calculate_connections, daemon=True)
    connections_thread.start()

    while True:
        # Wait for client connection request
        c, client_address = tcpServerSocket.accept()
        client_thread = threading.Thread(target=handle_client, args=(c, client_address))
        client_thread.start()
        

if __name__=="__main__":
    main()