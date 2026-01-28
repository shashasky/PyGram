# framework/Bot/sessions/UserMessageRecorder.py
from framework.Session import session_manager


def record_user_message_from_update(update):
    """从 Telegram Update 对象记录用户消息"""
    if not update.message or not update.message.from_user:
        return

    user_id = update.message.from_user.id
    message_data = {
        "user_id": user_id,
        "chat_id": update.effective_chat.id,
        "text": update.message.text.strip() if update.message.text else "",
        "first_name": update.message.from_user.first_name,
        "last_name": getattr(update.message.from_user, 'last_name', None),
        "username": update.message.from_user.username,
        "language_code": getattr(update.message.from_user, 'language_code', None),
        "is_premium": getattr(update.message.from_user, 'is_premium', False),
        "message_id": update.message.message_id,
        "date": update.message.date.isoformat() if update.message.date else None
    }
    session_manager.record_user_message(user_id, message_data)