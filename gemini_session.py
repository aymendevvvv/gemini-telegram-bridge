import asyncio
import time
import re


class GeminiSession:
  def __init__(self, sessionID: str = None):
    self.sessionID = sessionID
    self.model = "gemini-2.5-flash"
    self.last_used = time.time()

  def _build_prompt(self, user_text: str) -> str:

    html_prompt = f"""
      Task: {user_text}
      Format: Use ONLY Telegram HTML.
      - Allowed tags: <b>, <i>, <u>, <s>, <a>, <code></code>
      - For lists: Use the '•' bullet point and manual newlines.
      # - NO Markdown (no **, no __, no #).
      - emojies are allowed.
    """

    return html_prompt

  async def _get_session_id(self):
    list_proc = await asyncio.create_subprocess_exec(
      "gemini",
      "--list-sessions",
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.DEVNULL,
    )
    list_out, _ = await asyncio.wait_for(
      list_proc.communicate(), timeout=180
    )
    list_text = list_out.decode("utf-8", errors="ignore").strip()

    # match uuids
    matches = re.findall(r"\[([a-f0-9\-]{36})\]", list_text)

    if matches:
      self.sessionID = matches[-1]
      return self.sessionID
    else:
      return None

  async def send(self, text: str) -> str:
    self.last_used = time.time()

    prompt = self._build_prompt(text)

    cmd_args = [
        "gemini",
        "--yolo",
        "--prompt",
        prompt,
        "--output-format",
        "text",
        "--model",
        self.model,
    ]

    if self.sessionID is not None:
      cmd_args.extend(["--resume", self.sessionID])

    try:
      process = await asyncio.create_subprocess_exec(
          *cmd_args,
          stdout=asyncio.subprocess.PIPE,
          stderr=asyncio.subprocess.DEVNULL,
      )

      stdout, _ = await asyncio.wait_for(process.communicate(), timeout=180)
      reply = stdout.decode("utf-8", errors="ignore").strip()

      if self.sessionID is None:
        self.sessionID = await self._get_session_id()
        print(f"DEBUG: Captured new Session ID: {self.sessionID}")
        print(f"DEBUG: Reply: {reply}")

      return reply

    except asyncio.TimeoutError:
      process.kill()
      await process.wait()
      return "Error: Gemini timeout"
    except Exception as e:
      return f"Error: {e}"

  async def delete(self):
    process = await asyncio.create_subprocess_exec(
        "gemini",
        "--delete-session",
        self.sessionID,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )

    stdout, _ = await asyncio.wait_for(process.communicate(), timeout=180)
    reply = stdout.decode("utf-8", errors="ignore").strip()

    return reply
