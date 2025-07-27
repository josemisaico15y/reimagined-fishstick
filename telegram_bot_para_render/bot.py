import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Obtener el token desde la variable de entorno
TOKEN = os.getenv("BOT_TOKEN")

# Función para leer cuentas desde el archivo
def cargar_cuentas():
    cuentas = []
    try:
        with open("cuentas.txt", "r", encoding="utf-8") as f:
            for linea in f:
                if ":" in linea:
                    correo, password = linea.strip().split(":", 1)
                    cuentas.append({"correo": correo, "password": password})
    except FileNotFoundError:
        print("El archivo cuentas.txt no se encontró.")
    return cuentas

# Guardar la lista de cuentas en el archivo
def guardar_cuentas(cuentas):
    with open("cuentas.txt", "w", encoding="utf-8") as f:
        for c in cuentas:
            f.write(f"{c['correo']}:{c['password']}\n")

cuentas = cargar_cuentas()

# Funciones de acciones
async def cuenta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if cuentas:
        cuenta_info = cuentas.pop(0)
        respuesta = f"📧 **Correo:** {cuenta_info['correo']}\n🔑 **Contraseña:** {cuenta_info['password']}"
        guardar_cuentas(cuentas)
    else:
        respuesta = "⚠️ No hay más cuentas disponibles."
    await update.message.reply_text(respuesta, parse_mode="Markdown")

async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if cuentas:
        lista = "\n".join([f"{i+1}. {c['correo']}" for i, c in enumerate(cuentas)])
        respuesta = f"📋 **Cuentas disponibles:**\n{lista}"
    else:
        respuesta = "⚠️ No hay cuentas disponibles."
    await update.message.reply_text(respuesta, parse_mode="Markdown")

async def agregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        nueva_cuenta = " ".join(context.args)
        if ":" in nueva_cuenta:
            correo, password = nueva_cuenta.split(":", 1)
            cuentas.append({"correo": correo.strip(), "password": password.strip()})
            guardar_cuentas(cuentas)
            respuesta = f"✅ Cuenta agregada: {correo.strip()}"
        else:
            respuesta = "⚠️ Formato incorrecto. Usa: /agregar correo:contraseña"
    else:
        respuesta = "⚠️ Debes escribir una cuenta. Ejemplo: /agregar user@example.com:pass123"
    await update.message.reply_text(respuesta)

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛒 Para comprar cuentas, contacta con soporte o visita nuestra página de pagos.")

async def entregar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📦 Tu pedido está siendo procesado. Usa /cuenta para obtener una cuenta disponible.")

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "ℹ️ **Lista de comandos disponibles:**\n"
        "/cuenta - Entregar una cuenta\n"
        "/listar - Ver cuentas disponibles\n"
        "/agregar - Agregar una nueva cuenta (correo:contraseña)\n"
        "/comprar - Información para comprar cuentas\n"
        "/entregar - Mensaje de entrega\n"
        "/ayuda - Muestra esta lista"
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

# Menú interactivo
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗂 Ver Cuentas", callback_data='listar')],
        [InlineKeyboardButton("🎟 Obtener Cuenta", callback_data='cuenta')],
        [InlineKeyboardButton("🛒 Comprar", callback_data='comprar')],
        [InlineKeyboardButton("📦 Entregar", callback_data='entregar')],
        [InlineKeyboardButton("ℹ️ Ayuda", callback_data='ayuda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona una opción:", reply_markup=reply_markup)

# Botones callback
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'listar':
        if cuentas:
            lista = "\n".join([f"{i+1}. {c['correo']}" for i, c in enumerate(cuentas)])
            respuesta = f"📋 **Cuentas disponibles:**\n{lista}"
        else:
            respuesta = "⚠️ No hay cuentas disponibles."
        await query.edit_message_text(respuesta, parse_mode="Markdown")

    elif data == 'cuenta':
        if cuentas:
            cuenta_info = cuentas.pop(0)
            respuesta = f"📧 **Correo:** {cuenta_info['correo']}\n🔑 **Contraseña:** {cuenta_info['password']}"
            guardar_cuentas(cuentas)
        else:
            respuesta = "⚠️ No hay más cuentas disponibles."
        await query.edit_message_text(respuesta, parse_mode="Markdown")

    elif data == 'comprar':
        await query.edit_message_text("🛒 Para comprar cuentas, contacta con soporte o visita nuestra página de pagos.")

    elif data == 'entregar':
        await query.edit_message_text("📦 Tu pedido está siendo procesado. Usa /cuenta para obtener una cuenta disponible.")

    elif data == 'ayuda':
        mensaje = (
            "ℹ️ **Lista de comandos disponibles:**\n"
            "/cuenta - Entregar una cuenta\n"
            "/listar - Ver cuentas disponibles\n"
            "/agregar - Agregar una nueva cuenta (correo:contraseña)\n"
            "/comprar - Información para comprar cuentas\n"
            "/entregar - Mensaje de entrega\n"
            "/ayuda - Muestra esta lista"
        )
        await query.edit_message_text(mensaje, parse_mode="Markdown")

# Bienvenida
async def bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "👋 **¡Bienvenido a nuestro Bot de Cuentas Premium!**\n\n"
        "Aquí podrás:\n"
        "• Ver y obtener cuentas disponibles.\n"
        "• Comprar cuentas de forma rápida y segura.\n"
        "• Recibir soporte directo con un solo clic.\n\n"
        "👇 **Elige una opción del menú de abajo para comenzar:**"
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")
    await menu(update, context)

if __name__ == "__main__":
    print("Bot en funcionamiento (Railway)...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("cuenta", cuenta))
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("agregar", agregar))
    app.add_handler(CommandHandler("comprar", comprar))
    app.add_handler(CommandHandler("entregar", entregar))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bienvenida))
    app.run_polling()
