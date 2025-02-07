import os
import json
from simple_term_menu import TerminalMenu

# Caminho do arquivo para salvar as tarefas
TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    return {"pending": [], "completed": [], "archived": []}

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

def add_task(tasks):
    task = input("Digite a nova tarefa: ")
    if task:
        tasks["pending"].append(task)
        save_tasks(tasks)
        print("\033[92mTarefa adicionada com sucesso!\033[0m")
        input("Pressione Enter para continuar...")

def complete_task(tasks):
    if not tasks["pending"]:
        print("\033[91mNenhuma tarefa pendente.\033[0m")
        input("Pressione Enter para continuar...")
        return
    menu = TerminalMenu(tasks["pending"], title="Selecione a tarefa para completar:")
    choice = menu.show()
    if choice is not None:
        task = tasks["pending"].pop(choice)
        tasks["completed"].append(task)
        save_tasks(tasks)
        print("\033[92mTarefa concluída!\033[0m")
        input("Pressione Enter para continuar...")

def archive_tasks(tasks):
    if not tasks["completed"]:
        print("\033[91mNenhuma tarefa concluída para arquivar.\033[0m")
        input("Pressione Enter para continuar...")
        return
    tasks["archived"].extend(tasks["completed"])
    tasks["completed"] = []
    save_tasks(tasks)
    print("\033[93mTarefas arquivadas.\033[0m")
    input("Pressione Enter para continuar...")

def view_tasks(tasks):
    print("\n\033[94mTarefas Pendentes:\033[0m")
    for task in tasks["pending"]:
        print(f"  - {task}")
    print("\n\033[92mTarefas Concluídas:\033[0m")
    for task in tasks["completed"]:
        print(f"  - {task}")
    print("\n\033[90mTarefas Arquivadas:\033[0m")
    for task in tasks["archived"]:
        print(f"  - {task}")
    input("\nPressione Enter para continuar...")

def main():
    tasks = load_tasks()
    options = ["Adicionar Tarefa", "Completar Tarefa", "Arquivar Tarefas", "Ver Tarefas", "Sair"]
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        print("\033[96mGerenciador de Tarefas\033[0m\n")
        menu = TerminalMenu(options)
        choice = menu.show()
        if choice == 0:
            add_task(tasks)
        elif choice == 1:
            complete_task(tasks)
        elif choice == 2:
            archive_tasks(tasks)
        elif choice == 3:
            view_tasks(tasks)
        elif choice == 4:
            break

if __name__ == "__main__":
    main()
