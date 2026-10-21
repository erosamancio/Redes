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

    print("Servidor UDP iniciado na porta 7777")
    print("Servidor ativo Aguardando comunicacao")

    handshake_concluido = False

    while True:
        try:
            data, endereco = socket_server.recvfrom(1024)
            texto = data.decode()
            mensagem = json.loads(texto)

        except (UnicodeDecodeError, json.JSONDecodeError):
            print("Pacote recebido invalido Ignorando")
            continue

        tipo_msg = mensagem.get("tipo")

        if tipo_msg == "HANDSHAKE_REQUEST":
            modo_envio = mensagem.get("modo_envio")

            if isinstance(modo_envio, str):
                modo_envio = modo_envio.lower().strip()

            if modo_envio not in ["individual", "lote"]:
                print("Modo de envio invalido")
                continue

            modo_janela = mensagem.get("modo_janela")

            if isinstance(modo_janela, str):
                modo_janela = modo_janela.upper().strip()

            if modo_janela not in ["GBN", "SR"]:
                print("Modo de janela invalido")
                continue

            tamanho_max_texto = mensagem.get("tamanho_max_texto")

            if not isinstance(tamanho_max_texto, int):
                print("Tamanho maximo do texto invalido")
                continue

            if tamanho_max_texto < 30:
                tamanho_max_texto = 30

            if modo_envio == "individual":
                janela_final = 1
            else:
                janela_final = CAPACIDADE_MAXIMA_JANELA

            print(f"Janela definida pelo servidor {janela_final}")

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

            handshake_concluido = True
            print("Handshake concluido com sucesso")

        elif tipo_msg == "DATA" and handshake_concluido:
            seq = mensagem.get("seq")
            payload = mensagem.get("payload")
            checksum = mensagem.get("checksum")

            print(f"Recebido DATA Seq {seq} Payload {payload} Checksum {checksum}")

            ack = {
                "tipo": "ACK",
                "seq": seq
            }

            socket_server.sendto(
                json.dumps(ack).encode(),
                endereco
            )
            print(f"Enviado ACK Seq {seq}")

if __name__ == "__main__":
    main()