import socket
from datetime import datetime
import sys
import os
import random
import csv

buffer_size = 5000
clientSocket = None

MIN_LEN = 1500
MAX_LEN = 2000

def generate_random_message(length_in_bytes):
    return os.urandom(length_in_bytes).decode('latin1')

def send_all(sock, data):
    total_sent = 0
    while total_sent < len(data):
        sent = sock.send(data[total_sent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        total_sent += sent

def update_rtt_csv(rtt):
    now = datetime.now()
    timestamp_number = now.minute + now.second / 60 + now.microsecond / 60000000
    timestamp = datetime.now().strftime("%M:%S.%f")
    with open('/home/TCP/rtt.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, timestamp_number, rtt])
        file.flush()

def main():
    
    args = len(sys.argv)
    
    if args != 5:
        print("Error, incorrect number of arguments")
        sys.exit(0)
    else:
        server_ip = sys.argv[1]
        server_tcp_port = int(sys.argv[2])
        server_address = (server_ip, server_tcp_port)
        client_ip = sys.argv[3]
        traffic_class = int(sys.argv[4], 16)
    
    global clientSocket
    global buffer_size

    #Initialize CSV file for rtt with headers
    # with open('/home/TCP/rtt.csv', mode='w', newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow(['Timestamp', 'Timestamp Number', "Round Trip Time (seconds)"])
    #     file.flush()
    # os.chmod('/home/TCP/rtt.csv', 0o666)  # Set permissions to rw-rw-rw-

    clientSocket = socket.socket(family=socket.AF_INET6, type=socket.SOCK_STREAM)
    clientSocket.settimeout(60)

    print("[INFO] Socket successfully created")

    # set Traffic Class
    clientSocket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_TCLASS, traffic_class)

    # Bind the socket to the client IP address
    clientSocket.bind((client_ip, 0))
    print("[INFO] Socket is binded to address", client_ip)

    try:
        clientSocket.connect(server_address)
        print("[INFO] Socket connected successfully to server")
        
        message_length_in_bytes = random.randrange(MIN_LEN, MAX_LEN + 1)
        msg = generate_random_message(message_length_in_bytes)
        msg = msg.encode('latin1')

        sending_time = datetime.now()
        print("[CLIENT][" + sending_time.strftime("%H:%M:%S.%f") + "] Request sent. Waiting for reply...")

        # send the message len
        msg_length = len(msg)
        clientSocket.send(msg_length.to_bytes(4, byteorder='big'))

        # send the message data
        send_all(clientSocket, msg)        

        try:
            received = clientSocket.recv(buffer_size)
            receiving_time = datetime.now()
            received = received.decode('utf-8')
            print("[CLIENT][" + receiving_time.strftime("%H:%M:%S.%f") + "] Received reply.")

            resp_delay = receiving_time - sending_time
            print("[INFO][DELAY: " + str(resp_delay.total_seconds()) + "]" + '\n')
            update_rtt_csv(resp_delay.total_seconds())

        except socket.timeout:
            print("[ERROR] Timeout occurred while waiting for a reply. Exiting.")
            sys.exit(1)

        except Exception as e:
            print("[ERROR] An error occurred:", e)

    except socket.timeout:
        print("[ERROR] Timeout occurred while trying to connect to the server. Exiting.")
        sys.exit(1)

    except Exception as e:
        print("[ERROR] An error occurred:", e)

    finally:
        clientSocket.close()
    
if __name__=="__main__":
    main()