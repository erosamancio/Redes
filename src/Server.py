import socket
import json

HOST = "127.0.0.1"
PORT = 7777
CAPACIDADE_MAXIMA_JANELA = 5

def calcular_checksum(payload):
    return sum(payload.encode()) % 65536

def main():
    socket_server = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    socket_server.bind((HOST, PORT))

    print("Servidor UDP iniciado na porta 7777")
    print("Servidor ativo Aguardando comunicacao")

    handshake_concluido = False
    modo_janela_atual = None
    buffer = {}
    esperado = 0
    total_pacotes = None

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
            modo_janela_atual = modo_janela
            buffer = {}
            esperado = 0
            total_pacotes = None
            print("Handshake concluido com sucesso")

        elif tipo_msg == "DATA" and handshake_concluido:
            seq = mensagem.get("seq")
            payload = mensagem.get("payload")
            checksum = mensagem.get("checksum")
            ultimo = mensagem.get("ultimo", False)

            if not isinstance(seq, int) or not isinstance(payload, str):
                print("Pacote DATA malformado Ignorando")
                continue

            if calcular_checksum(payload) != checksum:
                print(f"Checksum invalido Seq {seq} Ignorando")
                continue

            print(f"Recebido DATA Seq {seq} Payload {payload} Checksum {checksum}")

            if modo_janela_atual == "GBN":
                if seq == esperado:
                    buffer[seq] = payload
                    esperado += 1
                    if ultimo:
                        total_pacotes = seq + 1
                ack_seq = esperado - 1 
            else:
                buffer[seq] = payload
                if ultimo:
                    total_pacotes = seq + 1
                ack_seq = seq

            if ack_seq >= 0:
                ack = {
                    "tipo": "ACK",
                    "seq": ack_seq
                }

                socket_server.sendto(
                    json.dumps(ack).encode(),
                    endereco
                )
                print(f"Enviado ACK Seq {ack_seq}")

            if total_pacotes is not None and all(i in buffer for i in range(total_pacotes)):
                texto_final = "".join(buffer[i] for i in range(total_pacotes))
                print(f"Texto completo recebido: {texto_final}")
                buffer = {}
                esperado = 0
                total_pacotes = None
                handshake_concluido = False

if __name__ == "__main__":
    main()