# bootstrap/Foundation/Application.py
from pathlib import Path
from bootstrap.Foundation.RouteValidator import validate_routes
from framework.Error.Handler import enable_global_error_handler
from config.bot import BOT_MODE

class Application:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.resolve()
        enable_global_error_handler()
        validate_routes(self.project_root)
        print("应用初始化完成")

    def run(self):
        if BOT_MODE == "polling":
            from framework.Bot.bot_instance.BotKernel import start_polling
            start_polling()
        elif BOT_MODE == "webhook":
            from framework.Bot.bot_instance.BotKernel import start_webhook
            start_webhook()

    def handle_console(self, argv):
        from framework.Console.ConsoleKernel import handle_console
        return handle_console(argv)