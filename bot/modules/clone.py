import random
import string
from telegram.ext import CommandHandler
from bot.helper.mirror_utils.upload_utils import gdriveTools
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, download_dict, download_dict_lock, Interval
from bot.helper.ext_utils.bot_utils import get_readable_file_size, new_thread


@new_thread
def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        gd = gdriveTools.GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            sendMessage(res, context.bot, update)
            return
        if STOP_DUPLICATE:
            LOGGER.info('<b>📁 Checking File/Folder if already in Drive...🤒</b>')
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "<b>📁 File/Folder is already Available in Drive..!! 🤒</b>\n<b>🔎 Here are the Search Results 👇</b>"
                sendMarkup(msg3, context.bot, update, button)
                return
        if CLONE_LIMIT is not None:
            LOGGER.info('<b>💽 Checking File/Folder Size...</b>')
            if size > CLONE_LIMIT * 1024**3:
                msg2 = f'<b>,🚫 Failed, Clone limit is {CLONE_LIMIT}GB 😷</b>\n<b>Your File/Folder size is {get_readable_file_size(size)} 😱</b>'
                sendMessage(msg2, context.bot, update)
                return
        if files <= 10:
            msg = sendMessage(f"<b>♻️ Cloning... :</b> <code>{link}</code>", context.bot, update)
            result, button = gd.clone(link)
            deleteMessage(context.bot, msg)
        else:
            drive = gdriveTools.GoogleDriveHelper(name)
            gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
            clone_status = CloneStatus(drive, size, update, gid)
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            sendStatusMessage(update, context.bot)
            result, button = drive.clone(link)
            with download_dict_lock:
                del download_dict[update.message.message_id]
                count = len(download_dict)
            try:
                if count == 0:
                    Interval[0].cancel()
                    del Interval[0]
                    delete_all_messages()
                else:
                    update_all_messages()
            except IndexError:
                pass
        if update.message.from_user.username:
            uname = f'@{update.message.from_user.username}'
        else:
            uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
        if uname is not None:
            cc = f'\n\n<b>👤 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐁𝐲 : {uname}</b>\n\n💫 𝑷𝒐𝒘𝒆𝒓𝒆𝒅 𝑩𝒚 : 𝑾𝒉𝒊𝒕𝑬_𝑫𝒆𝒗𝒊𝑳𝟎𝟗'
            men = f'{uname} '
        if button in ["<b>❌ cancelled</b>", ""]:
            sendMessage(men + result, context.bot, update)
        else:
            sendMarkup(result + cc, context.bot, update, button)
    else:
        sendMessage('<b>📎 Provide G-Drive Shareable Link to Clone 🤒</b>', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
