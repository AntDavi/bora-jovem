"""Gera a versão estática do dashboard (dados fictícios) em docs/ para o GitHub Pages.
Uso: python build_pages.py"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

os.environ["DB_PATH"] = "demo.db"
subprocess.run([sys.executable, "seed_demo.py"], check=True)

import dashboard  # noqa: E402  (lê DB_PATH ao importar)

docs = Path("docs")
shutil.rmtree(docs, ignore_errors=True)
(docs / "export").mkdir(parents=True)
shutil.copy("dashboard.html", docs / "index.html")
(docs / "data.json").write_text(json.dumps(dashboard.stats(), ensure_ascii=False))
for nome in dashboard.EXPORTS:
    (docs / "export" / f"{nome}.csv").write_bytes(dashboard.export_csv(nome))
(docs / ".nojekyll").touch()
print("docs/ gerado com dados fictícios.")
