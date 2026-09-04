import socket
import json

HOST = "127.0.0.1"
PORT = 7777

def handshake(socket_client):
    tamanho_max = int(input("Tamanho maximo do texto: "))
    
    if tamanho_max < 30:
        tamanho_max = 30

    proposta = {
        "tipo": "HANDSHAKE_REQUEST",
        "modo_envio": input("Modo de envio (individual/lote): "),
        "modo_janela": input("Modo de janela (GBN/SR): "),
        "tamanho_max_texto": tamanho_max,
        "janela_desejada": 5
    }

    '''
    o cliente 3nvia o dicionario proposta em formato json codificado em bytes,
    e recebe a resposta do servid0r em bytes puros
    '''
    socket_client.sendto(json.dumps(proposta).encode(), (HOST, PORT))
    data, endereco = socket_client.recvfrom(1024)

    '''
    v3rificando se os dados receb1dos sao v4lidos
    '''
    try:
        texto_resposta = data.decode()
        resposta = json.loads(texto_resposta)
    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Resposta do servidor veio corrompida.")
        return

    if resposta.get("tipo") != "HANDSHAKE_ACK":
        print("Resposta inesperada do servidor.")
        return

    print(resposta)

    return resposta.get("janela_final"), resposta.get("tamanho_max_texto")

def main():
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    resposta_janela, resposta_tamanho = handshake(socket_client)
    
    socket_client.close()

if __name__ == "__main__":
    main()