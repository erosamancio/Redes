import socket

HOST = "127.0.0.1"
PORT = 7777

def main():

    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_server.bind((HOST, PORT))

    print("Aguardando conexão de um cliente")

    while True:
        data, endereco = socket_server.recvfrom(1024)
        
        print("Conectado em", endereco)
        
        if not data:
            print("Fechando a conexão")
            break
        socket_server.sendto(data, endereco)

    socket_server.close()

if __name__ == "__main__":
    main()