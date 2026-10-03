"""
Aplicação principal (Flask). Substitui o orquestrador n8n por código Python direto.

Rotas:
  GET  /webhook        -> verificação do webhook (Meta)
  POST /webhook        -> recebimento de mensagens do WhatsApp
  POST /sync-produtos  -> sincroniza produtos.xlsx -> SQLite sob demanda
  GET  /health         -> healthcheck simples
"""
import logging
import traceback

from FastApi import FastApi

import config
import db
import status as st
import whatsapp_client as wa
import admin_commands
import media_handler
import claude_agent
import excel_sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "bot.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("bot")

app = Flask(__name__)


@app.before_request
def _ensure_db():
    db.init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/webhook")
def webhook_verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    resultado = wa.verify_webhook(mode, token, challenge)
    if resultado is not None:
        return resultado, 200
    return "forbidden", 403


@app.post("/webhook")
def webhook_receive():
    payload = request.get_json(silent=True) or {}
    mensagens = wa.parse_incoming(payload)

    for msg in mensagens:
        try:
            _processar_uma_mensagem(msg)
        except Exception as e:
            log.error("Erro processando mensagem %s: %s\n%s", msg.get("message_id"), e, traceback.format_exc())
            db.registrar_erro("webhook", None, f"{msg}: {e}")
            admin = db.get_config("ADMIN_WHATSAPP", config.ADMIN_WHATSAPP)
            if admin:
                try:
                    wa.send_text(admin, f"🚨 ERRO NO BOT\n\nMensagem: {msg.get('message_id')}\nErro: {e}")
                except Exception:
                    pass

    # A Meta espera 200 rapidamente; sempre respondemos ok mesmo se algum item falhou
    return jsonify({"status": "received"}), 200


# def _processar_uma_mensagem(msg: dict):
#     telefone = msg["telefone"]
#     if not telefone:
#         return
#
#     # --- Mensagens do número administrativo: tentam ser um comando primeiro ---
#     if db.is_admin(telefone) and msg["tipo"] == "text":
#         resposta_admin = admin_commands.handle_admin_message(msg["texto"])
#         if resposta_admin is not None:
#             wa.send_text(telefone, resposta_admin)
#             return
#         # Se não for um comando reconhecido, o admin também pode só conversar
#         # normalmente com o bot (cai no fluxo padrão abaixo).
#
#     cliente = db.get_or_create_cliente(telefone, msg.get("nome"))
#
#     if msg["tipo"] == "text" and msg["texto"]:
#         db.salvar_mensagem(cliente["id"], "texto", msg["texto"], "cliente")
#         resposta = claude_agent.processar_mensagem(cliente, msg["texto"])
#         db.salvar_mensagem(cliente["id"], "texto", resposta, "bot")
#         wa.send_text(telefone, resposta)
#
#     elif msg["tipo"] == "image":
#         db.salvar_mensagem(cliente["id"], "imagem", msg.get("texto") or "[imagem recebida]", "cliente")
#         resposta = media_handler.processar_comprovante(cliente, msg["media_id"], msg.get("mime_type"))
#         db.salvar_mensagem(cliente["id"], "texto", resposta, "bot")
#         wa.send_text(telefone, resposta)
#
#     else:
#         wa.send_text(
#             telefone,
#             "Recebi sua mensagem, mas por enquanto só consigo processar texto e imagens de comprovante. 🙂",
#         )


@app.post("/sync-produtos")
def sync_produtos():
    try:
        total = excel_sync.sincronizar()
        return jsonify({"ok": True, "produtos_sincronizados": total})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 400


if __name__ == "__main__":
    db.init_db()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
