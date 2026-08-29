import socket

HOST = "127.0.0.1"
PORT = 7777

def main():

    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind((HOST, PORT))
    socket_server.listen()

    print("Aguardando conexão de um cliente")

    conexao_client, endereco = socket_server.accept()

    print("Conectado em", endereco)

    while True:
        data = conexao_client.recv(1024)
        if not data:
            print("Fechando a conexão")
            conexao_client.close()
            break
        conexao_client.sendall(data)

    socket_server.close()

if __name__ == "__main__":
    main()