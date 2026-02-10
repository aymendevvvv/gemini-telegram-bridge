import time

class ChatSession:
    def __init__(self, ttl_seconds: int = 600):
        self.created_at = time.time()
        self.last_activity = time.time()
        self.ttl = ttl_seconds
        self.history: list[tuple[str, str]] = []  # (role, text)

    def is_expired(self) -> bool:
        return time.time() - self.last_activity > self.ttl

    def touch(self):
        self.last_activity = time.time()

    def add_user(self, text: str):
        self.history.append(("user", text))
        self.touch()

    def add_assistant(self, text: str):
        self.history.append(("assistant", text))
        self.touch()

    def build_prompt(self) -> str:
        parts = []
        for role, text in self.history:
            parts.append(f"{role.capitalize()}: {text}")
        return "\n".join(parts)
