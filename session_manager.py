import time
from telegram.ext import ContextTypes
from gemini_session import GeminiSession
from config import SESSION_TTL


class SessionManager:
  def __init__(self):
    self.sessions = {}  # chat_id -> session

  async def get_session(self, chat_id: int) -> GeminiSession:
    now = time.time()

    session = self.sessions.get(chat_id)

    if session:
      if now - session.last_used < SESSION_TTL:
        session.last_used = now
        return session
      else:
        await session.delete()

    # Create new session
    session = GeminiSession()
    session.last_used = now
    self.sessions[chat_id] = session
    return session

  async def cleanup(self, context: ContextTypes.DEFAULT_TYPE = None):
    now = time.time()
    expired = []

    for chat_id, session in self.sessions.items():
      if now - session.last_used > SESSION_TTL:
        expired.append(chat_id)

    for chat_id in expired:
      await self.sessions[chat_id].delete()
      del self.sessions[chat_id]
