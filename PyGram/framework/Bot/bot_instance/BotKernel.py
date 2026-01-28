import sys
from config.bot import BOT_TOKEN
from framework.Bot.bot_instance.BotManager import set_bot_instance
from framework.Bot.routing.Handler import setup_handlers
from framework.Bot.WrappedBot import WrappedBot
def start_polling():
    try:
        from telegram.ext import ApplicationBuilder
    except ImportError:
        print("错误：缺少依赖 'python-telegram-bot'", file=sys.stderr)
        sys.exit(1)

    if not BOT_TOKEN:
        print("错误：未设置 BOT_TOKEN", file=sys.stderr)
        sys.exit(1)
    bot_instance = WrappedBot(token=BOT_TOKEN)
    app = ApplicationBuilder().bot(bot_instance).build()
    set_bot_instance(app.bot)
    setup_handlers(app)
    print("PyGram OK run...")
    app.run_polling()
def start_webhook():
    print("Webhook 模式待实现")