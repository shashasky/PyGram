from framework.Bot.bot_instance.BotManager import get_bot_instance
from framework.Database import DB
from framework.Session import session_manager
class BaseController:
    def __init__(self, bot=None):
        self.bot = bot or get_bot_instance()
        self.DB = DB
        self.session_manager = session_manager
    def get_user_context(self, user_id: int) -> list:
        return self.session_manager.get_latest_user_context(user_id)
    async def handle(self, update, context):
        raise NotImplementedError("子类必须实现 handle 方法")