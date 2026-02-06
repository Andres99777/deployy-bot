import json
import threading
import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ChatJoinRequestHandler,
    filters
)

# =======================
# CONFIG
# =======================

TOKEN = "8278289735:AAFWAJRrwNXTcZF-5l3Q4sqkMDhpw-MO2rg"
ADMIN_URL = "https://t.me/KykePicks"
IMAGEN = "fotodekyke.png"
ARCHIVO = "users.json"

RECORDATORIO_1 = 3600      # 1 hora
RECORDATORIO_2 = 86400    # 24 horas

# =======================
# FLASK (KEEP ALIVE)
# =======================

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot KykePicks activo 🔥"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

# =======================
# UTILIDADES
# =======================

def cargar_datos():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except:
        return {"joined": [], "contacted": []}

def guardar_datos(data):
    with open(ARCHIVO, "w") as f:
        json.dump(data, f, indent=4)

# =======================
# RECORDATORIOS
# =======================

async def recordatorio_1(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data
    data = cargar_datos()

    if user_id in data["contacted"]:
        return

    await context.bot.send_message(
        chat_id=user_id,
        text="👋 ¿Sigues ahí?\nSi quieres info personalizada, escríbenos 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Hablar con Kyke", url=ADMIN_URL)]
        ])
    )

async def recordatorio_2(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data
    data = cargar_datos()

    if user_id in data["contacted"]:
        return

    await context.bot.send_message(
        chat_id=user_id,
        text="⏰ Último recordatorio\nEstamos disponibles para ayudarte 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Contactar soporte", url=ADMIN_URL)]
        ])
    )

# =======================
# APPROVE + BIENVENIDA
# =======================

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_request = update.chat_join_request
    user_id = join_request.from_user.id

    await join_request.approve()

    data = cargar_datos()
    if user_id not in data["joined"]:
        data["joined"].append(user_id)
        guardar_datos(data)

        context.job_queue.run_once(recordatorio_1, when=RECORDATORIO_1, data=user_id)
        context.job_queue.run_once(recordatorio_2, when=RECORDATORIO_2, data=user_id)

    with open(IMAGEN, "rb") as photo:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=(
                "🎉 *Bienvenido a KykePicks*\n\n"
                "📊 Pronósticos diarios\n"
                "🔥 Contenido exclusivo\n\n"
                "¿Dudas? Escríbeme 👇"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Contactar a Kyke", url=ADMIN_URL)]
            ])
        )

# =======================
# DETECTAR MENSAJE
# =======================

async def detectar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = cargar_datos()

    if user_id not in data["contacted"]:
        data["contacted"].append(user_id)
        guardar_datos(data)

# =======================
# MAIN
# =======================

keep_alive()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(ChatJoinRequestHandler(approve))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, detectar_mensaje))

app.run_polling()







