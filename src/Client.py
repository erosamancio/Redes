import socket
import json

HOST = "127.0.0.1"
PORT = 7777

def handshake(socket_client):

    while True:
        try:
            tamanho_max = int(input("Tamanho maximo do texto: "))
            if tamanho_max < 30:
                tamanho_max = 30
            break
        except ValueError:
            print("Digite um numero inteiro válido.")

    modo_envio = input("Modo de envio (individual/lote): ").lower().strip()
    while modo_envio not in ["individual", "lote"]:
        print("Modo de envio invalido.")
        modo_envio = input("Modo de envio (individual/lote): ").lower().strip()

    modo_janela = input("Modo de janela (GBN/SR): ").upper().strip()
    while modo_janela not in ["GBN", "SR"]:
        print("Modo de janela invalido.")
        modo_janela = input("Modo de janela (GBN/SR): ").upper().strip()

    proposta = {
        "tipo": "HANDSHAKE_REQUEST",
        "modo_envio": modo_envio,
        "modo_janela": modo_janela,
        "tamanho_max_texto": tamanho_max
    }

    TENTATIVAS_MAX = 3
    TIMEOUT_SEGUNDOS = 3
    socket_client.settimeout(TIMEOUT_SEGUNDOS)

    data = None

    for tentativa in range(1, TENTATIVAS_MAX + 1):
        socket_client.sendto(
            json.dumps(proposta).encode(),
            (HOST, PORT)
        )

        try:
            data, endereco = socket_client.recvfrom(1024)
            break

        except socket.timeout:
            print(
                f"Sem resposta do servidor "
                f"(tentativa {tentativa}/{TENTATIVAS_MAX}). Reenviando..."
            )

    if data is None:
        print("Servidor nao respondeu apos varias tentativas. Encerrando.")
        return None, None

    try:
        texto_resposta = data.decode()
        resposta = json.loads(texto_resposta)

    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Resposta do servidor veio corrompida.")
        return None, None

    if resposta.get("tipo") != "HANDSHAKE_ACK":
        print("Resposta inesperada do servidor.")
        return None, None

    print(resposta)

    return (
        resposta.get("janela_final"),
        resposta.get("tamanho_max_texto")
    )


def main():

    socket_client = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    resposta_janela, resposta_tamanho = handshake(socket_client)

    print("Janela final:", resposta_janela)
    print("Tamanho maximo:", resposta_tamanho)

    socket_client.close()


if __name__ == "__main__":
    main()