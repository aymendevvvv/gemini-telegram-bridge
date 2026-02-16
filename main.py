import logging
from session_manager import SessionManager
from telegram.constants import ParseMode

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

session_manager = SessionManager()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user = update.effective_user
  await update.message.reply_html(
      rf"Hi {user.mention_html()}!",
      reply_markup=ForceReply(selective=True),
  )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  await update.message.reply_text("Help!")


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  chat_id = update.effective_chat.id
  text = update.message.text

  gemini = await session_manager.get_session(chat_id)
  reply = await gemini.send(text)

  if reply:
    await update.message.reply_text(parse_mode=ParseMode.HTML, text=reply)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
  logger.error(msg="Exception while handling an update:",
               exc_info=context.error)


async def post_init(application: Application) -> None:
  application.job_queue.run_repeating(
    session_manager.cleanup, interval=60, first=0)


def main() -> None:
  application = Application.builder().token(BOT_TOKEN).connect_timeout(
    60).read_timeout(60).write_timeout(60).pool_timeout(60).post_init(post_init).build()

  application.add_error_handler(error_handler)

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("help", help_command))

  application.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND, reply))

  application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
  main()
