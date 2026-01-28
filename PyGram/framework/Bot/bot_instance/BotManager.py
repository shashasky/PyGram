_BOT_INSTANCE = None
def set_bot_instance(bot):
    global _BOT_INSTANCE
    _BOT_INSTANCE = bot
def get_bot_instance():
    return _BOT_INSTANCE