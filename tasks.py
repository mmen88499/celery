import socket

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5001        # Your chosen port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    
