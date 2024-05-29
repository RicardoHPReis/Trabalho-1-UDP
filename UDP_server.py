import socket as s
import time as t
import logging as l
import threading as th
import hashlib as h
import os

NOME_DO_SERVER = ''
PORTA_DO_SERVER = 6000
TAM_BUFFER = 2048
PORTAS_EM_USO = [6000,]

# Funções padrão --------------------------------------------

def titulo():
    print("--------------------")
    print("      SERVIDOR")
    print("--------------------\n")


def print_mensagem(mensagem, mensagem_modificada, endereco_server):
    titulo()
    print("--------------------")
    print('Recebido: ', mensagem, ' - Enviou: ', mensagem_modificada, ' - Cliente: ', endereco_server)
    print("--------------------\n")


# def main():

logger = l.getLogger(__name__)
l.basicConfig(filename="server.log", encoding="utf-8", level=l.INFO, format="%(levelname)s - %(asctime)s: %(message)s")

inicializar = ''
iniciar_server = True
while inicializar == '':
    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    inicializar = input("Deseja inicializar o servidor [S/N] ? ").lower()
    match inicializar:
        case 's':
            iniciar_server = True
        case 'sim':
            iniciar_server = True
        case 'n':
            iniciar_server = False
        case 'não':
            iniciar_server = False
        case _:
            print('A escolha precisa estar nas opções acima!')
            t.sleep(2)
            erro_arquivo = ''

os.system('cls' if os.name == 'nt' else 'clear')
server_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
server_socket.bind((NOME_DO_SERVER, PORTA_DO_SERVER))


def envio_parte_arquivo(retorno_socket: s.socket, nome_arquivo: str, parte: str, endereco: tuple):
    if not os.path.exists(os.path.join("./Arquivos", nome_arquivo)):
        retorno_socket.sendto("ERROR Arquivo não encontrado".encode(), endereco)
        return

    num_pacotes = (os.path.getsize(os.path.join("./Arquivos", nome_arquivo)) // TAM_BUFFER) + 1

    num_digitos = len(str(num_pacotes))
    if int(parte) > num_pacotes - 1:
        retorno_socket.sendto("ERROR Pacote não existe".encode(), endereco)

    with open(os.path.join("./Arquivos", nome_arquivo), "rb") as arquivo:
        i = 0
        while data := arquivo.read(TAM_BUFFER):
            if int(parte) == i:
                hash_ = h.md5(data).digest()
                retorno_socket.sendto(
                    b" ".join([f"{i:{'0'}{num_digitos}}".encode(), hash_, data]), endereco
                )
                break
            i += 1


def envio_arquivo_completo(retorno_socket: s.socket, nome_arquivo: str, endereco: tuple) -> None:
    if not os.path.exists(os.path.join("./Arquivos", nome_arquivo)):
        print("ERROR Arquivo não encontrado")
        retorno_socket.sendto("ERROR Arquivo não encontrado".encode(), endereco)
        return

    num_pacotes = (os.path.getsize(os.path.join("./Arquivos", nome_arquivo)) // TAM_BUFFER) + 1

    num_digitos = len(str(num_pacotes))

    retorno_socket.sendto(f"OK {num_pacotes} {num_digitos+1+16+1+TAM_BUFFER}".encode(), endereco)

    with open(os.path.join("./Arquivos", nome_arquivo), "rb") as file:
        i = 0
        while data := file.read(TAM_BUFFER):
            hash_ = h.md5(data).digest()
            retorno_socket.sendto(b" ".join([f"{i:{'0'}{num_digitos}}".encode(), hash_, data]), endereco)
            i += 1

    t.sleep(1)
    retorno_socket.sendto(b"END", endereco)


def requisicao_arquivo(message_: bytes, addr_: tuple):
    request = message_.decode().split()

    retorno_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)

    porta_aleatoria = PORTAS_EM_USO[len(PORTAS_EM_USO)-1] + 1
    PORTAS_EM_USO.append(porta_aleatoria)
    retorno_socket.bind((NOME_DO_SERVER, porta_aleatoria))

    logger.info(f"Requisição: '{message.decode()}', socket criado na porta: {porta_aleatoria}")
    print(f"Requisição: '{message.decode()}', socket criado na porta: {addr_}")

    if len(request) <= 1:
        print("ERROR Má requisição")
        retorno_socket.sendto("ERROR Má requisição".encode(), addr_)
        return

    if request[0] != "GET":
        print("ERROR Método não permitido")
        retorno_socket.sendto("ERROR Método não permitido".encode(), addr_)
        return
    
    nome_arquivo = request[1]
    arquivos_separados = nome_arquivo.split("/")
    if len(arquivos_separados) > 1:
        envio_parte_arquivo(retorno_socket, arquivos_separados[0], arquivos_separados[1], addr_)
    else:
        envio_arquivo_completo(retorno_socket, nome_arquivo, addr_)

    PORTAS_EM_USO.remove(porta_aleatoria)
    retorno_socket.close()


while iniciar_server:
    message, addr = server_socket.recvfrom(TAM_BUFFER)
    
    thread = th.Thread(target=requisicao_arquivo, args=(message, addr), daemon=True)
    thread.start()