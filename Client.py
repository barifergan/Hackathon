import socket
import struct
import time
import getch

def init_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    CBLUE = '\33[34m'
    CEND = '\33[0m'
    print(CBLUE + 'Client started, listening for offer requests....' + CEND)
    try:
        time.sleep(2)
        client.bind(("", 13117))
    except:
        pass

    while True:
        data, addr = client.recvfrom(10000)
        try:
            unpacked_data = struct.unpack('Ibh', data)
            break
        except:
            pass
    print(CBLUE + 'Received offer from ', addr[0], ' attempting to connect...' + CEND)
    connect_with_tcp(addr,unpacked_data)

def connect_with_tcp(addr,unpacked_data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((addr[0], unpacked_data[2]))
    except:
        sock.close()
        sock.detach()
    try:
        team_name = 'CHEESE CAKE FACTORY'
        sock.send(team_name.encode('utf-8'))
        welcome_message = sock.recv(1024).decode('utf-8')
    except:
        print("connection was close, reset connection")
        sock.close()
        time.sleep(2)
        init_client()
    CBLUE = '\33[34m'
    CEND = '\33[0m'
    print( CBLUE + welcome_message + CEND)
    server_message = None
    while server_message is None:
        message = getch.getche()
        sock.sendall(message.encode('utf-8'))
        try:
            sock.settimeout(0.00001)
            server_message = sock.recv(1024).decode()
        except:
            pass

    print( server_message)
    print("Server disconnected, listening for offer requests..")
    sock.close()
    time.sleep(2)
    init_client()


