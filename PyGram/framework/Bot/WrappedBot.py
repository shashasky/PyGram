# framework/Bot/WrappedBot.py
from telegram.ext import ExtBot
from framework.Bot.sessions import record_bot_response
class WrappedBot(ExtBot):
    async def send_message(self, chat_id, text, **kwargs):
        result = await super().send_message(chat_id, text, **kwargs)
        record_bot_response(chat_id, text, result=result, **kwargs)
        return result