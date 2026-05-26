from typing import Dict, List, Optional

class ContextManager:
    def __init__(
        self,
        max_messages: Optional[int] = None,
        max_chars: Optional[int] = None,
        system_prompt: str = '',
    ) -> None:
        self.max_messages = max_messages
        self.max_chars = max_chars
        self.system_prompt = system_prompt
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        self.history.append({'role': role, 'content': content})
        self.trim()

    def total_chars(self, messages: List[Dict[str, str]]) -> int:
        total = 0
        for m in messages:
            total += len(m['content'])
        return total

    def trim(self) -> None:
        if self.max_messages is not None and self.max_messages > 0:
            while len(self.history) > self.max_messages:
                self.history.pop(0)

        if self.max_chars is not None and self.max_chars > 0:
            while self.total_chars(self.history) > self.max_chars and self.history:
                first_len = len(self.history[0]['content'])
                if first_len > self.max_chars:
                    excess = self.total_chars(self.history) - self.max_chars
                    self.history[0]['content'] = self.history[0]['content'][excess:]
                    if not self.history[0]['content']:
                        self.history.pop(0)
                else:
                    self.history.pop(0)

    def get_messages(self) -> List[Dict[str, str]]:
        return list(self.history)

    def reset(self) -> None:
        self.history = []