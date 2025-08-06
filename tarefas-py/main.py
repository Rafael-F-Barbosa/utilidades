from simple_term_menu import TerminalMenu

from repository import AtividadeRepository
from models import Atividade
from view import Tela


def main():
    while True:
        
        tela = Tela()

        _, valor_selecionado, tecla_utilizada, atividade = tela.apresenta_menu_inicial()

        
        if atividade is not None and tecla_utilizada == "a":
            tela.apresenta_menu_atividade_criar_irma(atividade)

        if atividade is not None and tecla_utilizada == "c":
            tela.apresenta_menu_atividade_criar_filha(atividade)
            
        if atividade is not None and tecla_utilizada == "r":
            tela.apresenta_menu_atividade_renomear(atividade)
        
        if atividade is not None and tecla_utilizada == "d":
            tela.apresenta_menu_atividade_deletar(atividade)
            
        elif tecla_utilizada == "x":
            print("Encerrando...")
            break
        
if __name__ == "__main__":
    main()
