import asyncio
import time
from config import MAX_HISTORY_MESSAGES

class GeminiPromptSession:
  def __init__(self):
    self.last_used = time.time()
    self.history = []

  def _build_prompt(self, user_text: str) -> str:
    """
    Build a conversation-style prompt from history
    """
    lines = []
    html_prompt = f"""
      Task: {user_text}
      Format: Use ONLY Telegram HTML.
      - Allowed tags: <b>, <i>, <u>, <s>, <a>, <code></code>
      - For lists: Use the '•' bullet point and manual newlines.
      # - NO Markdown (no **, no __, no #).
      - emojies are allowed.
    """
    for msg in self.history:
      role = "User" if msg["role"] == "user" else "Assistant"
      lines.append(f"{role}: {msg['content']}")

    lines.append(f"User: {html_prompt}")
    lines.append("Assistant:")

    return "\n".join(lines)

  async def send(self, text: str) -> str:
    self.last_used = time.time()

    prompt = self._build_prompt(text)

    try:
      process = await asyncio.create_subprocess_exec(
          "gemini",
          "--yolo",
          "--prompt", prompt,
          "--output-format", "text",
          stdout=asyncio.subprocess.PIPE,
          stderr=asyncio.subprocess.DEVNULL
      )

      stdout, _ = await asyncio.wait_for(process.communicate(), timeout=180)
      reply = stdout.decode("utf-8", errors="ignore").strip()

      # Save conversation
      self.history.append({"role": "user", "content": text})
      self.history.append({"role": "assistant", "content": reply})

      if len(self.history) > MAX_HISTORY_MESSAGES:
        self.history = self.history[-MAX_HISTORY_MESSAGES:]

      return reply

    except asyncio.TimeoutError:
      process.kill()
      await process.wait()
      return "Error: Gemini timeout"
    except Exception as e:
      return f"Error: {e}"
