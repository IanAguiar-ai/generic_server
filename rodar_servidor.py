from threading import Thread
from time import sleep
import sys
import importlib
import server_master

def atualizar():
    import requests
    import os

    url = "https://raw.githubusercontent.com/IanAguiar-ai/generic_server/main/server_master.py"
    nome_arquivo = "server_master.py"

    response = requests.get(url)

    if os.path.exists(nome_arquivo):
        os.remove(nome_arquivo)

    if response.status_code == 200:
        with open(nome_arquivo, 'wb') as arquivo:
            arquivo.write(response.content)
        print(f"Conteúdo baixado com sucesso e salvo em '{nome_arquivo}'.")
    else:
        print(f"Erro ao baixar o conteúdo. Código de status: {response.status_code}.")

if __name__ == "__main__":
    while True:
        atualizar()
        
        importlib.reload(server_master)
        
        t1 = Thread(target = server_master.main)
        t1.start()

        sleep(5)
        print("Esperando processo terminar...")
        with open("comando.txt", "w") as arq:
            arq.write("exit")
        sleep(2)
        with open('comando.txt', 'w') as arquivo:
            pass  # Nada é escrito, resultando em um arquivo vazio
        sleep(1)
        t1.join()
        del t1
        print("Terminado")

        print("Server reiniciando em 100 segundos", end = "")
        for i in range(10):
            print(".", end = "")
            sleep(10)
        print(f"{'-'*50}\n\n")

        
        
    
