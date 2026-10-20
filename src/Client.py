import socket
import json

HOST = "127.0.0.1"
PORT = 7777
TAMANHO_PAYLOAD = 4

def handshake(socket_client):
    while True:
        try:
            tamanho_max = int(input("Tamanho maximo do texto: "))
            if tamanho_max < 30:
                tamanho_max = 30
            break
        except ValueError:
            print("Digite um numero inteiro valido.")

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
            print(f"Sem resposta do servidor tentativa {tentativa} de {TENTATIVAS_MAX} Reenviando")

    if data is None:
        print("Servidor nao respondeu Encerrando")
        return None, None

    try:
        texto_resposta = data.decode()
        resposta = json.loads(texto_resposta)

    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Resposta do servidor corrompida")
        return None, None

    if resposta.get("tipo") != "HANDSHAKE_ACK":
        print("Resposta inesperada do servidor")
        return None, None

    print(resposta)

    return (
        resposta.get("janela_final"),
        resposta.get("tamanho_max_texto")
    )

def ler_input_usuario(tamanho_max):
    texto = input(f"Digite o texto da mensagem maximo de {tamanho_max} caracteres: ").strip()

    while len(texto) > tamanho_max or not texto:
        if not texto:
            texto = input(f"Texto vazio Tente novamente maximo de {tamanho_max} caracteres: ").strip()
        elif len(texto) > tamanho_max:
            texto = input(f"Texto ultrapassou limite maximo de {tamanho_max} caracteres Tente novamente: ").strip()

    return texto

def fragmentar_texto(texto_validado):
    fragmentos = []

    for i in range(0, len(texto_validado), TAMANHO_PAYLOAD):
        fragmentos.append(texto_validado[i:i+TAMANHO_PAYLOAD])

    return fragmentos

def enviar_pacotes_iniciais(socket_client, payloads, janela):
    total_pacotes = len(payloads)
    limite_envio = min(janela, total_pacotes)

    for seq in range(limite_envio):
        pacote = {
            "tipo": "DATA",
            "seq": seq,
            "payload": payloads[seq],
            "checksum": 0
        }
        
        socket_client.sendto(json.dumps(pacote).encode(), (HOST, PORT))
        print(f"Enviado Pacote DATA Seq {seq} Payload {payloads[seq]}")

def main():
    socket_client = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    resposta_janela, resposta_tamanho = handshake(socket_client)

    if resposta_janela is None or resposta_tamanho is None:
        socket_client.close()
    
    else: 
        print("Janela final", resposta_janela)
        print("Tamanho maximo", resposta_tamanho)

        texto_valido = ler_input_usuario(resposta_tamanho)
        payloads = fragmentar_texto(texto_valido)

        enviar_pacotes_iniciais(socket_client, payloads, resposta_janela)

        socket_client.close()

if __name__ == "__main__":
    main()