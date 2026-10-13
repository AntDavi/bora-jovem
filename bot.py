import logging
import os
import unicodedata

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters,
)

import db
from content import GOSTOS, OBJETIVOS, OPORTUNIDADES, SITUACOES, TRILHAS

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)  # evita logar o token nas URLs

MENU = ReplyKeyboardMarkup([["📚 Trilhas", "📈 Meu progresso"], ["💼 Oportunidades"]], resize_keyboard=True)


async def tira_botoes(q):
    try:
        await q.edit_message_reply_markup(None)
    except BadRequest:
        pass  # botões já removidos (clique repetido)


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def barra(feitas, total):
    return "🟩" * feitas + "⬜" * (total - feitas) + f" {feitas}/{total}"


def concluida(uid, k):
    return db.licoes(uid, k) >= len(TRILHAS[k]["licoes"])


def faltam(uid, k):
    return [r for r in TRILHAS[k]["requisitos"] if not concluida(uid, r)]


def status(uid, k):
    if faltam(uid, k):
        return "🔒"
    if concluida(uid, k):
        return "✅"
    return "▶️" if db.licoes(uid, k) else "🆕"


def teclado_trilhas(uid):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"{status(uid, k)} {t['nome']}", callback_data=f"ver:{k}")] for k, t in TRILHAS.items()]
    )


def kb_opcoes(prefixo, opcoes):
    return InlineKeyboardMarkup([[InlineKeyboardButton(r, callback_data=f"{prefixo}:{k}")] for k, r in opcoes.items()])


def kb_gostos(sel):
    linhas = [[InlineKeyboardButton(("✅ " if k in sel else "") + r, callback_data=f"g:{k}")] for k, (r, _) in GOSTOS.items()]
    linhas.append([InlineKeyboardButton("🤷 Ainda não sei", callback_data="g:nenhum")])
    linhas.append([InlineKeyboardButton("➡️ Pronto", callback_data="g:ok")])
    return InlineKeyboardMarkup(linhas)


async def proxima_etapa(msg, uid, ctx):
    """Faz a próxima pergunta da anamnese. Retorna True se a anamnese já está completa."""
    j = db.get(uid)
    if not j["bairro"]:
        ctx.user_data["etapa"] = "bairro"
        await msg.reply_text("Pra começar, me conta: em qual bairro você mora?")
    elif not j["situacao"]:
        await msg.reply_text("Valeu! Agora, qual é a sua situação hoje?\n(Sem julgamento, é só pra eu te ajudar melhor 🙂)", reply_markup=kb_opcoes("sit", SITUACOES))
    elif not j["objetivo"]:
        await msg.reply_text("E qual é o seu principal objetivo?", reply_markup=kb_opcoes("obj", OBJETIVOS))
    elif not j["gostos"]:
        ctx.user_data["gostos"] = set()
        await msg.reply_text("O que você gosta de fazer? Pode marcar mais de uma e tocar em *Pronto*.", reply_markup=kb_gostos(set()), parse_mode="Markdown")
    else:
        return True
    return False


def recomendar(uid, gostos):
    """Primeira trilha ligada aos gostos; se faltar pré-requisito, recomenda o pré-requisito."""
    for g in gostos:
        k = GOSTOS[g][1]
        return (faltam(uid, k) or [k])[0]
    return "foto"  # trilha de entrada, sem pré-requisito


async def finalizar_anamnese(msg, uid):
    j = db.get(uid)
    db.log_event(uid, "anamnese_completa", detalhe=j["situacao"])
    gostos = [g for g in (j["gostos"] or "").split(",") if g in GOSTOS]
    k = recomendar(uid, gostos)
    t = TRILHAS[k]
    abre = "Que bom que você chegou até aqui, a gente tem muita coisa pra te oferecer. " if j["situacao"] == "nemnem" else ""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"▶️ Ver {t['nome']}", callback_data=f"ver:{k}")],
        [InlineKeyboardButton("📚 Ver todas as trilhas", callback_data="todas:x")],
    ])
    await msg.reply_text(f"Pronto! 🎉 {abre}Pelo que você me contou, recomendo começar por *{t['nome']}*.\n\n{t['perspectiva']}", reply_markup=kb, parse_mode="Markdown")


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not db.get(u.id):
        db.log_event(u.id, "start")
    db.upsert(u.id, nome=u.first_name)
    await update.message.reply_text(
        f"Fala, {u.first_name}! 👋 Bora Jovem! Aqui você aprende uma habilidade criativa e encontra trampo perto de casa.\n\n"
        "Antes de escolher uma trilha, quero te conhecer um pouco.",
        reply_markup=MENU,
    )
    if await proxima_etapa(update.message, u.id, ctx):
        await mostrar_trilhas(update, ctx)


async def mostrar_trilhas(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not db.get(update.effective_user.id) or not await proxima_etapa(update.message, update.effective_user.id, ctx):
        if not db.get(update.effective_user.id):
            await update.message.reply_text("Mande /start pra gente se conhecer primeiro 🙂")
        return
    await update.message.reply_text(
        "Escolha uma trilha:\n🆕 nova · ▶️ em andamento · ✅ concluída · 🔒 precisa de outra antes",
        reply_markup=teclado_trilhas(update.effective_user.id),
    )


async def detalhe(msg, uid, k):
    t = TRILHAS[k]
    n = db.licoes(uid, k)
    txt = f"{t['nome']}\n\n📖 {t['descricao']}\n\n🎯 Onde isso pode te levar: {t['perspectiva']}\n\n{barra(n, len(t['licoes']))}"
    f = faltam(uid, k)
    if f:
        nomes = ", ".join(TRILHAS[r]["nome"] for r in f)
        await msg.reply_text(txt + f"\n\n🔒 Para entrar, conclua antes: {nomes}")
        return
    if concluida(uid, k):
        await msg.reply_text(txt + "\n\n✅ Trilha concluída! Veja /oportunidades")
        return
    rotulo = "Continuar" if n else "Começar"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"▶️ {rotulo}", callback_data=f"ir:{k}")]])
    await msg.reply_text(txt, reply_markup=kb)


async def enviar_licao(msg, uid, k):
    t = TRILHAS[k]
    n = db.licoes(uid, k)
    if n >= len(t["licoes"]):
        novas = [x for x, tt in TRILHAS.items() if k in tt["requisitos"] and not faltam(uid, x)]
        extra = ""
        if novas:
            extra = "\n\n🔓 Liberou: " + ", ".join(TRILHAS[x]["nome"] for x in novas) + " (veja em Trilhas)"
        await msg.reply_text(f"🏆 Você concluiu {t['nome']}!\n{barra(n, n)}\n\n🎯 {t['perspectiva']}{extra}\n\nAgora veja onde aplicar: /oportunidades")
        return
    titulo, corpo = t["licoes"][n]
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Fiz o desafio", callback_data=f"feito:{k}.{n}")]])
    await msg.reply_text(
        f"{t['nome']} — Lição {n + 1}\n{barra(n, len(t['licoes']))}\n\n*{titulo}*\n{corpo}",
        reply_markup=kb, parse_mode="Markdown",
    )


async def botoes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    if q.data == "g:ok" and not ctx.user_data.get("gostos"):
        return await q.answer("Marque pelo menos um, ou toque em 'Ainda não sei'", show_alert=True)
    await q.answer()
    acao, k = q.data.split(":")
    if acao == "sit" and k in SITUACOES:
        db.upsert(uid, situacao=k)
        await tira_botoes(q)
        if await proxima_etapa(q.message, uid, ctx):
            await finalizar_anamnese(q.message, uid)
    elif acao == "obj" and k in OBJETIVOS:
        db.upsert(uid, objetivo=k)
        await tira_botoes(q)
        if await proxima_etapa(q.message, uid, ctx):
            await finalizar_anamnese(q.message, uid)
    elif acao == "g":
        sel = ctx.user_data.setdefault("gostos", set())
        if k in GOSTOS:
            sel.symmetric_difference_update({k})
            await q.edit_message_reply_markup(kb_gostos(sel))
        elif k in ("ok", "nenhum"):
            db.upsert(uid, gostos="nenhum" if k == "nenhum" else ",".join(g for g in GOSTOS if g in sel))
            await tira_botoes(q)
            await finalizar_anamnese(q.message, uid)
    elif acao == "todas":
        await q.message.reply_text("Escolha uma trilha:\n🆕 nova · ▶️ em andamento · ✅ concluída · 🔒 precisa de outra antes", reply_markup=teclado_trilhas(uid))
    elif acao == "ver":
        await detalhe(q.message, uid, k)
    elif acao == "ir":
        if faltam(uid, k):
            db.log_event(uid, "bloqueado", k)
            return await detalhe(q.message, uid, k)
        if db.licoes(uid, k) == 0:
            db.log_event(uid, "trilha_inicio", k)
        db.upsert(uid, trilha=k)
        await enviar_licao(q.message, uid, k)
    elif acao == "feito":
        k, _, esperado = k.partition(".")
        if k not in TRILHAS or faltam(uid, k):
            return
        n = db.licoes(uid, k)
        if esperado and int(esperado) != n:
            return await tira_botoes(q)  # botão de lição já concluída (clique repetido)
        if n < len(TRILHAS[k]["licoes"]):
            db.set_licoes(uid, k, n + 1)
            db.log_event(uid, "licao", k, str(n + 1))
            if n + 1 == len(TRILHAS[k]["licoes"]):
                db.log_event(uid, "trilha_concluida", k)
        await tira_botoes(q)
        await q.message.reply_text("Mandou bem! 🔥")
        await enviar_licao(q.message, uid, k)


async def progresso(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    linhas = ["📈 Seu progresso:\n"]
    for k, t in TRILHAS.items():
        n = db.licoes(uid, k)
        if faltam(uid, k):
            linhas.append(f"🔒 {t['nome']} — precisa de {', '.join(TRILHAS[r]['nome'] for r in faltam(uid, k))}")
        else:
            linhas.append(f"{t['nome']}\n{barra(n, len(t['licoes']))}")
    await update.message.reply_text("\n".join(linhas))


async def oportunidades(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    j = db.get(uid)
    if not j or not j["bairro"]:
        await update.message.reply_text("Me diz seu bairro primeiro com /start")
        return
    db.log_event(uid, "vagas", detalhe=j["bairro"])
    bairro = norm(j["bairro"])
    perto = [o for o in OPORTUNIDADES if norm(o["bairro"]) == bairro]
    remoto = [o for o in OPORTUNIDADES if o["bairro"] == "*"]
    # prioriza vagas de trilhas que ele já iniciou
    chave = lambda o: db.licoes(uid, o["trilha"]) == 0
    linhas = []
    if not perto:
        linhas.append(f"Ainda não temos vagas em {j['bairro']}, mas estamos chegando. Por enquanto:")
    for titulo, lista in (("📍 No seu bairro", sorted(perto, key=chave)), ("🌐 Remoto", sorted(remoto, key=chave))):
        if lista:
            linhas.append(f"\n*{titulo}*")
            for o in lista:
                linhas.append(f"• {o['titulo']} — {o['pagamento']}\n  Contato: {o['contato']}")
    await update.message.reply_text("\n".join(linhas), parse_mode="Markdown")


async def texto(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    j = db.get(uid)
    if not j:
        return await update.message.reply_text("Mande /start pra gente se conhecer primeiro 🙂")
    if not j["bairro"]:
        db.upsert(uid, bairro=update.message.text.strip()[:60])
        ctx.user_data["etapa"] = None
        if await proxima_etapa(update.message, uid, ctx):
            await finalizar_anamnese(update.message, uid)
        return
    t = norm(update.message.text)
    if "progress" in t:
        # progresso de uma trilha específica, se citada
        for k, tr in TRILHAS.items():
            if k in t or norm(tr["nome"].split(" ", 1)[1]) in t:
                n = db.licoes(update.effective_user.id, k)
                return await update.message.reply_text(f"{tr['nome']}\n{barra(n, len(tr['licoes']))}")
        return await progresso(update, ctx)
    if any(w in t for w in ("trilha", "curso", "aprender")):
        return await mostrar_trilhas(update, ctx)
    if any(w in t for w in ("vaga", "oportunidade", "trampo", "emprego", "trabalho", "freela")):
        return await oportunidades(update, ctx)
    await update.message.reply_text("Posso te mostrar as 📚 trilhas, seu 📈 progresso ou 💼 oportunidades. É só escolher no menu!", reply_markup=MENU)


def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise SystemExit("Defina TELEGRAM_TOKEN (crie um bot com @BotFather).")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["trilha", "trilhas"], mostrar_trilhas))
    app.add_handler(CommandHandler("progresso", progresso))
    app.add_handler(CommandHandler("oportunidades", oportunidades))
    app.add_handler(CallbackQueryHandler(botoes))
    app.add_handler(MessageHandler(filters.Regex("^📚"), mostrar_trilhas))
    app.add_handler(MessageHandler(filters.Regex("^📈"), progresso))
    app.add_handler(MessageHandler(filters.Regex("^💼"), oportunidades))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    async def erro(update, context):
        logging.error("Erro ao tratar update", exc_info=context.error)

    app.add_error_handler(erro)
    app.run_polling()


if __name__ == "__main__":
    main()
