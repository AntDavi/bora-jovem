import sqlite3

_conn = sqlite3.connect("jovens.db", check_same_thread=False)
_conn.row_factory = sqlite3.Row
_conn.execute("CREATE TABLE IF NOT EXISTS jovens (id INTEGER PRIMARY KEY, nome TEXT, bairro TEXT, trilha TEXT, licao INTEGER DEFAULT 0)")
# progresso por trilha: licoes concluídas
_conn.execute("CREATE TABLE IF NOT EXISTS progresso (uid INTEGER, trilha TEXT, licoes INTEGER DEFAULT 0, PRIMARY KEY (uid, trilha))")

for _col in ("situacao", "objetivo", "gostos"):
    try:
        _conn.execute(f"ALTER TABLE jovens ADD COLUMN {_col} TEXT")
    except sqlite3.OperationalError:
        pass  # coluna já existe


def get(uid):
    return _conn.execute("SELECT * FROM jovens WHERE id=?", (uid,)).fetchone()


def upsert(uid, **campos):
    if not get(uid):
        _conn.execute("INSERT INTO jovens (id) VALUES (?)", (uid,))
    for k, v in campos.items():
        _conn.execute(f"UPDATE jovens SET {k}=? WHERE id=?", (v, uid))
    _conn.commit()


def licoes(uid, trilha):
    r = _conn.execute("SELECT licoes FROM progresso WHERE uid=? AND trilha=?", (uid, trilha)).fetchone()
    return r["licoes"] if r else 0


def set_licoes(uid, trilha, n):
    _conn.execute(
        "INSERT INTO progresso (uid, trilha, licoes) VALUES (?,?,?) "
        "ON CONFLICT(uid, trilha) DO UPDATE SET licoes=excluded.licoes",
        (uid, trilha, n),
    )
    _conn.commit()


_conn.execute("CREATE TABLE IF NOT EXISTS eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, tipo TEXT, trilha TEXT, detalhe TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")


def log_event(uid, tipo, trilha=None, detalhe=None):
    _conn.execute("INSERT INTO eventos (uid, tipo, trilha, detalhe) VALUES (?,?,?,?)", (uid, tipo, trilha, detalhe))
    _conn.commit()
