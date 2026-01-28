# framework/Bot/sessions/BotResponseRecorder.py
from framework.Session import session_manager

def record_bot_response(chat_id: int, text: str, **kwargs):
    """记录机器人发送的回复"""
    # 只记录私聊消息（chat_id > 0 且等于 user_id）
    if chat_id > 0:
        user_id = chat_id
        response_data = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": kwargs.get('reply_markup'),
            "parse_mode": kwargs.get('parse_mode'),
            "disable_web_page_preview": kwargs.get('disable_web_page_preview'),
            "timestamp": None  # WrappedBot 会处理实际时间戳
        }
        try:
            session_manager.record_bot_response(user_id, response_data)
        except Exception:
            pass  # 记录失败不影响主流程