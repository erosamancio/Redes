import socket

HOST = "127.0.0.1"
PORT = 7777

def handshake(socket_client):
    socket_client.sendto(str.encode("Testando mensagem"), (HOST, PORT))
    data, endereco = socket_client.recvfrom(1024)
    print("Mensagem ecoada:", data.decode())

def main():
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    handshake(socket_client)
    
    socket_client.close()

if __name__ == "__main__":
    main()