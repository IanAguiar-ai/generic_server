"""
Server aberto para requisições e respostas.
"""
version = [0, 0, 3]

import socket
from threading import Thread
from time import sleep, time, localtime
from datetime import datetime
from os import listdir, path
from sys import exit

def time_now():
    data = localtime()
    d = data.tm_mday
    mt = data.tm_mon
    y = data.tm_year
    h = data.tm_hour
    m = data.tm_min
    s = data.tm_sec
    return [d, mt, y, h, m, s]

class Log:
    """
    Creates a txt log that stores information along with the machine's local time
    """
    def __init__(self, file:str = "log"):
        """
        file: File name next to directory
        """
        if file == "log":
            t = time_now()
            file += f"_{t[2]}_{t[1]:02}_{t[0]:02}"
        if file.find(".txt") == -1:
            file += ".txt"
        self.file = file
        self.name = id(self)
        self.time_initial = time_now()
        self.create_file()

    def create_file(self):
        """
        Create txt file if file does not exist
        """
        if not path.isfile(self.file):
            with open(self.file, 'w') as arq:
                t = self.time_initial
                arq.write(f"<log creation> {t[0]:02}/{t[1]:02}/{t[2]} - {t[3]:02}:{t[4]:02}:{t[5]:02}")
                arq.write("""Níveis de registro:
fatal	A tarefa não pode continuar e o componente, o aplicativo e o servidor não podem funcionar.
severe	A tarefa não pode continuar mas o componente, aplicativo e servidor ainda podem funcionar. Esse nível também pode indicar um erro irrecuperável iminente.
aviso	Erro potencial ou erro iminente. Este nível também pode indicar um defeito progressivo (por exemplo, a possível perda de recursos).
audit	Evento significativo afetando o estado do servidor ou os recursos.
config	Alteração na configuração ou status.""")

        else:
            self.add(text = f"connecting to the log", description = "action")

    def add(self, text:str, description:str = "info"):
        """
        Add the requested text next to the time

        Níveis de registro:
        fatal	A tarefa não pode continuar e o componente, o aplicativo e o servidor não podem funcionar.
        severe	A tarefa não pode continuar mas o componente, aplicativo e servidor ainda podem funcionar. Esse nível também pode indicar um erro irrecuperável iminente.
        aviso	Erro potencial ou erro iminente. Este nível também pode indicar um defeito progressivo (por exemplo, a possível perda de recursos).
        audit	Evento significativo afetando o estado do servidor ou os recursos.
        config	Alteração na configuração ou status.
        """
        if path.isfile(self.file):
            with open(self.file, 'r') as arq:
                old = arq.read()
        else:
            print("The log has been lost!")

        if path.isfile(self.file):
            with open(self.file, 'w') as arq:
                t = time_now()
                arq.write(f"{old}\n<{description}> {t[0]:02}/{t[1]:02}/{t[2]} - {t[3]:02}:{t[4]:02}:{t[5]:02} | {text}")
        else:
            print("The log has been lost!")

    def backup(self, new_log:str = "backup_log"):
        """
        Back up the specified log
        new_log: Backup txt name
        """
        if new_log.find(".txt") == -1:
            new_log += ".txt"
        self.add(text = f"Make copy to '{new_log}'", description = "backup")
        with open(self.file, 'r') as arq:
            old = arq.read()
        if not path.isfile(new_log):
            with open(new_log, 'w') as arq:
                arq.write(old)

    def read(self):
        """
        Reads the log and returns a dictionary
        """
        self.add(text = f"getting log", description = "action")
        
        with open(self.file, 'r') as arq:
            old = arq.read()
        all_log = old.split("\n")
        
        all_log_dict = {}
        for i in range(len(all_log)):
            all_log[i] = all_log[i].replace("<","").split(">")
            if not all_log[i][0] in all_log_dict:
                all_log_dict[all_log[i][0]] = [all_log[i][1][1:]]
            else:
                all_log_dict[all_log[i][0]].append(all_log[i][1][1:])

        all_log_dict["all"] = old.split("\n")        
        return all_log_dict

    def clean(self):
        """
        Clear the log
        """
        if path.isfile(self.file):
            with open(self.file, 'w') as arq:
                t = time_now()
                arq.write(f"<log creation> {t[0]:02}/{t[1]:02}/{t[2]} - {t[3]:02}:{t[4]:02}:{t[5]:02}")
        else:
            print("The log has been lost!")

    def __repr__(self):
        log = self.read()
        t = self.time_initial
        text = f"Log: {self.file}\nCreation Log: {log['log creation'][0]}\nOpen log: {t[0]:02}/{t[1]:02}/{t[2]} - {t[3]:02}:{t[4]:02}:{t[5]:02}\nLines Log: {len(log['all'])}"
        return text


def _ip_adress_():
    """
    Obtain ip in linux
    """
    try:
        import netifaces
    except:
        print("In thre terminal:\npip install netifaces")
        sleep(30)
        exit()
    try:
        import requests
    except:
        print("In thre terminal:\npip install request")
        sleep(30)
        exit()

    interfaces = netifaces.interfaces()
    for interface in interfaces:
        try:
            ip_adress = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]['addr']
            if ip_adress != '127.0.0.1':
                print(f"IPv6:{ip_adress}")
        except (KeyError, IndexError):
            pass

    response = requests.get('https://httpbin.org/ip')
    return response.json()['origin']

class Server:
    def __init__(self, port:int = 20241, limit:int = 3, logic = None, key = None):
        self.points = {}
        self.equivalent = {"ip":{}, "int":{}}
        self.print__ = True
        self.send_to = {}
        self.condition = {}
        self.program = {}

        #Funções:
        self.logic = logic 
        #text = self.logic(self, text:str, ip:str, port:int) -> str
        #Recebe:
        # - objeto server:class
        # - texto:str
        # - ip:str
        # - porta:int
        #Retorna:
        # - texto:str

        self.key = key
        #list_ip = self.key(list(map(int, self.ip.split("."))))
        #Recebe:
        # - ip:str
        #Retorna:
        # - key:str
    
        #Configuração:
        self.port = port
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        self.socket.listen(limit)
        self.ip = socket.gethostbyname(socket.gethostname())
        if self.ip == "127.0.1.1":
            self.print_("The local IP was passed, getting the global IP...")
            self.ip = _ip_adress_()        
        
        with open("ip.txt", 'w') as arq:
            arq.write(self.ip)

        if self.key != None:
            with open("key.txt", 'w') as arq:
                arq.write(".".join(list(map(str,self.key(list(map(int, self.ip.split("."))))))))

    def __repr__(self):
        return f"Servidor escutando em {self.port} com o ip {self.ip} {self.socket.getsockname()}"

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
        log.add(f"Open socket {self.socket.getsockname()}", "audit")
        try:
            con, client = self.socket.accept() #Abre o socket
        except OSError:
            print("Thread principal foi fechado...")
            log.add(f"Close thread server", "fatal")
            exit()
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
            
        try:
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
        finally:
            log.add(f"Close socket", "audit")
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
                    self.print_(f"{blocks} blocos necessários para mandar o {program}")
                    return str(blocks)#Retorna o número de requisições necessárias
                except FileNotFoundError:
                    self.print_(f"O programa {program} não existe no diretório atual!")
                    log.add(f"Not find {program}, can not send this", "aviso")
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
            log.add(text = text)

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
        log.add(f"No file {name}", "aviso")
        with open(name, "w") as arq:
            pass
        print(f"Criado arquivo {name}\n")
        log.add("{name} created", "audit")

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
{'-' * 50}\n\n
Níveis de registro:
fatal	A tarefa não pode continuar e o componente, o aplicativo e o servidor não podem funcionar.
severe	A tarefa não pode continuar mas o componente, aplicativo e servidor ainda podem funcionar. Esse nível também pode indicar um erro irrecuperável iminente.
aviso	Erro potencial ou erro iminente. Este nível também pode indicar um defeito progressivo (por exemplo, a possível perda de recursos).
audit	Evento significativo afetando o estado do servidor ou os recursos.
config	Alteração na configuração ou status.
{'-' * 50}\n\n""")
    
    text_old = Memory()
    while True:
        sleep(0.5)
        
        text_ = see_txt("comando.txt", text_old)

        if text_ != None:
            for text in text_:
                log.add(description = "root", text = text)
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
                    log.add(f"server.print_ = {server.print_}", "config")

                #Informacoes:
                elif text == "exit":
                    print("Terminando conexão!\n")
                    server.socket.close()
                    log.add(description = "fatal", text = "exit")
                    exit()     

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
                        log.add("block {new_text[1]}", "audit")
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
                        gloabals()["log"].add( "next message for {new_text[1]} = '{send_text}'", "audit")
                    except KeyError:
                        print(f"'{new_text[1]}' não está registrado.\n")

                elif text.find("if") > -1:
                    new_text = text.split(" ")
                    new_text[1] = new_text[1].replace("#"," ")
                        
                    server.condition[new_text[1]] = new_text[2]
                    print(f"Resposta definida: {new_text[1]} -> {new_text[2]}\n")
                    globals()["log"].add("if {new_text[1]} return {new_text[2]}", "audit")
                

def run_server(server, memory):
    """
    Loop principal no thread
    """
    while True:
        server.run_server(memory)

def main(port:int = 20241, limit:int = 3, logic = None):
    print(f"Version {'.'.join(list(map(str, globals()['version'])))}")
    globals()["log"] = Log()
    globals()["log"].add(f"Version {'.'.join(list(map(str, globals()['version'])))}")
    memory = Memory()
    globals()["log"].add("memory created")
    server = Server(port, limit, logic)
    globals()["log"].add(f"server created, chanel {server.ip}:{server.port}")
    print(server)

    process_server = Thread(target = run_server, args = [server, memory])
    globals()["log"].add(f"run server")
    process_server.start()
        
    try:
        comand_line(memory, server) #Está na thread main
    except KeyboardInterrupt:
        globals()["log"].add("root keyboard interrupt", "audit")
        print("Kill comand_line")

    process_server.join()

if __name__ == "__main__":
    main()

