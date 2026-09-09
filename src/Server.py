import socket
import json

HOST = "127.0.0.1"
PORT = 7777

CAPACIDADE_MAXIMA_JANELA = 5


def main():

    socket_server = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    socket_server.bind((HOST, PORT))

    print("Servidor iniciado. Aguardando handshake do cliente...")

    while True:

        try:
            data, endereco = socket_server.recvfrom(1024)

            texto = data.decode()

            mensagem = json.loads(texto)

        except (UnicodeDecodeError, json.JSONDecodeError):
            print("O pacote recebido eh invalido. Ignorando...")
            continue

        print("Metadados recebidos: ", mensagem)

        if mensagem.get("tipo") != "HANDSHAKE_REQUEST":
            print("A mensagem recebida nao e do tipo esperado.")
            continue

        modo_envio = mensagem.get("modo_envio")

        if isinstance(modo_envio, str):
            modo_envio = modo_envio.lower().strip()

        if modo_envio not in ["individual", "lote"]:
            print("Modo de envio invalido.")
            continue

        modo_janela = mensagem.get("modo_janela")

        if isinstance(modo_janela, str):
            modo_janela = modo_janela.upper().strip()

        if modo_janela not in ["GBN", "SR"]:
            print("Modo de janela invalido.")
            continue

        tamanho_max_texto = mensagem.get("tamanho_max_texto")

        if not isinstance(tamanho_max_texto, int):
            print("Tamanho maximo do texto invalido.")
            continue

        if tamanho_max_texto < 30:
            tamanho_max_texto = 30

        janela_final = CAPACIDADE_MAXIMA_JANELA

        print(
            f"Janela definida pelo servidor: {janela_final}"
        )

        resposta = {
            "tipo": "HANDSHAKE_ACK",
            "modo_envio": modo_envio,
            "modo_janela": modo_janela,
            "tamanho_max_texto": tamanho_max_texto,
            "janela_final": janela_final
        }

        socket_server.sendto(
            json.dumps(resposta).encode(),
            endereco
        )

        print("Aguardando novo handshake...")

    socket_server.close()


if __name__ == "__main__":
    main()