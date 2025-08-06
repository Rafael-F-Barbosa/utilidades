from simple_term_menu import TerminalMenu

from models import Atividade
from repository import AtividadeRepository

status_bar="\nUse ↑↓ para navegar e Enter para selecionar\nAções:\n\
    d - para deletar atividade principal\n\
    r - para selecionar atividade principal\n\
    c - para criar atividade atividade principal\n\
    x - para sair"

class Tela:
    def __init__(self):
        self.repo = AtividadeRepository()
        
        pass
    
    def transforma_estrutura_arvore_em_lista(self, dados):
        atividades_planas = []

        def percorrer(node):
            # Adiciona a atividade atual
            atividades_planas.append(node['atividade'])
            # Percorre os filhos recursivamente
            for filho in node['filhos']:
                percorrer(filho)

        # Se for lista de nós raiz
        if isinstance(dados, list):
            for item in dados:
                percorrer(item)
        else:  # Se for só um nó raiz
            percorrer(dados)

        return atividades_planas

    def imprime_item(self, at: Atividade):
        tabulacao=2
        return f"{at.profundidade * ' ' * tabulacao}- {at.nome}"
        
    def formata_lista_para_impressao(self, lista: list[Atividade]):
        lista_formatada = []
        
        for l in lista:
            lista_formatada.append(self.imprime_item(l))

        return lista_formatada

    def apresenta_menu_inicial(self):
        atividades_pai = self.repo.obter_atividades_principais()
    
        atividades = []
        for at in atividades_pai:
            atividades.append(self.repo.obter_atividades_com_profundidade(at, -1))

        lista_atividades = self.transforma_estrutura_arvore_em_lista(atividades)
        
        
        abas = []
        
        index = 0
        for ap in lista_atividades:
            abas.append((index, self.imprime_item(ap), ap.id))
            index += 1
        
        menu_labels = [
            f"{f'[{key}] ' if not str(key).isdigit() else ''}{label}" for key, label, id in abas
        ]

        terminal_menu = TerminalMenu(
            menu_labels, 
            title="Tarefas", 
            accept_keys=["enter", "x", "c", "r", "d", "a"], 
            clear_screen=True,
            status_bar=status_bar
        )

        index_selecionado = terminal_menu.show()
        
        tecla_utilizada = terminal_menu.chosen_accept_key
        
        valor_selecionado = None
        atividade = None
        if index_selecionado is not None:
            valor_selecionado = str(abas[index_selecionado][0])
        
            if valor_selecionado.isnumeric():
                atividade = int(abas[index_selecionado][2])

            return int(index_selecionado), valor_selecionado, tecla_utilizada, atividade
        return int(-1), valor_selecionado, tecla_utilizada, atividade
    
    def apresenta_menu_gerencial(self):
        print("Menu gerencial\n")
        
        atividades = self.repo.obter_atividades_principais()
        
        abas = []
        index = 0
        
        for ap in atividades:
            abas.append((index, ap.nome))
            index += 1
        
        menu_labels = [f"[{key}] {label}" for key, label in abas]

        terminal_menu = TerminalMenu(menu_labels, clear_screen=True, title="Atividades Pricipais\n", accept_keys=["d", "r", "c",  "enter", "q"],
            status_bar="\nUse ↑↓ para navegar e Enter para selecionar\nAções:\n  d - para deletar atividade principal\n  r - para selecionar atividade principal\n  c - para criar atividade atividade principal\n  q - para voltar ao menu principal")
        
        
        index_selecionado = terminal_menu.show() 

        tecla_utilizada = terminal_menu.chosen_accept_key
        
        
    def apresenta_menu_atividade_criar_filha(self, id_atividade: int):
        atividade_pai = self.repo.obter(id_atividade)
        
        print(f"Atividade: {atividade_pai.nome}")
        
        nome_nova_atividade = input("Escreva o nome da atividade filha ou digite :q para cancelar...\n")

        if nome_nova_atividade == ":q":
            return
        
        else:
            nova_atividade = Atividade()
            nova_atividade.nome = nome_nova_atividade
            nova_atividade.parent_id = id_atividade
            self.repo.add(nova_atividade)
    
    
    def apresenta_menu_atividade_renomear(self, id_atividade: int):
        atividade = self.repo.obter(id_atividade)
        
        print(f"Atividade: {atividade.nome}")
        
        nome_nova_atividade = input("Escreva novo nome para atividade ou :q para cancelar...\n")

        if nome_nova_atividade == ":q":
            return
        
        else:
            atividade.nome = nome_nova_atividade
            self.repo.editar(atividade)

    def apresenta_menu_atividade_deletar(self, id_atividade: int):
        
        self.repo.deletar(id_atividade)
    
    
    def apresenta_menu_atividade_criar_irma(self, id_atividade: int):
        atividade = self.repo.obter(id_atividade)
        
        if atividade.parent_id is None:
            print(f"Atividade principal")
            nome_nova_atividade = input("Escreva o nome da atividade principal ou digite :q para cancelar...\n")

            if nome_nova_atividade == ":q":
                return
            else:
                nova_atividade = Atividade()
                nova_atividade.nome = nome_nova_atividade
                self.repo.add(nova_atividade)

            return

        atividade_pai = self.repo.obter(atividade.parent_id)
        
        print(f"Atividade: {atividade.nome}")
        nome_nova_atividade = input("Escreva o nome da atividade filha ou digite :q para cancelar...\n")

        if nome_nova_atividade == ":q":
            return
        else:
            nova_atividade = Atividade()
            nova_atividade.nome = nome_nova_atividade
            nova_atividade.parent_id = atividade.parent_id
            self.repo.add(nova_atividade)