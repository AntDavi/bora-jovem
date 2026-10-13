"""Gera um banco de demonstração (demo.db) para ver o dashboard cheio. Uso: python seed_demo.py"""
import os
import random
import sqlite3
from datetime import datetime, timedelta

if os.path.exists("demo.db"):
    os.remove("demo.db")
import db  # noqa: E402  (cria o schema em jovens.db no diretório atual)

from content import TRILHAS  # noqa: E402

# cria o schema num demo.db separado, sem tocar no jovens.db real
schema_src = sqlite3.connect("jovens.db")
schema = [r[0] for r in schema_src.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
c = sqlite3.connect("demo.db")
for s in schema:
    c.execute(s)

random.seed(7)
nomes = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabi", "Hugo", "Iara", "João", "Kaique", "Lara", "Marcos", "Nina", "Otávio", "Paula", "Rafa", "Sofia", "Tiago", "Vitória"]
bairros = ["Capão Redondo", "Brasilândia", "Paraisópolis", "Heliópolis", "Cidade Tiradentes"]
agora = datetime.now()


def ts(dias):
    return (agora - timedelta(days=dias, hours=random.randint(0, 12))).strftime("%Y-%m-%d %H:%M:%S")


def ev(uid, tipo, dt, trilha=None, det=None):
    c.execute("INSERT INTO eventos (uid,tipo,trilha,detalhe,ts) VALUES (?,?,?,?,?)", (uid, tipo, trilha, det, dt))


for i, nome in enumerate(nomes, 1):
    bairro = random.choice(bairros)
    entrada = random.randint(0, 13)
    ev(i, "start", ts(entrada))
    trilha_ativa = None
    # ordem: foto/musica/design livres; audiovisual só depois de foto
    for k in random.sample(["foto", "musica", "design"], random.randint(0, 2)):
        n = len(TRILHAS[k]["licoes"])
        feitas = random.choices(range(0, n + 1), weights=[1, 4, 3, 3, 2, 3])[0]
        if feitas:
            trilha_ativa = k
            ev(i, "trilha_inicio", ts(entrada), k)
            c.execute("INSERT INTO progresso VALUES (?,?,?)", (i, k, feitas))
            for l in range(1, feitas + 1):
                ev(i, "licao", ts(max(0, entrada - l // 2)), k, str(l))
            if feitas == n:
                ev(i, "trilha_concluida", ts(max(0, entrada - 3)), k)
    done = c.execute("SELECT 1 FROM progresso WHERE uid=? AND trilha='foto' AND licoes=5", (i,)).fetchone()
    if done:
        feitas = random.randint(1, 4)
        trilha_ativa = "audiovisual"
        ev(i, "trilha_inicio", ts(1), "audiovisual")
        c.execute("INSERT INTO progresso VALUES (?,?,?)", (i, "audiovisual", feitas))
        for l in range(1, feitas + 1):
            ev(i, "licao", ts(0), "audiovisual", str(l))
    if random.random() < 0.4:
        ev(i, "bloqueado", ts(random.randint(0, entrada)), "audiovisual")
    if random.random() < 0.6:
        ev(i, "vagas", ts(random.randint(0, entrada)), det=bairro)
    sit = random.choices(["estuda", "trabalha", "ambos", "nemnem"], weights=[3, 3, 2, 4])[0]
    obj = random.choice(["renda", "emprego", "negocio", "profissao"])
    gostos = ",".join(random.sample(["video", "musica", "arte", "foto"], random.randint(1, 3)))
    c.execute("INSERT INTO jovens (id,nome,bairro,trilha,situacao,objetivo,gostos) VALUES (?,?,?,?,?,?,?)",
              (i, nome, bairro, trilha_ativa, sit, obj, gostos))

c.commit()
print("demo.db criado. Rode: DB_PATH=demo.db python dashboard.py")
