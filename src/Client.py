import socket

HOST = "127.0.0.1"
PORT = 7777

def handshake(socket_client):
    socket_client.sendall(str.encode("Testando mensagem"))
    data = socket_client.recv(1024)
    print("Mensagem ecoada:", data.decode())

def main():
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((HOST, PORT))
    handshake(socket_client)
    
    socket_client.close()

if __name__ == "__main__":
    main()