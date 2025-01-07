## Pré-requisitos
- Ter python e pip instalados

## Comandos
- mkdir fast-python-api
- python3 -m venv .venv
- . .venv/bin/activate
- pip install fastapi uvicorn
- touch main.py

Criar main.py
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

```
Executar com o comando
- uvicorn main:app --reload --port 5000

Comando para executar mais de um worker de forma concerrente(testar concorrência)
- uvicorn main:app --port 5000 --workers 5
