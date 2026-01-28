# framework/Session/SessionManager.py
import json
import os
from pathlib import Path
from datetime import datetime
class SessionManager:
    def __init__(self):
        self.base_session_dir = Path("storage/framework/sessions")
        self.base_session_dir.mkdir(parents=True, exist_ok=True)
        self.max_messages_per_file = 50  # 每个文件最多50条消息
    def _get_user_session_dir(self, user_id: int) -> Path:
        user_dir = self.base_session_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    def _get_current_session_file(self, user_id: int) -> Path:
        user_dir = self._get_user_session_dir(user_id)
        session_files = list(user_dir.glob("session_*.json"))
        if not session_files:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return user_dir / f"session_{timestamp}.json"
        latest_file = max(session_files, key=os.path.getctime)
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if len(data) >= self.max_messages_per_file:
                    # 创建新文件
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    return user_dir / f"session_{timestamp}.json"
        except (json.JSONDecodeError, OSError):
            pass
        return latest_file
    def _load_session_file(self, file_path: Path) -> list:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []
    def _save_session_file(self, file_path: Path, session_data: list):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    def record_user_message(self, user_id: int, message: dict):
        current_file = self._get_current_session_file(user_id)
        session_data = self._load_session_file(current_file)
        record = {
            "timestamp": datetime.now().isoformat(),
            "type": "user_message",
            "data": message
        }
        session_data.append(record)
        self._save_session_file(current_file, session_data)
    def record_bot_response(self, user_id: int, response: dict):
        current_file = self._get_current_session_file(user_id)
        session_data = self._load_session_file(current_file)
        record = {
            "timestamp": datetime.now().isoformat(),
            "type": "bot_response",
            "data": response
        }
        session_data.append(record)
        self._save_session_file(current_file, session_data)
    def get_latest_user_context(self, user_id: int) -> list:
        user_dir = self._get_user_session_dir(user_id)
        if not user_dir.exists():
            return []
        session_files = sorted(user_dir.glob("session_*.json"), key=os.path.getctime)
        if not session_files:
            return []
        latest_file = session_files[-1]
        return self._load_session_file(latest_file)
    def get_all_sessions(self, user_id: int) -> list:
        user_dir = self._get_user_session_dir(user_id)
        session_files = sorted(user_dir.glob("session_*.json"), key=os.path.getctime)
        all_records = []
        for file_path in session_files:
            records = self._load_session_file(file_path)
            all_records.extend(records)
        return all_records
    def clear_user_sessions(self, user_id: int):
        user_dir = self._get_user_session_dir(user_id)
        if user_dir.exists():
            import shutil
            shutil.rmtree(user_dir)