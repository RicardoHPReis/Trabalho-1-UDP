import socket as s
import time as t
import hashlib as h
import os

NOME_DO_SERVER = '127.0.0.1'
PORTA_DO_SERVER = 6000
TAM_BUFFER = 2048

# Funções padrão --------------------------------------------

def titulo():
    print("--------------------")
    print("       CLIENTE")
    print("--------------------\n")


def print_envio(mensagem):
    print("--------------------")
    print('Enviado: ', mensagem)
    print("--------------------\n")


def print_recebimento(mensagem_modificada, endereco_server):
    print("--------------------")
    print('Recebido: ', mensagem_modificada, ' - Servidor: ', endereco_server)
    print("--------------------\n")

# def main():

cliente_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
cliente_socket.settimeout(60)

os.system('cls' if os.name == 'nt' else 'clear')
titulo()
nome_arquivo = input("Qual o nome do arquivo que você deseja receber? ")

config = True
erro_arquivo = ''
while erro_arquivo == '':
    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    erro_arquivo = input("Deseja remover algum socket [S/N] ? ").lower()
    match erro_arquivo:
        case 's':
            config = True
        case 'n':
            config = False
        case _:
            print('A escolha precisa estar nas opções acima!')
            t.sleep(2)
            erro_arquivo = ''

try:
    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    print('Enviando nome do arquivo!')
    cliente_socket.sendto(("GET " + nome_arquivo).encode(), (NOME_DO_SERVER, PORTA_DO_SERVER))

    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    print('Esperando resposta do servidor!')
    mensagem, endereco_server = cliente_socket.recvfrom(TAM_BUFFER)
    print('Recebeu!')
    
    num_pacotes = None
    if mensagem[0:5] == b"ERROR":
        response = mensagem.decode().split(" ")
        os.system('cls' if os.name == 'nt' else 'clear')
        titulo()
        print("Aconteceu um erro: ", " ".join(response[1:]))
    else:
        if mensagem[0:2] == b"OK":
            os.system('cls' if os.name == 'nt' else 'clear')
            titulo()
            print("Mensagem recebida com sucesso!")
            
            response = mensagem.decode().split(" ")
            num_pacotes = response[1]
            tam_buffer_server = response[2]
            buffer = []
            message, addr = cliente_socket.recvfrom(int(tam_buffer_server))
            
            descartar_pacote = -1
            if config:
                while descartar_pacote == -1:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    titulo()
                    num_inteiro = int(input(f"Qual pacote deseja jogar fora? (Escolha um número entre 0 e {int(num_pacotes)-1}): " ))
                    if isinstance(num_inteiro, int) and num_inteiro > -1 and num_inteiro < int(num_pacotes):
                        descartar_pacote = num_inteiro
                    else:
                        print('O número precisa ser válido!')
                        t.sleep(2)
                        

            for i in range(0, int(num_pacotes)):
                if message[0:3] == b"END":
                    break

                if i != int(descartar_pacote):
                    buffer.append(message)

                message, addr = cliente_socket.recvfrom(int(tam_buffer_server))
                
        if num_pacotes is not None:
            vet_arquivo = [None for i in range(int(num_pacotes))]

            num_digitos = len(str(num_pacotes))
            hash_inicial = num_digitos + 1
            hash_final = hash_inicial + 16
            
            for pacote in buffer:
                header = pacote[0:num_digitos]
                hash_ = pacote[hash_inicial:hash_final]
                data = pacote[hash_final + 1 :]

                if h.md5(data).digest() == hash_:
                    vet_arquivo[int(header)] = data

            arquivo = open(nome_arquivo, "wb")
            for index, segment in enumerate(vet_arquivo):
                if segment is not None:
                    arquivo.write(segment)
                else:
                    data = b"dkjasbda"
                    hash_ = b"dasjbadskd"
                    while h.md5(data).digest() != hash_:
                        cliente_socket.sendto(f"GET {nome_arquivo}/{index}".encode(), (NOME_DO_SERVER, PORTA_DO_SERVER))
                        message, addr = cliente_socket.recvfrom(int(tam_buffer_server))
                        hash_ = message[hash_inicial:hash_final]
                        data = message[hash_final + 1 :]
                    arquivo.write(data)
                    
            arquivo.close()
            
            os.system('cls' if os.name == 'nt' else 'clear')
            titulo()
            print("Arquivo transferido com sucesso!\n")

    cliente_socket.close()
    
except TimeoutError:
    os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    print("Excedeu-se o tempo para comunicação entre o servidor e o cliente!")

except Exception as e:
    #os.system('cls' if os.name == 'nt' else 'clear')
    titulo()
    print("Erro não registrado!")
    print(e)