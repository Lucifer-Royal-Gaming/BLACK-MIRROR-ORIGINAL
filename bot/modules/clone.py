import random
import string
from threading import Thread
import pytz

from datetime import datetime
from telegram.ext import CommandHandler
from telegram import ParseMode
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import auto_delete_message, sendMessage, sendMarkup, deleteMessage, delete_all_messages, update_all_messages, sendStatusMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.mirror_utils.status_utils.clone_status import CloneStatus
from bot import PM_LOG, bot, dispatcher, LOGGER, CLONE_LIMIT, STOP_DUPLICATE, LOGS_CHATS, download_dict, download_dict_lock, Interval, TIMEZONE
from bot.helper.ext_utils.bot_utils import get_readable_file_size, is_appdrive_link, is_gdrive_link, is_gdtot_link, new_thread, secondsToText
from bot.helper.mirror_utils.download_utils.direct_link_generator import appdrive, gdtot
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

@new_thread
def cloneNode(update, context):
    if PM_LOG:
        try:
            sent_msg = bot.copy_message(
                chat_id=update.message.from_user.id,
                from_chat_id=update.message.chat.id,
                message_id=update.message.message_id
            )
            deleteMessage(update.message.from_user.id, sent_msg.message_id)
        except Exception as ex:
            print(ex)
            help_msg = '𝐒𝐭𝐚𝐫𝐭 𝐓𝐡𝐞 𝐁𝐨𝐭 𝐔𝐬𝐢𝐧𝐠 𝐓𝐡𝐞 𝐋𝐢𝐧𝐤,\n\n𝐈𝐭 𝐍𝐞𝐞𝐝𝐞𝐝 𝐅𝐨𝐫 𝐅𝐢𝐫𝐬𝐭 𝐓𝐢𝐦𝐞\n\n𝐒𝐨 𝐁𝐨𝐭 𝐂𝐚𝐧 𝐆𝐢𝐯𝐞 𝐘𝐨𝐮 𝐌𝐢𝐫𝐫𝐨𝐫 𝐅𝐢𝐥𝐞𝐬 𝐈𝐧 𝐘𝐨𝐮𝐫 𝐏𝐌 \n𝐇𝐞𝐫𝐞 𝐈𝐬 𝐓𝐡𝐞 𝐋𝐢𝐧𝐤: https://t.me/' + bot.get_me().username + '?start=start'
            return sendMessage(help_msg, context.bot, update.message)
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    link = ''
    if len(args) > 1:
        link = args[1]
        if update.message.from_user.username:
            tag = f"@{update.message.from_user.username}"
        else:
            tag = update.message.from_user.mention_html(update.message.from_user.first_name)
    if reply_to is not None:
        if len(link) == 0:
            link = reply_to.text
        if reply_to.from_user.username:
            tag = f"@{reply_to.from_user.username}"
        else:
            tag = reply_to.from_user.mention_html(reply_to.from_user.first_name)
    is_appdrive = is_appdrive_link(link)
    if is_appdrive:
        try:
            msg = sendMessage(f"Pʀᴏᴄᴇssɪɴɢ Aᴘᴘᴅʀɪᴠᴇ Lɪɴᴋ:- \n<code>{link}</code>", context.bot, update.message)
            link = appdrive(link)
            deleteMessage(context.bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update)
    is_gdtot = is_gdtot_link(link)
    if is_gdtot:
        try:
            msg = sendMessage(f"𝐁𝐘𝐏𝐀𝐒𝐒𝐈𝐍𝐆 𝐆𝐃𝐓𝐎𝐓 𝐋𝐈𝐍𝐊 ⇝ <code>{link}</code>", context.bot, update.message)
            link = gdtot(link)
            deleteMessage(context.bot, msg)
        except DirectDownloadLinkException as e:
            deleteMessage(context.bot, msg)
            return sendMessage(str(e), context.bot, update.message)
    if is_gdrive_link(link):
        autodel = secondsToText()
        msg1 = f'<b> I have sent files in PM & <a href="https://t.me/reflectionmir_logs"><b>LOG CHANNEL</b></a>\n This message will auto deleted in {autodel} </b>' if PM_LOG else ''
        gd = GoogleDriveHelper()
        res, size, name, files = gd.helper(link)
        if res != "":
            return sendMessage(res, context.bot, update.message)
        if STOP_DUPLICATE:
            LOGGER.info('Checking File/Folder if already in Drive...')
            smsg, button = gd.drive_list(name, True, True)
            if smsg:
                msg3 = "📂 𝐅𝐢𝐥𝐞/𝐅𝐨𝐥𝐝𝐞𝐫 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐢𝐧 𝐃𝐫𝐢𝐯𝐞.\n𝐇𝐞𝐫𝐞 𝐚𝐫𝐞 𝐭𝐡𝐞 𝐬𝐞𝐚𝐫𝐜𝐡 𝐫𝐞𝐬𝐮𝐥𝐭𝐬 ↴"
                return sendMarkup(msg3, context.bot, update.message, button)
        if CLONE_LIMIT is not None:
            LOGGER.info('Checking File/Folder Size...')
            if size > CLONE_LIMIT * 1024**3:
                msg2 = f'𝐅𝐚𝐢𝐥𝐞𝐝, 𝐂𝐥𝐨𝐧𝐞 𝐥𝐢𝐦𝐢𝐭 𝐢𝐬 {CLONE_LIMIT}GB.\nYour File/Folder size is {get_readable_file_size(size)}.'
                return sendMessage(msg2, context.bot, update.message)
        if files <= 20:
            msg = sendMessage(f"⚙️ 𝐂𝐥𝐨𝐧𝐢𝐧𝐠 𝐘𝐨𝐮𝐫 𝐅𝐢𝐥𝐞/𝐅𝐨𝐥𝐝𝐞𝐫 𝐈𝐧𝐭𝐨 𝐌𝐲 𝐃𝐫𝐢𝐯𝐞 !! 𝐘𝐨𝐮𝐫 𝐋𝐢𝐧𝐤 ⇝ <code>{link}</code>", context.bot, update.message)
            result, button = gd.clone(link)
            deleteMessage(context.bot, msg)
        else:
            drive = GoogleDriveHelper(name)
            gid = ''.join(random.SystemRandom().choices(string.ascii_letters + string.digits, k=12))
            clone_status = CloneStatus(drive, size, update.message, gid)
            with download_dict_lock:
                download_dict[update.message.message_id] = clone_status
            sendStatusMessage(update.message, context.bot)
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
        result += f'\n╰─📬 𝐁𝐲 ⇢ {tag}\n\n'
        if button in ["cancelled", ""]:
            reply_message = sendMessage(f"{tag} {result}", context.bot, update.message)
        else:
            reply_message = sendMarkup(result + msg1, context.bot, update.message, button)
            if PM_LOG:
                Thread(target=auto_delete_message, args=(context.bot, update.message, reply_message, True)).start()
                bot.sendMessage(chat_id=update.message.from_user.id, text=result, reply_markup=button, parse_mode=ParseMode.HTML) 
        if LOGS_CHATS:
            try:
                for i in LOGS_CHATS:
                    kie = datetime.now(pytz.timezone(f'{TIMEZONE}'))
                    jam = kie.strftime('\n 𝗗𝗮𝘁𝗲 : %d/%m/%Y\n 𝗧𝗶𝗺𝗲: %I:%M:%S %P')
                    msg1 = f'{jam}'
                    msg1 += f'\n╭─📂 𝐅𝐢𝐥𝐞𝐧𝐚𝐦𝐞 ⇢ <code>{name}</code>'
                    msg1 += f'\n├─🕹️ Size ⇢ {get_readable_file_size(size)}'
                    msg1 += f'\n╰─📬 𝐁𝐲 ⇢ {tag}\n\n'
                    bot.sendMessage(chat_id=i, text=msg1, reply_markup=button, parse_mode=ParseMode.HTML)
            except Exception as e:
                LOGGER.warning(e)
        if is_gdtot:
            gd.deletefile(link)
        if is_appdrive:
            gd.deletefile(link)
    else:
        sendMessage('𝐆𝐢𝐯𝐞 𝐆𝐝𝐫𝐢𝐯𝐞 𝐨𝐫 𝐆𝐝𝐫𝐢𝐯𝐞 site 𝐥𝐢𝐧𝐤 𝐚𝐥𝐨𝐧𝐠 𝐰𝐢𝐭𝐡 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐨𝐫 𝐛𝐲 𝐫𝐞𝐩𝐥𝐲𝐢𝐧𝐠 𝐭𝐨 𝐭𝐡𝐞 𝐥𝐢𝐧𝐤 𝐛𝐲 𝐜𝐨𝐦𝐦𝐚𝐧𝐝', context.bot, update.message)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
