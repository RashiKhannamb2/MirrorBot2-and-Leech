from telegram.ext import CommandHandler
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot import LOGGER, dispatcher
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands


def list_drive(update, context):
    try:
        search = update.message.text.split(' ', maxsplit=1)[1]
        LOGGER.info(f"<b>🔎 Searching...</b> {search}")
        reply = sendMessage('🔎 Searching... Please wait! 🤒</b>', context.bot, update)
        gdrive = GoogleDriveHelper()
        msg, button = gdrive.drive_list(search)

        if button:
            editMessage(msg, reply, button)
        else:
            editMessage(f'<b>❌ No Result Found for :</b> {search}', reply, button)

    except IndexError:
        sendMessage('<b>Send a Search Key along With Command 😡</b>', context.bot, update)


list_handler = CommandHandler(BotCommands.ListCommand, list_drive, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(list_handler)
