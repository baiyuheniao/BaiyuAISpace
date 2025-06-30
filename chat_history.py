import os
import json
import uuid
import datetime
from typing import List, Dict, Optional

class ChatHistory:
    def __init__(self, history_file: str = 'chat_histories.json'):
        self.history_file = history_file
        self.histories: Dict[str, dict] = {}
        self._load_histories()

    def _load_histories(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.histories = json.load(f)
            except Exception:
                self.histories = {}
        else:
            self.histories = {}

    def _save_histories(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.histories, f, ensure_ascii=False, indent=2)

    def create_history(self, title: Optional[str] = None) -> str:
        history_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()
        self.histories[history_id] = {
            'id': history_id,
            'title': title or f'对话 {now[:10]}',
            'created_at': now,
            'updated_at': now,
            'messages': [],
            'is_favorite': False
        }
        self._save_histories()
        return history_id

    def get_histories(self) -> List[dict]:
        # 按更新时间倒序
        return sorted(self.histories.values(), key=lambda h: h['updated_at'], reverse=True)

    def get_favorites(self) -> List[dict]:
        return [h for h in self.histories.values() if h.get('is_favorite')]

    def get_history(self, history_id: str) -> Optional[dict]:
        return self.histories.get(history_id)

    def update_history_title(self, history_id: str, title: str) -> bool:
        if history_id in self.histories:
            self.histories[history_id]['title'] = title
            self.histories[history_id]['updated_at'] = datetime.datetime.now().isoformat()
            self._save_histories()
            return True
        return False

    def toggle_favorite(self, history_id: str) -> bool:
        if history_id in self.histories:
            self.histories[history_id]['is_favorite'] = not self.histories[history_id].get('is_favorite', False)
            self.histories[history_id]['updated_at'] = datetime.datetime.now().isoformat()
            self._save_histories()
            return True
        return False

    def delete_history(self, history_id: str) -> bool:
        if history_id in self.histories:
            del self.histories[history_id]
            self._save_histories()
            return True
        return False

    def clear_all_histories(self):
        self.histories = {}
        self._save_histories()

    def add_message(self, history_id: str, message: dict) -> bool:
        if history_id in self.histories:
            self.histories[history_id]['messages'].append(message)
            self.histories[history_id]['updated_at'] = datetime.datetime.now().isoformat()
            self._save_histories()
            return True
        return False
