# Gerenciador de Tarefas Terminal

Aplicação terminal para gerenciar tarefas e subtarefas usando `python-simple-term-menu` e SQLite.

Principais comandos (após selecionar uma tarefa no menu):
- `p` : adicionar tarefa no nível principal
- `s` : adicionar subtarefa da tarefa selecionada
- `d` : editar / detalhar informações extras (editor dividido com preview)
- `r` : renomear tarefa
- `x` : deletar tarefa
- `q` : sair

Instalação:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Uso:

```bash
# Terminal app
python tasks.py

# Web app (in another terminal):
# start the FastAPI server and serve the web UI
# install dependencies then run:
uvicorn server:app --reload --host 127.0.0.1 --port 8000

# open the browser at http://127.0.0.1:8000/static/index.html
```

Os dados são salvos em `tasks.db` no diretório do projeto.
