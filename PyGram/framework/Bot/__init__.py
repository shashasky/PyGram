# framework/Bot/__init__.py
from .routing.Router import route, fallback
from .bot_instance.BotKernel import start_polling, start_webhook
from .bot_instance.BotManager import get_bot_instance, set_bot_instance
from .controllers.BaseController import BaseController
from .WrappedBot import WrappedBot

__all__ = [
    'route',
    'fallback',
    'start_polling',
    'start_webhook',
    'get_bot_instance',
    'set_bot_instance',
    'BaseController',  # ✅
    'WrappedBot'       # ✅
]