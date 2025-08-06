import sqlite3
from models import Atividade

class AtividadeRepository:
    def __init__(self, db_path="atividades.db"):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS atividades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY(parent_id) REFERENCES atividades(id)
                )
            """)
            
    def editar(self, atividade: Atividade):
        """
        Atualiza uma atividade existente no banco de dados.
        Necessário que a atividade tenha um id válido.
        """
        if atividade.id is None:
            raise ValueError("A atividade precisa ter um ID para ser editada.")

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE atividades SET nome = ?, parent_id = ? WHERE id = ?",
                (atividade.nome, atividade.parent_id, atividade.id)
            )
            
    def add(self, atividade: Atividade):
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO atividades (nome, parent_id) VALUES (?, ?)",
                (atividade.nome, atividade.parent_id)
            )
            atividade.id = cursor.lastrowid
        return atividade

    def obter(self, atividade_id: int):
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT id, nome, parent_id FROM atividades WHERE id = ?",
                (atividade_id,)
            ).fetchone()
            return Atividade(*row) if row else None

    def get_children(self, parent_id: int):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT id, nome, parent_id FROM atividades WHERE parent_id = ?",
                (parent_id,)
            ).fetchall()
            return [Atividade(*row) for row in rows]

    def list_all(self):
        with self._get_connection() as conn:
            rows = conn.execute("SELECT id, nome, parent_id FROM atividades").fetchall()
            return [Atividade(*row) for row in rows]

    def obter_atividades_principais(self):
        with self._get_connection() as conn:
            rows = conn.execute("SELECT id, nome, parent_id FROM atividades WHERE parent_id is NULL").fetchall()
            return [Atividade(*row) for row in rows]
    
    
    def obter_atividades_com_profundidade(self, atividade: Atividade, profundidade = 0):
        profundidade += 1
        
        filhos = self.get_children(atividade.id)
        
        if len(filhos) == 0:
            atividade.profundidade = profundidade
            return {"atividade": atividade, "filhos": []}
        
        atividades_netas = []
        for f in filhos:
            neta = self.obter_atividades_com_profundidade(f, profundidade)

            atividades_netas.append(
                neta
            )
        
        atividade.profundidade = profundidade
        return {"atividade": atividade, "filhos": atividades_netas}
    
    
    def deletar(self, atividade_id: int):
        """
        Deleta uma atividade e todas as suas filhas (deleção em cascata).
        Pergunta confirmação ao usuário antes de excluir.
        """
        # Obter atividade
        atividade = self.obter(atividade_id)
        if not atividade:
            print(f"Atividade com ID {atividade_id} não encontrada.")
            return

        # Confirmação
        confirmacao = input(f"Tem certeza que deseja excluir a atividade '{atividade.nome}' "
                            f"e todas as suas filhas? (s/N): ").strip().lower()

        if confirmacao != 's':
            print("Exclusão cancelada.")
            return

        # Função recursiva para obter todos os IDs de filhos
        def coletar_filhos_ids(atividade_id):
            filhos = self.get_children(atividade_id)
            ids = [atividade_id]
            for filho in filhos:
                ids.extend(coletar_filhos_ids(filho.id))
            return ids

        # Coletar IDs da atividade e suas filhas
        ids_para_deletar = coletar_filhos_ids(atividade_id)

        # Deletar do banco
        with self._get_connection() as conn:
            conn.executemany("DELETE FROM atividades WHERE id = ?", [(i,) for i in ids_para_deletar])

        print(f"Atividade '{atividade.nome}' e todas as filhas foram excluídas.")
