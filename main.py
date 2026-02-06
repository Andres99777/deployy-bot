import json
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
# CONFIGURACIÓN
# =======================

TOKEN = "8278289735:AAFWAJRrwNXTcZF-5l3Q4sqkMDhpw-MO2rg"
ADMIN_URL = "https://t.me/KykePicks"  # Link para que te escriban
IMAGEN = "fotodekyke.png"             # Ruta local de la foto
ARCHIVO = "users.json"

# tiempos de recordatorio en segundos
RECORDATORIO_1 = 10       # 1 hora
RECORDATORIO_2 = 30    # 24 horas

# =======================
# UTILIDADES
# =======================

def cargar_datos():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except:
        return {"started": [], "contacted": [], "joined": []}

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

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Escríbeme aquí", url=ADMIN_URL)]
    ])

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "👋 Hola\n\n"
            "Vimos que entraste al canal pero aún no nos escribes.\n"
            "Si quieres info personalizada, haz clic 👇"
        ),
        reply_markup=teclado
    )

async def recordatorio_2(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data
    data = cargar_datos()

    if user_id in data["contacted"]:
        return

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Hablar con soporte", url=ADMIN_URL)]
    ])

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "⏰ Último recordatorio\n\n"
            "Estamos disponibles para ayudarte con cualquier duda.\n"
            "Escríbenos cuando quieras 👇"
        ),
        reply_markup=teclado
    )

# =======================
# CUANDO EL USUARIO DA /START
# =======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = cargar_datos()

    if user_id not in data["started"]:
        data["started"].append(user_id)
        guardar_datos(data)

        # programar recordatorios
        context.job_queue.run_once(recordatorio_1, when=RECORDATORIO_1, data=user_id)
        context.job_queue.run_once(recordatorio_2, when=RECORDATORIO_2, data=user_id)

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Contactar administrador", url=ADMIN_URL)]
    ])

    with open(IMAGEN, "rb") as photo:
        await update.message.reply_photo(
            photo=photo,
            caption=(
                "🎉 Bienvenido a *KykePicks*\n\n"
                "✅ Pronósticos diarios 📊🔥\n"
                "✅ Soporte personalizado 👇"
            ),
            reply_markup=teclado,
            parse_mode="Markdown"
        )

# =======================
# DETECTAR SI EL USUARIO ESCRIBIÓ
# =======================

async def detectar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = cargar_datos()

    if user_id not in data["contacted"]:
        data["contacted"].append(user_id)
        guardar_datos(data)

# =======================
# APROBAR UNIONES AL GRUPO
# =======================

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_request = update.chat_join_request
    user_id = join_request.from_user.id
    data = cargar_datos()

    # aprobar al usuario
    await join_request.approve()

    # registrar que se unió
    if user_id not in data["joined"]:
        data["joined"].append(user_id)
        guardar_datos(data)

    # teclado con botón
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Contactar administrador", url=ADMIN_URL)]
    ])

    # enviar foto + mensaje privado
    with open(IMAGEN, "rb") as photo:
        await context.bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=(
                "🎉 ¡Bienvenido a *KykePicks*! 🎉\n\n"
                "Gracias por unirte al canal privado 🔒\n"
                "Aquí encontrarás pronósticos diarios y contenido exclusivo 📊🔥\n\n"
                "Si tienes dudas, contáctanos 👇"
            ),
            reply_markup=teclado,
            parse_mode="Markdown"
        )

# =======================
# EJECUCIÓN DEL BOT
# =======================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, detectar_mensaje))
app.add_handler(ChatJoinRequestHandler(approve))

app.run_polling(allowed_updates=Update.ALL_TYPES)






