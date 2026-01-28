import re
import importlib
from telegram.ext import MessageHandler, filters, CallbackQueryHandler
from framework.Bot.sessions import record_user_message_from_update
def _resolve_controller(target):
    if isinstance(target, type):
        return target
    if isinstance(target, str):
        module_name = target
        class_name = target.split('.')[-1]
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    raise ValueError(f"无效的控制器: {target}")
async def _handle_message(update, context):
    from framework.Bot.routing.Router import get_command_routes, get_fallback_route
    from framework.Bot.bot_instance.BotManager import get_bot_instance
    bot = get_bot_instance()
    text = update.message.text.strip() if update.message and update.message.text else ""
    record_user_message_from_update(update)
    if text.startswith("/"):
        match = re.match(r"^/(\w+)", text)
        if match:
            cmd = match.group(1).lower()
            routes = get_command_routes()
            if cmd in routes:
                ctrl_class = _resolve_controller(routes[cmd])
                controller = ctrl_class(bot=bot)
                await controller.handle(update, context)
                return
    fallback_ctrl = get_fallback_route()
    if fallback_ctrl:
        ctrl_class = _resolve_controller(fallback_ctrl)
        controller = ctrl_class(bot=bot)
        await controller.handle(update, context)
async def _handle_callback(update, context):
    from framework.Bot.bot_instance.BotManager import get_bot_instance
    bot = get_bot_instance()
    callback_data = update.callback_query.data
    if not callback_data or '@' not in callback_data:
        await context.bot.answer_callback_query(update.callback_query.id)
        return
    class_name, method_name = callback_data.split('@', 1)
    if not class_name.strip() or not method_name.strip():
        await context.bot.answer_callback_query(update.callback_query.id)
        return
    target = f"app.Bot.Controllers.{class_name}"
    try:
        module = importlib.import_module(target)
        cls = getattr(module, class_name)
        instance = cls(bot=bot)
        method = getattr(instance, method_name, None)
        if callable(method):
            await method(update, context)
        await context.bot.answer_callback_query(update.callback_query.id)
    except Exception:
        await context.bot.answer_callback_query(update.callback_query.id)
def setup_handlers(app):
    app.add_handler(MessageHandler(filters.TEXT, _handle_message))
    app.add_handler(CallbackQueryHandler(_handle_callback))