"""Bora Jovem — Dashboard do MVP. Uso: DB_PATH=jovens.db python dashboard.py  ->  http://localhost:8765"""
import csv
import io
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from content import GOSTOS, OBJETIVOS, SITUACOES, TRILHAS

DB_PATH = os.environ.get("DB_PATH", "jovens.db")
PORT = int(os.environ.get("PORT", 8765))
HOST = os.environ.get("HOST", "127.0.0.1")
# PUBLIC=1: modo público, só números agregados (sem nomes de alunos e sem exportação)
PUBLIC = os.environ.get("PUBLIC") == "1"
HTML = (Path(__file__).parent / "dashboard.html").read_bytes()


def q(c, sql, *a):
    return [dict(r) for r in c.execute(sql, a).fetchall()]


def one(c, sql, *a):
    return c.execute(sql, a).fetchone()[0] or 0


def stats():
    c = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    total = one(c, "SELECT COUNT(*) FROM jovens")
    ativos = one(c, "SELECT COUNT(DISTINCT uid) FROM eventos WHERE ts >= datetime('now','-7 days')")
    novos = one(c, "SELECT COUNT(*) FROM eventos WHERE tipo='start' AND ts >= datetime('now','-7 days')")
    licoes = one(c, "SELECT COUNT(*) FROM eventos WHERE tipo='licao'")
    iniciaram = one(c, "SELECT COUNT(DISTINCT uid) FROM progresso WHERE licoes>0")
    concluiram = one(c, "SELECT COUNT(*) FROM eventos WHERE tipo='trilha_concluida'")
    pares = one(c, "SELECT COUNT(*) FROM progresso WHERE licoes>0")

    trilhas = []
    for k, t in TRILHAS.items():
        n = len(t["licoes"])
        funil = [one(c, "SELECT COUNT(*) FROM progresso WHERE trilha=? AND licoes>=?", k, i) for i in range(1, n + 1)]
        trilhas.append({
            "id": k, "nome": t["nome"], "requisitos": t["requisitos"], "total_licoes": n,
            "iniciaram": funil[0], "concluiram": funil[-1], "funil": funil,
            "bloqueios": one(c, "SELECT COUNT(*) FROM eventos WHERE tipo='bloqueado' AND trilha=?", k),
        })

    por_dia = {r["d"]: r for r in q(c, """
        SELECT date(ts) d, SUM(tipo='licao') licoes, SUM(tipo='start') novos
        FROM eventos WHERE ts >= date('now','-13 days') GROUP BY d""")}
    dias = [r["d"] for r in q(c, "WITH RECURSIVE x(n) AS (SELECT 0 UNION ALL SELECT n+1 FROM x WHERE n<13) "
                                 "SELECT date('now', '-'||(13-n)||' days') d FROM x")]
    atividade = [{"dia": d, "licoes": (por_dia.get(d) or {}).get("licoes", 0) or 0,
                  "novos": (por_dia.get(d) or {}).get("novos", 0) or 0} for d in dias]

    bairros = q(c, """
        SELECT COALESCE(j.bairro,'(sem bairro)') bairro, COUNT(*) alunos,
               (SELECT COUNT(*) FROM eventos e WHERE e.tipo='vagas' AND e.detalhe=j.bairro) consultas_vagas
        FROM jovens j GROUP BY j.bairro ORDER BY alunos DESC LIMIT 8""")

    alunos = q(c, """
        SELECT j.nome, j.bairro, j.trilha,
               COALESCE((SELECT SUM(licoes) FROM progresso p WHERE p.uid=j.id),0) licoes,
               (SELECT MAX(ts) FROM eventos e WHERE e.uid=j.id) ultimo
        FROM jovens j ORDER BY ultimo DESC LIMIT 10""")
    if PUBLIC:
        alunos = []
    for a in alunos:
        a["trilha_nome"] = TRILHAS[a["trilha"]]["nome"] if a["trilha"] in TRILHAS else None

    def contagem(col, rotulos):
        r = {k: one(c, f"SELECT COUNT(*) FROM jovens WHERE {col}=?", k) for k in rotulos}
        return [{"rotulo": rotulos[k], "n": n} for k, n in r.items()]

    gostos = [{"rotulo": v[0], "n": one(c, "SELECT COUNT(*) FROM jovens WHERE ',' || gostos || ',' LIKE ?", f"%,{k},%")}
              for k, v in GOSTOS.items()]
    perfil = {
        "respondeu": one(c, "SELECT COUNT(*) FROM jovens WHERE gostos IS NOT NULL"),
        "nemnem": one(c, "SELECT COUNT(*) FROM jovens WHERE situacao='nemnem'"),
        "situacoes": contagem("situacao", SITUACOES),
        "objetivos": contagem("objetivo", OBJETIVOS),
        "gostos": gostos,
    }

    return {
        "perfil": perfil,
        "publico": PUBLIC,
        "kpis": {
            "total": total, "ativos_7d": ativos, "novos_7d": novos, "licoes": licoes,
            "trilhas_concluidas": concluiram,
            "engajamento": round(100 * iniciaram / total) if total else 0,
            "conclusao": round(100 * concluiram / pares) if pares else 0,
            "licoes_por_aluno": round(licoes / total, 1) if total else 0,
            "consultas_vagas": one(c, "SELECT COUNT(*) FROM eventos WHERE tipo='vagas'"),
        },
        "trilhas": trilhas, "atividade": atividade, "bairros": bairros, "alunos": alunos,
    }


EXPORTS = {
    "alunos": ("SELECT j.id, j.nome, j.bairro, j.situacao, j.objetivo, j.gostos, j.trilha AS trilha_ativa, "
               "COALESCE((SELECT SUM(licoes) FROM progresso p WHERE p.uid=j.id),0) AS licoes_concluidas, "
               "(SELECT MIN(ts) FROM eventos e WHERE e.uid=j.id) AS primeiro_registro, "
               "(SELECT MAX(ts) FROM eventos e WHERE e.uid=j.id) AS ultima_atividade FROM jovens j ORDER BY j.id"),
    "progresso": ("SELECT j.nome, j.bairro, p.trilha, p.licoes AS licoes_concluidas FROM progresso p "
                  "JOIN jovens j ON j.id=p.uid ORDER BY j.nome, p.trilha"),
    "eventos": "SELECT ts, uid, tipo, trilha, detalhe FROM eventos ORDER BY ts",
}


def seguro(v):
    # evita injeção de fórmulas ao abrir o CSV no Excel/Sheets
    return "'" + v if isinstance(v, str) and v[:1] in ("=", "+", "-", "@") else v


def export_csv(nome):
    c = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    cur = c.execute(EXPORTS[nome])
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([d[0] for d in cur.description])
    for row in cur:
        w.writerow([seguro(v) for v in row])
    return ("\ufeff" + buf.getvalue()).encode("utf-8")  # BOM: acentos corretos no Excel


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/export/"):
            if PUBLIC:
                self.send_error(404)
                return
            nome = self.path[len("/export/"):].split("?")[0].removesuffix(".csv")
            if nome not in EXPORTS:
                self.send_error(404)
                return
            body = export_csv(nome)
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="bora-jovem-{nome}.csv"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/api/stats"):
            try:
                body, ctype = json.dumps(stats()).encode(), "application/json"
            except sqlite3.Error as e:
                body, ctype = json.dumps({"erro": str(e)}).encode(), "application/json"
        else:
            body, ctype = HTML, "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"Dashboard em http://{HOST}:{PORT} (banco: {DB_PATH}, público: {PUBLIC})")
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
