
from typing import Optional

class AppState:
    def __init__(self):
        self.assistant_id: Optional[str] = None
        self.thread_id: Optional[str] = None
        self.chat_history: list = []
        self.context: str = ""

app_state = AppState()
