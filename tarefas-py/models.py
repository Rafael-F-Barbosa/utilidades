class Atividade:
    def __init__(self, id=None, nome=None, parent_id=None):
        self.id = id
        self.nome = nome
        self.parent_id = parent_id
        self.profundidade = 0
    def __init__(self, id=None, nome=None, parent_id=None, profundidade = None):
        self.id = id
        self.nome = nome
        self.parent_id = parent_id
        self.profundidade = 0

    def __repr__(self):
        return f"Atividade(id={self.id}, nome='{self.nome}', parent_id={self.parent_id}, profundidade={self.profundidade})"
