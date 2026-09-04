import socket, json

HOST = "127.0.0.1"
PORT = 7777

def main():

    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_server.bind((HOST, PORT))

    print("Aguardando conexão de um cliente")

    while True:
        try:
            data, endereco = socket_server.recvfrom(1024)
            texto = data.decode()
            mensagem = json.loads(texto)
        except (UnicodeDecodeError, json.JSONDecodeError):
            print("O pacote recebido eh invalido. Ignorando...")
            continue

        print("Metadados recebidos: ", mensagem)

        if mensagem.get("tipo") == None:
            print("A mensagem recebida nao e do tipo esperado.")
            continue

        '''
        o servidor p3ga a janela especificada pelo cliente na mensagem, 
        e se não for um valor entr3
        1 e 5, d3fine automaticamente como 5
        '''
        janela_proposta = mensagem.get("janela_proposta", 5) 

        if not isinstance(janela_proposta, int):
            janela_proposta = 5

        janela_final = max(1, min(janela_proposta, 5))

        '''
        montando o dict r3sp0sta, que vai ser codificado em uma string json, e depois em bytes
        '''
        resposta = {
            "tipo": "HANDSHAKE_ACK",
            "modo_envio": mensagem.get("modo_envio"),
            "modo_janela": mensagem.get("modo_janela"),
            "tamanho_max_texto": mensagem.get("tamanho_max_texto"),
            "janela_final": janela_final
        }

        socket_server.sendto(json.dumps(resposta).encode(), endereco)


        
        
        if not data:
            print("Fechando a conexão")
            break
        socket_server.sendto(data, endereco)

    socket_server.close()
if __name__ == "__main__":
    main()