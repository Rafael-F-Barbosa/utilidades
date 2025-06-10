#!/usr/bin/env python3
import os
import json
from simple_term_menu import TerminalMenu

# Execução de qualquer pasta no linux
# Se necessário alterar: 
#   sudo rm /usr/local/bin/k8s
# Criar link simbólico para o script: 
#   sudo ln -s /home/rafael/suite-k8s-python/main.py /usr/local/bin/k8s
# Dar permissão de execução: 
#   chmod  +x  /usr/local/bin/k8s

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from k8s import obter_pods, obter_secrets, obter_logs, obter_configmaps

# Caminho do arquivo para salvar as tarefas
NAMESPACES_FILE = "/home/rafael/suite-k8s-python/namespaces.json"
CONFIG_FILE = "/home/rafael/suite-k8s-python/config.json"

def obter_namespace_selecionado(arquivo_configuracao):
    return arquivo_configuracao['namespace_selecionado']

def salvar_arquivo_configuracao(nome_arquivo, configs):
    with open(nome_arquivo, "w") as file:
        json.dump(configs, file, indent=4)

def obter_arquivo_configuracao(nome_arquivo, arquivo_configuracao_padrao):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "r") as file:
            return json.load(file)
    salvar_arquivo_configuracao(CONFIG_FILE, arquivo_configuracao_padrao)
    return arquivo_configuracao_padrao

def gerenciar_namespace_de_trabalho(arquivo_configuracao):
    opcoes = obter_arquivo_configuracao(NAMESPACES_FILE, [])
    
    completer = WordCompleter(opcoes, ignore_case=True)

    namespace = prompt('Digite um namespace ou selecione um(TAB): ', completer=completer)
    
    if not namespace:
        print("Namespace não pode ser vazio.")
        return gerenciar_namespace_de_trabalho()

    # Se namespace não estiver na lista de opções, adiciona-o no início da lista
    if namespace not in opcoes:
        opcoes.insert(0, namespace)
    else:
        opcoes.remove(namespace)
        opcoes.insert(0, namespace)

    arquivo_configuracao['namespace_selecionado'] = namespace
    salvar_arquivo_configuracao(CONFIG_FILE, arquivo_configuracao)
    salvar_arquivo_configuracao(NAMESPACES_FILE, opcoes)
    return namespace

def main():
    options = ["Listar pods", "Listar secrets", "Obter logs", "Obter configmaps", "Trocar namespace", "Sair"]
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        print("\033[96mk8s ligeiro\033[0m\n")
        
        arquivo_configuracao = obter_arquivo_configuracao(CONFIG_FILE, {"namespace_selecionado": ""})
        namespace_selecionado = obter_namespace_selecionado(arquivo_configuracao)
        if(namespace_selecionado == ""):
            namespace_selecionado = gerenciar_namespace_de_trabalho(arquivo_configuracao)
        else:
            print("namespace atual: ", namespace_selecionado)

        print("Escolha uma ação:")

        menu = TerminalMenu(options)
        choice = menu.show()

        if choice == 0:
            pods = obter_pods(namespace_selecionado)
        if choice == 1:
            secrets = obter_secrets(namespace_selecionado)
        elif choice == 2:
            pods = obter_pods(namespace_selecionado)
            logs = obter_logs(pods)
        elif choice == 3:
            configmaps = obter_configmaps(namespace_selecionado)
        elif choice == 4:
            namespace_selecionado = gerenciar_namespace_de_trabalho(arquivo_configuracao)
        elif choice == 5:
            print("Saindo...")
            break

if __name__ == "__main__":
    main()