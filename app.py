import socket
import threading

# Constant variables
BACKLOG = 50
MAX_DATA_RECV = 999999
DEBUG = True
BLOCKED = []  # example: ["www.blocked.com"]

def printout(type, request, address):
    if "Block" in type or "Blacklist" in type:
        colornum = 91
    elif "Request" in type:
        colornum = 92
    elif "Reset" in type:
        colornum = 93
    print(f"\033[{colornum}m{address[0]}\t{type}\t{request}\033[0m")

def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECV)
    first_line = request.split(b'\n')[0]
    url = first_line.split(b' ')[1]

    for blocked in BLOCKED:
        if blocked in url:
            printout("Blacklisted", first_line, client_addr)
            conn.close()
            return

    printout("Request", first_line, client_addr)

    http_pos = url.find(b"://")
    if http_pos == -1:
        temp = url
    else:
        temp = url[http_pos + 3:]

    port_pos = temp.find(b":")
    webserver_pos = temp.find(b"/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if port_pos == -1 or webserver_pos < port_pos:
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int(temp[port_pos + 1:webserver_pos].decode())
        webserver = temp[:port_pos]

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver.decode(), port))
        s.send(request)

        while True:
            data = s.recv(MAX_DATA_RECV)
            if len(data) > 0:
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except socket.error as e:
        if s:
            s.close()
        if conn:
            conn.close()
        printout("Peer Reset", first_line, client_addr)

def main():
    if len(sys.argv) < 2:
        port = 8080
    else:
        port = int(sys.argv[1])

    host = ""
    print(f"Proxy Server Running on {host}:{port}")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(BACKLOG)

        while True:
            conn, client_addr = s.accept()
            threading.Thread(target=proxy_thread, args=(conn, client_addr)).start()

    except socket.error as e:
        if s:
            s.close()
        print(f"Could not open socket: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
