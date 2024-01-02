"""
Server aberto para requisições e respostas.
"""
version = [0, 0, 1]

import socket
from threading import Thread
from time import sleep, time
from datetime import datetime
from os import listdir

class Server:
    def __init__(self, host:str = "0.0.0.0", port:int = 20241, limit:int = 3, logic = None):
        self.points = {}
        self.equivalent = {"ip":{}, "int":{}}
        self.print__ = True
        self.send_to = {}
        self.condition = {}
        self.program = {}

        self.logic = logic #Função
        #text = self.logic(self, text:str, ip:str, port:int) -> str
        #Recebe:
        # - objeto server
        # - texto;
        # - ip;
        # - porta.
        #Retorna:
        # - texto.

        #Configuração:
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(limit)
        

    def __repr__(self):
        print(f"Servidor escutando em {host}:{porta}")
        return None

    def run_server(self, memory):
        """
        A hierarquia da resposta é dada por:
        1) Está bloqueado <server.points[ip]["block"]>
        2) Tem texto pedido root <server.send_to[ip]>
        3) Satisfaz uma condição passada pelo root em <self.condition[text]>
        4) Confere se existe pacotes de arquivos a serem mandados na lista <self.program[ip]>
        5) Confere na lógica passada ao criar o servidor. <server.logic>

        * Onde <ip> é o ip do ponto que fez a requisição;
        * <text> é o texto mandado pelo ponto;
        * <server> é o próprio objeto <self>.
        """
        con, client = self.socket.accept() #Abre o socket
        data = con.recv(1024).decode('utf-8') #Recebe 1024 bites do ponto
        ip, port = client[0], client[1] #Assim que um ponto conecta separa o ip e a porta

        self.print_(f"Conexão estabelecida com {client}")

        if not ip in self.equivalent["ip"]: #Confere se aquele ip já está registrado na base
            self.print_(f"Nova conexão {ip}!")
            len_ = len(self.equivalent["ip"].values())
            self.equivalent["ip"][ip] = len_
            self.equivalent["int"][len_] = ip
            self.points[ip] = {"block":False,
                               "first_time": time(),
                               "last_time": time()}
        else: #Se já está registrado atualiza o horário de request
            self.points[ip]["last_time"] = time()
            

        if not self.points[ip]["block"]: #Se ele não foi bloqueado em algum momento
            self.print_(f"{client} disse: {data}")

            if not ip in self.send_to: #Se não tem nada programado em primeiro nível para dizer ao ponto
                text = self.request(data, ip, port) #Entra na lógica principal do request
            else: #Se tem algo programado ele diz e apaga aquela mensagem da lista de a dizeres
                text = self.send_to[ip]
                del self.send_to[ip]

            if text != None: #Se o texto não for vazio ele manda:
                self.print_(f"Respondendo ao {ip} -> {text}")
                con.send(text.encode("utf-8"))
        else: #Se ele foi bloqueado ele é avisado:
            self.print_(f"Respondendo ao {ip} -> You is blocket!")
            con.send("You is blocket!".encode("utf-8"))

        con.close() #A conexão é fechada

    def request(self, text, ip, port):
        """
        Lógica principal.
        """
        if text in self.condition: #Se o texto está igual as condições salvas pelo root
            return self.condition[text]

        elif text.find("send_program") > -1: #Requisição para mandar um programa
            if not ip in self.program: #Se não tem nenhuma requisição anterior para qualquer programa neste ip
                try:
                    len_block = 950
                    text = text.split(" ")
                    program = "§" + text[1]
                    with open(program, "r") as pr_:
                        pr = pr_.read()
                        blocks = int(len(pr)/len_block) + 1
                        blocks_part = []
                        for i in range(0, blocks):
                            blocks_part.append(pr[i*len_block: (i+1)*len_block])
                    self.program[ip] = blocks_part
                    self.print_("{blocks} blocos necessários para mandar o {program}")
                    return str(blocks)#Retorna o número de requisições necessárias
                except FileNotFoundError:
                    print(f"O programa {program} não existe no diretório atual!")
                    return "0"
            else: #Se já existe uma requisição de programa para este ip
                to_send = self.program[ip][0]
                self.program[ip].pop(0)
                if len(self.program[ip]) == 0: #Se os pacotes acabaram apaga o ip da lista de programas a mandar
                    del self.program[ip]
                return to_send

        elif self.logic != None: #Se existir uma lógica importada ao servidor
            return self.logic(self, text, ip, port)

        return None

    def print_(self, text):
        """
        Printa.
        """
        if self.print__ == True:
            # Formatar a saída
            format_ = "%Y-%m-%d %H:%M:%S"
            data = datetime.now().strftime(format_)
            print(f"{data} | {text}")

class Memory:
    """
    Memória entre processos.
    """
    def __init__(self):
        self.save = None

def see_txt(name:str, text_old):
    """
    Lê o comando manual do root.
    """
    try:
        with open(name, "r") as arq:
            text = arq.read()
            text = text.split("\n")
            if text_old.save != text:
                print(f"Comando mandado <{text}>")
                text_old.save = text
                return text
            else:
                return None
    except FileNotFoundError:
        with open(name, "w") as arq:
            pass
        print(f"Criado arquivo {name}\n")

def comand_line(memory, server):
    """
    Lógica da manipulação do servidor pelo root por meio do txt 'comando.txt'.
    """
    print(f"""{'-'*50}\nComandos:
<código> [variável] descrição



<print> diz se o server deve ou não printar as entradas

<exit> sai do programa
<ips> vê os ips conectados ou que já conectaram em algum momento
<to send> mostra a próxima mensagem que vai mandar a cada ip

<block [ip]> bloqueia um ip
<send_to [ip]> salva a próxima mensagem a mandar para um ip
<if [algo] [faz algo]> salva uma condicional para mandar para os pontos caso satisfaça a condição
<data> mostra os programas permitidos para mandar com o a requisição do ponto <send_program>



server.points
server.equivalent
server.send_to
server.condition
{'-' * 50}\n\n""")
    
    text_old = Memory()
    while True:
        sleep(0.5)
        
        text_ = see_txt("comando.txt", text_old)

        if text_ != None:
            for text in text_:
                #Salvando texto:
                if text != "":
                    memory.save = text
                else:
                    memory.save = None

                #Mudando definições no server:
                if text == "print":
                    print(f"Mudando estado do print do server de {server.print__} para ", end = "")
                    if server.print__:
                        server.print__ = False
                        print("False\n")
                    else:
                        server.print__ = True
                        print("True\n")

                #Informacoes:
                elif text == "exit":
                    print("Terminando coneção!\n")
                    return None            

                elif text == "ips":
                    for key in server.equivalent["ip"]:
                        print(f"{key} -> {server.equivalent['ip'][key]}")
                    print("\n")

                elif text == "to send":
                    for key in server.send_to:
                        print(f"{key} -> {server.send_to[key]}")
                    print("\n")

                elif text == "data":
                    for permission in [".txt", ".py"]:
                        print(f"Permitidos '{permission}':")
                        for program in listdir():
                            if program.find(permission) > -1 and program[0] == "§":
                                print(program.replace("§",""))
                        print("\n")

                    for key in server.program:
                        print(f"{key} tem {server.program[key]} blocos a mandar")
                    print("\n")

                #Operações:
                elif text.find("block") > -1:
                    try:
                        new_text = text.split(" ")
                        if len(new_text[1]) <= 6:
                            new_text[1] = server.equivalent["int"][int(new_text[1])]

                        server.points[new_text[1]]["block"] = True
                        print(f"{new_text[1]} foi bloqueado!\n")
                    except KeyError:
                        print(f"'{new_text[1]}' não está registrado.\n")

                elif text.find("send_to") > -1:
                    try:
                        new_text = text.split(" ")
                        if len(new_text[1]) <= 6:
                            new_text[1] = server.equivalent["int"][int(new_text[1])]

                        send_text = ""
                        for i in range(2, len(new_text)):
                            send_text += new_text[i] + " "
                            
                        server.send_to[new_text[1]] = send_text
                        print(f"Mensagem '{send_text}' salva para envio do {new_text[1]}.\n")
                    except KeyError:
                        print(f"'{new_text[1]}' não está registrado.\n")

                elif text.find("if") > -1:
                    new_text = text.split(" ")
                    new_text[1] = new_text[1].replace("#"," ")
                        
                    server.condition[new_text[1]] = new_text[2]
                    print(f"Resposta definida: {new_text[1]} -> {new_text[2]}\n")                    
                

def run_server(server, memory):
    """
    Loop principal no thread
    """
    while True:
        server.run_server(memory)

if __name__ == "__main__":
    memory = Memory()
    server = Server()

    process_server = Thread(target = run_server, args = [server, memory])
    process_server.start()
    
    comand_line(memory, server) #Está na thread main
    process_server.join()

