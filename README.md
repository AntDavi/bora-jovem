# Bora Jovem

Bot de Telegram que conecta jovens periféricos a trilhas de economia criativa e a oportunidades de renda no próprio bairro, com um painel (dashboard) para acompanhar a plataforma.

## Rodando

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
TELEGRAM_TOKEN=<token do @BotFather> .venv/bin/python bot.py
```

O bot guarda tudo em `jovens.db` (SQLite). **Nunca coloque o token no código ou no repositório.**

## Dashboard

```bash
DB_PATH=jovens.db .venv/bin/python dashboard.py        # http://localhost:8765 (completo, só local)
.venv/bin/python seed_demo.py && DB_PATH=demo.db PUBLIC=1 .venv/bin/python dashboard.py   # modo público com dados fictícios
```

`PUBLIC=1` mostra só números agregados: sem lista de alunos e sem exportação de CSV. Variáveis: `DB_PATH`, `PORT`, `HOST`, `PUBLIC`.

## Estrutura

- `bot.py` — fluxo do Telegram (anamnese, trilhas, progresso, vagas)
- `content.py` — trilhas, pré-requisitos, vagas e perguntas da anamnese
- `db.py` — banco SQLite e registro de eventos
- `dashboard.py` / `dashboard.html` — painel
- `seed_demo.py` — gera dados fictícios para demonstração

## Dashboard público (demo)

O `render.yaml` publica o painel no Render com **dados fictícios** gerados por `seed_demo.py` a cada start. Nunca aponte o painel público para o `jovens.db` real: ele não tem login.
