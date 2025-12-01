from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Application, CallbackQueryHandler, MessageHandler, filters
import logging
import asyncio
from core.i18n import detect_lang, get_help_text
from core.config import telegram_config
from core.config_manager import get_config_manager

tel_bots = {}
pending_edits = {}
commands = [
    BotCommand(command="help", description="Show help message"),
]


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await help(update, context)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = detect_lang(update.message.chat_id, getattr(update.message.from_user, "language_code", None))
    help_text = get_help_text(lang, update.message.from_user.first_name)
    await update.message.reply_text(help_text, disable_web_page_preview=True)

def is_admin(user_id: int) -> bool:
    """
    判断用户是否为管理员
    """
    admin_str = telegram_config.get("admin_ids", "") or ""
    try:
        admin_ids = [int(x) for x in admin_str.split(",") if x.strip()]
    except Exception:
        admin_ids = []
    return user_id in admin_ids

async def config_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    管理员命令：展示可编辑的配置键盘
    """
    user = update.message.from_user
    if not is_admin(user.id):
        await update.message.reply_text("Permission denied")
        return
    mgr = get_config_manager()
    data = mgr.all()
    buttons = []
    for k, v in data.items():
        buttons.append([InlineKeyboardButton(text=f"{k}: {v}", callback_data=f"edit:{k}")])
    markup = InlineKeyboardMarkup(buttons or [[InlineKeyboardButton(text="No config", callback_data="noop")]])
    await update.message.reply_text("Config", reply_markup=markup)

async def edit_config_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    处理配置键编辑回调
    """
    query = update.callback_query
    if not query:
        return
    user = query.from_user
    if not is_admin(user.id):
        await query.answer()
        return
    data = query.data or ""
    if not data.startswith("edit:"):
        await query.answer()
        return
    key = data.split(":", 1)[1]
    pending_edits[user.id] = key
    await query.answer()
    await query.message.reply_text(f"Enter new value for {key}:")

async def apply_config_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    应用管理员输入的新配置值
    """
    user = update.message.from_user
    key = pending_edits.get(user.id)
    if not key:
        return
    text = (update.message.text or "").strip()
    value: object
    try:
        value = int(text)
    except Exception:
        try:
            value = float(text)
        except Exception:
            value = text
    mgr = get_config_manager()
    mgr.set(key, value)
    del pending_edits[user.id]
    await update.message.reply_text(f"Updated {key} = {value}")

async def run(token):
    global tel_bots
    application = (
        ApplicationBuilder()
        .token(token)
        .concurrent_updates(True)
        .post_init(post_init)
        .build()
    )

    # 用token作为key存储bot实例
    tel_bots[token] = application.bot

    # 基础命令
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("config", config_command))
    application.add_handler(CallbackQueryHandler(edit_config_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, apply_config_value))


    await application.initialize()
    await application.start()
    logging.info("Telegram bot startup successful")
    await application.updater.start_polling(drop_pending_updates=True)


async def init_task():
    logging.info("Initializing Telegram bot")


async def start_task(token):
    return await run(token)


def close_all():
    logging.info("Closing Telegram bot")


async def scheduled_task(token):
    """定时任务"""
    await asyncio.sleep(5)

    bot = tel_bots.get(token)
    if not bot:
        logging.error(f"未找到token对应的bot实例: {token}")
        return

    while True:
        try:
            logging.info("定时任务运行中")
            await asyncio.sleep(3600)
        except Exception as e:
            logging.error(f"定时任务执行失败: {str(e)}", exc_info=True)
            await asyncio.sleep(60)
