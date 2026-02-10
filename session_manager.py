import time
import asyncio
from gemini_prompt import GeminiPromptSession
from rich import print
from config import SESSION_TTL

class SessionManager:
    def __init__(self):
        self.sessions = {}  # chat_id -> session

    async def get_session(self, chat_id: int) -> GeminiPromptSession:
        now = time.time()

        session = self.sessions.get(chat_id)

        if session:
            # Check expiry
            if now - session.last_used < SESSION_TTL:
                session.last_used = now
                return session
            else:
                # await session.close() not implemented yet
                del self.sessions[chat_id]

        # Create new session
        session = GeminiPromptSession()
        session.last_used = now
        self.sessions[chat_id] = session
        return session

    async def cleanup(self):
        """Periodically remove expired sessions"""
        while True:
            print("cleanup")
            now = time.time()
            expired = []

            for chat_id, session in self.sessions.items():
                if now - session.last_used > SESSION_TTL:
                    expired.append(chat_id)

            for chat_id in expired:
                # await self.sessions[chat_id].close() not implemented yet
                del self.sessions[chat_id]

            await asyncio.sleep(60)
