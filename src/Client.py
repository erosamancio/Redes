import socket
import json

HOST = "127.0.0.1"
PORT = 7777
TAMANHO_PAYLOAD = 4
DESLOCAMENTO = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]

def calcular_checksum(payload):
    return sum(payload.encode()) % 65536

def handshake(socket_client):
    while True:
        try:
            tamanho_max = int(input("Tamanho maximo do texto: "))
            if tamanho_max < 30:
                tamanho_max = 30
            break
        except ValueError:
            print("Digite um numero inteiro valido.")

    chave = input("Digite a chave da criptografia: ").upper().strip()
    while not (chave and chave.isascii() and chave.isalpha()):
        print("A chave deve ter apenas letras de A a Z.")
        chave = input("Digite a chave da criptografia: ").upper().strip()

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
        "tamanho_max_texto": tamanho_max,
        "chave": chave,
        "deslocamento": DESLOCAMENTO
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
        return None, None, None, None, None

    try:
        texto_resposta = data.decode()
        resposta = json.loads(texto_resposta)

    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Resposta do servidor corrompida")
        return None, None, None, None, None

    if resposta.get("tipo") != "HANDSHAKE_ACK":
        print("Resposta inesperada do servidor")
        return None, None, None, None, None

    print(resposta)

    return (
        resposta.get("janela_final"),
        resposta.get("tamanho_max_texto"),
        resposta.get("modo_janela"),
        resposta.get("chave", chave),
        resposta.get("deslocamento", DESLOCAMENTO)
    )

def criptografar(texto, chave):
    resultado = ""
    indice_chave = 0
    for letra in texto:
        if letra.isascii() and letra.isalpha():
            deslocamento = DESLOCAMENTO[ord(chave[indice_chave]) - 65]
            if letra.isupper():
                resultado += chr((ord(letra) - 65 + deslocamento) % 26 + 65)
            else:
                resultado += chr((ord(letra) - 97 + deslocamento) % 26 + 97)
            indice_chave += 1
            if indice_chave == len(chave):
                indice_chave = 0
        else:
            resultado += letra
            continue
    return resultado

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

def configurar_falha(total_pacotes):
    print("\n=== SIMULADOR DETERMINISTICO ===")
    print("A - Erro de integridade (checksum invalido)")
    print("B - Perda de pacote DATA")
    print("C - Perda de ACK (descarte no cliente)")
    print("D - Sem erros")
    while True:
        cenario = input("Escolha A, B, C ou D: ").upper().strip()
        if cenario in ("A", "B", "C", "D"):
            break
        print("Opcao invalida.")

    seq_padrao = {"A": 2, "B": 1, "C": 2}
    if cenario == "D":
        return {"cenario": cenario, "seq": None, "falhas_aplicadas": set()}

    padrao = min(seq_padrao[cenario], total_pacotes - 1)
    while True:
        entrada = input(f"Sequencia alvo (0 a {total_pacotes - 1}) [padrao {padrao}]: ").strip()
        try:
            seq = padrao if not entrada else int(entrada)
            if 0 <= seq < total_pacotes:
                break
        except ValueError:
            pass
        print("Sequencia invalida.")

    print(f"Cenario {cenario} selecionado para seq={seq} (somente uma vez).")
    return {"cenario": cenario, "seq": seq, "falhas_aplicadas": set()}


def enviar_pacote(socket_client, seq, payload, total_pacotes, simulador=None):
    pacote = {
        "tipo": "DATA",
        "seq": seq,
        "payload": payload,
        "checksum": calcular_checksum(payload),
        "ultimo": seq == total_pacotes - 1
    }

    if simulador is not None:
        cenario = simulador["cenario"]
        falha = (cenario, seq)
        primeira_vez = (seq == simulador["seq"] and falha not in simulador["falhas_aplicadas"])
        if primeira_vez and cenario == "B":
            simulador["falhas_aplicadas"].add(falha)
            print(f"[SIMULACAO B] DATA seq={seq} descartado antes do sendto")
            return
        if primeira_vez and cenario == "A":
            simulador["falhas_aplicadas"].add(falha)
            pacote["checksum"] = (pacote["checksum"] + 1) % 65536
            print(f"[SIMULACAO A] Checksum adulterado em DATA seq={seq}")

    socket_client.sendto(json.dumps(pacote).encode(), (HOST, PORT))
    print(f"Enviado Pacote DATA Seq {seq} Payload {payload}")

def enviar_pacotes_iniciais(socket_client, payloads, janela, simulador=None):
    total_pacotes = len(payloads)
    limite_envio = min(janela, total_pacotes)

    for seq in range(limite_envio):
        enviar_pacote(socket_client, seq, payloads[seq], total_pacotes, simulador)

    return limite_envio

def receber_acks(socket_client, payloads, janela, modo_janela, proximo, simulador=None):
    total_pacotes = len(payloads)
    confirmados = set()
    base = 0

    while base < total_pacotes:
        try:
            data, endereco = socket_client.recvfrom(1024)
            ack = json.loads(data.decode())
        except socket.timeout:
            print("Timeout esperando ACK")
            break
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

        if ack.get("tipo") == "NACK":
            seq_nack = ack.get("seq")

            if type(seq_nack) is not int or not (0 <= seq_nack < proximo):
                print("NACK invalido; ignorando")
                continue

            if seq_nack < base or (modo_janela == "SR" and seq_nack in confirmados):
                print(f"NACK antigo para seq={seq_nack}; ignorando")
                continue

            print(f"Recebido NACK seq={seq_nack}. Retransmitindo imediatamente...")
            enviar_pacote(socket_client, seq_nack, payloads[seq_nack], total_pacotes, simulador)
            continue

        if ack.get("tipo") != "ACK":
            continue

        seq = ack.get("seq")
        if not isinstance(seq, int) or not (0 <= seq < total_pacotes):
            continue

        if (simulador is not None and simulador["cenario"] == "C"
                and seq == simulador["seq"]
                and ("C", seq) not in simulador["falhas_aplicadas"]):
            simulador["falhas_aplicadas"].add(("C", seq))
            print(f"[SIMULACAO C] ACK seq={seq} recebido, mas descartado")
            continue

        print(f"Recebido ACK Seq {seq}")

        if modo_janela == "GBN":
            if seq + 1 > base:
                base = seq + 1
        else:
            confirmados.add(seq)
            while base in confirmados:
                base += 1

        while proximo < total_pacotes and proximo < base + janela:
            enviar_pacote(socket_client, proximo, payloads[proximo], total_pacotes, simulador)
            proximo += 1

    if base == total_pacotes:
        print("Todos os pacotes foram confirmados")

def main():
    socket_client = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    resposta_janela, resposta_tamanho, resposta_modo_janela, chave, deslocamento = handshake(socket_client)

    if resposta_janela is None or resposta_tamanho is None or resposta_modo_janela is None:
        socket_client.close()

    else:
        print("Janela final", resposta_janela)
        print("Tamanho maximo", resposta_tamanho)

        texto_valido = ler_input_usuario(resposta_tamanho)
        texto_cifrado = criptografar(texto_valido, chave)
        payloads = fragmentar_texto(texto_cifrado)

        simulador = configurar_falha(len(payloads))
        proximo = enviar_pacotes_iniciais(socket_client, payloads, resposta_janela, simulador)
        receber_acks(socket_client, payloads, resposta_janela, resposta_modo_janela, proximo, simulador)

        socket_client.close()

if __name__ == "__main__":
    main()