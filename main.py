"""
Regex testing:
https://regex101.com/

The Telebot link:
https://github.com/eternnoir/pyTelegramBotAPI

----------------
"""
from time import sleep

from flask import request
from telebot import types, apihelper

import duckduckgo
import classes
import configparser
import getip
import os
import telebot
import flask

from classes import LoggerClass, MessageStrings, ConfigFile
from forum_webhook import ForumOperation

# Logger class
logger_class = LoggerClass()
logger = LoggerClass().logger
apihelper.ENABLE_MIDDLEWARE = True

# Bot Miscelenius staff
bot_misc = classes.BotMisc()
message_strings = MessageStrings()
config = ConfigFile()
forum_operations = ForumOperation()
search_class = classes.Search()
configparser_class = configparser.ConfigParser()
chat_info = classes.ChatInformation()
files_class = classes.Files()
duckduckgo_search = duckduckgo.DuckDuckGoSearch()

bot = telebot.TeleBot(config.telegram_token, parse_mode='HTML')
app = flask.Flask(__name__)


# telebot_debug = telebot.logger.setLevel(logging.DEBUG)
# logger.info(telebot_debug)


@bot.message_handler(commands=['help', 'start'])
def help(message):
    """
    This function has help and start message
    :param: command: /help for getting the help message
    :param: command_l = /start for getting started
    """
    start_message = message_strings.start()
    help_message = message_strings.help()

    if message.text == '/start':
        logger.info(f"The user {message.from_user.username} ran /start command")
        bot.send_message(message.chat.id, text=start_message)
    else:
        logger.info(f"The user {message.from_user.username} ran /help command")
        bot.send_message(message.chat.id, text=help_message)


@bot.message_handler(commands=['s'])
def g_search(message):
    chat_info.chat_id = message.chat.id

    logger.info(f"The user {message.from_user.username} wrote:\n{message.text}")

    wo_command_text = str(message.text).split(" ")[1:]
    logger.info(f"The user {message.from_user.username} ran /s command ")

    logger.info("Now running a G-search...")
    bot.send_chat_action(chat_id=chat_info.chat_id, action="typing")
    msg = bot.send_message(chat_id=message.chat.id,
                           text="עכשיו אנחנו בודקים לך קישורים מעניינים..."
                           )

    logger.info("Now running DuckDuckGo search...")
    msgddg = bot.send_message(chat_id=message.chat.id, text="עכשיו מחפשים DuckDuckGo...")
    duckduckgo_search.query = " ".join(wo_command_text)
    ddg_results = duckduckgo_search.search_method()

    # DuckDuckGo results print
    result_buttons(msgddg.id, ddg_results=ddg_results)
    bot.delete_message(chat_id=chat_info.chat_id, message_id=msg.id)
    logger.info("Now running a G-search...")
    msgggl = bot.send_message(chat_id=message.chat.id, text="עכשיו מחפשים בגוגל...")
    chat_info.message_id_from_bot = msg.id
    search = classes.Search(" ".join(wo_command_text)).Gsearch()

    # Not for now...
    # forum_search = forum_operations.forum_search(forum_operations.title)

    if len(search) == 0:
        logger.info("No links found.")
    else:
        logger.info('Found links:\n{}'.format(", ".join(search)))
        bot.edit_message_text(message_id=msgggl.id, chat_id=message.chat.id, text="מחפש כותרות...")
        search_titles = search_class.search_titles(search)
        logger.info('search_titles:\n{}'.format(', '.join(search_class.websites_titles_list)))
        logger.info(
            f"len of search_titles:{len(search_titles)}, len of search:{len(search)}\nsearch_titles:{', '.join(search_titles)}")

        if search_titles != None or len(search_titles) == len(search):
            # Google results print
            result_buttons(message_id_to_edit=msgggl.id, urls_list=search, titles_list=search_titles)

        else:
            logger.error(
                f"len of search_titles:{len(search_titles)}, len of search:{len(search)}\nsearch_titles:{', '.join(search_titles)}")
            bot.edit_message_text(message_id=msg.id, chat_id=message.chat.id, text="קרתה תקלה, נסו שנית!")

            # Send log files if issue occur
            if bot_misc.check_premission(message.chat.id):
                logger.error(f"{message.from_user.username} used text:\n{message.text}")
                send_log_to_admin(message)
        # FORUM SEARCH RESULTS
        # if forum_search is not None:
        #     for title, title_url in forum_search.items():
        #         itembtnb = types.InlineKeyboardButton(title, switch_inline_query="", url=title_url)
        #         markup.row(itembtnb)


def result_buttons(message_id_to_edit, urls_list=None, titles_list=None, ddg_results=None):
    markup = types.InlineKeyboardMarkup()

    # This is for Google search
    if urls_list is not None:
        for i in range(len(titles_list)):
            isitfile = files_class.isitfile(link=urls_list[i])

            if isitfile:
                bot.send_message(chat_id=chat_info.chat_id, text=urls_list[i])
            else:
                itembtnb = types.InlineKeyboardButton(titles_list[i], switch_inline_query="", url=urls_list[i])
                markup.row(itembtnb)
                bot.edit_message_text(message_id=message_id_to_edit, chat_id=chat_info.chat_id, text="תוצאות החיפוש שלך מגוגל:",
                                      reply_markup=markup)

    # This is for DuckDuckGo search
    else:
        for ddg_item in range(10):
            ddg_item = ddg_results[ddg_item]
            isitfile = files_class.isitfile(link=ddg_item['url'])

            if isitfile:
                bot.send_message(chat_id=chat_info.chat_id, text=ddg_item['url'])
            else:
                itembtnb = types.InlineKeyboardButton(ddg_item['title'], switch_inline_query="", url=ddg_item['url'])
                markup.row(itembtnb)
                bot.edit_message_text(message_id=message_id_to_edit, chat_id=chat_info.chat_id, text="תוצאות החיפוש שלך מDuckDuckGo:",
                                      reply_markup=markup)


@bot.message_handler(commands=['links'])
def links_command(message):
    logger.info(f'username {message.from_user.username} requested links')
    links = message_strings.links()
    msg = bot.send_message(message.chat.id, links, parse_mode='MarkdownV2', disable_web_page_preview=False)
    bot.delete_message(message.chat.id, message.from_user.id, 1)


# @bot.message_handler(commands=['lcom'])
# def linux_command(message):
#     if check_premission(message.chat.id):
#         logger.info(f"{message.chat.username} used a linux command: {message.text}")
#         msg = bot_misc.linux_commands(str(message.text).replace('/lcom', ''))
#         logger.info("msg: ", msg)
#         bot.send_message(message.chat.id, msg)
#         logger.info(msg)
#     else:
#         bot.reply_to(message, "You're unable to use this command.")
#         logger.error(f"{message.from_user.username} used a command {message.text}")


@bot.message_handler(commands=['ip'])
def getting_ip_addresses_command(message):
    check_permissions = bot_misc.check_premission(message.chat.id)
    if check_permissions:
        logger.info(f'{message.from_user.username}, pass the permissions with command {message.text}')

        # Get internal IP address
        local_ip = getip.get_local_ip()
        bot.send_message(message.chat.id, f"Local IP: {local_ip}")
        logger.info(f"Requested by username: {message.from_user.username} - Local IP: {local_ip}")
        msg = bot.send_message(message.chat.id, "checking an external IP...")

        # Get external IP address
        external_ip = getip.get_external_ip()

        bot.edit_message_text(f"External IP: {', '.join(external_ip)}", msg.chat.id, msg.id)

        logger.info(f'Requested by username: {message.from_user.username} - External IP: {external_ip}')

    else:
        bot.reply_to(message, "אין באפשרותך להריץ את הפקודה הזו. אנא צור קשר עם @IceBergius")
        logger.error(f"{message.from_user.username} used a command {message.text}")
        send_log_to_admin(message)


@bot.message_handler(commands=['logs'])
def log_files_sender(message):
    check_permissions = bot_misc.check_premission(message.chat.id)
    doc = logger_class.logs_file_handler()
    if check_permissions:
        logger.info(f'{message.from_user.username}, pass the permissions with command {message.text}')

        doc = logger_class.logs_file_handler()
        log_filename = logger_class.filename_only
        bot.send_chat_action(message.chat.id, 'typing')
        # The uncompressed log file sender
        bot.send_document(message.chat.id, doc)
        logger.info(f'Sent file name: {log_filename}')

        msg = bot.send_message(message.chat.id, "מכווץ ושולח לוגים...")
        compressed_filename = logger_class.log_files_compressor()

        # The compressed log files folder sender
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_document(
            chat_id=message.chat.id,
            data=compressed_filename,
            caption=f"בקובץ יש {logger_class.log_files_counter()} קבצי לוג",
            parse_mode="MARKDOWNV2"
        )
        sleep(5)
        bot.delete_message(message.chat.id, msg.id)
        # Closing the compressed file before removing
        compressed_filename.close()
        compressed_filename_zip = compressed_filename.name.split('\\')[-1]
        logger.info(f'Sent file name: {compressed_filename_zip}')
        logger.info(logger_class.zip_file_remover(file=compressed_filename.name))
        # bot.send_message(message.chat.id,
        #                  f"**{compressed_filename_zip}** and **{log_filename}** sent to you.\nwe're done here!",
        #                  parse_mode="MARKDOWNV2"
        #                  )

    else:
        bot.reply_to(message, "אין באפשרותך להריץ את הפקודה הזו. אנא צור קשר עם @IceBergius")
        logger.error(f"{message.from_user.username} used a command {message.text}")
        send_log_to_admin(message)


def send_log_to_admin(message):
    # Send log files if issue occur
    doc = logger_class.logs_file_handler()
    log_filename = logger_class.filename_only
    bot.send_chat_action(classes.ConfigFile().permitted_admins[0], 'typing')
    # The uncompressed log file sender
    bot.send_document(chat_id=classes.ConfigFile().permitted_admins[0], data=doc,
                      caption=f"{message.from_user.username}({message.chat.id}) used admin command.")
    logger.info(f'Sent file name: {log_filename}')


@bot.message_handler(commands=['log'])
def log_files_sender(message):
    check_permissions = bot_misc.check_premission(message.chat.id)
    if check_permissions:
        logger.info(f'{message.from_user.username}, pass the permissions with command {message.text}')
        doc = logger_class.logs_file_handler()
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, "שולח קובץ לוג...")
        bot.send_document(message.chat.id, doc)  # Single log file sender
        logger.info(f'Sent file name: {logger_class.filename_only}')
    else:
        bot.reply_to(message, "אין באפשרותך להריץ את הפקודה הזו. אנא צור קשר עם @IceBergius")
        logger.error(f"{message.from_user.username} used a command {message.text}")
        # Send log files if issue occur
        if bot_misc.check_premission(message.chat.id):
            bot.reply_to(message, "אין באפשרותך להריץ את הפקודה הזו. אנא צור קשר עם @IceBergius")
            logger.error(f"{message.from_user.username} used a command {message.text}")
            send_log_to_admin(message)


if config.bot_dev_status == 'heroku':
    @app.route('/' + config.telegram_token, methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200


    @app.route("/")
    def webhook():

        bot.set_webhook(url='https://devhub-questions-bot.herokuapp.com/' + config.telegram_token)
        return "!", 200

elif config.bot_dev_status == 'localweb':
    WEBHOOK_URL_BASE = "https://%s:%s" % (config.webhook_host, config.webhook_port)
    WEBHOOK_URL_PATH = "/%s/" % config.telegram_token

    @app.route('/searchbot', methods=['GET', 'HEAD'])
    def index():
        return ''

    # Process webhook calls
    @app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)

if __name__ == "__main__":
    logger.info(msg="The application started.\nThis is a \"Google-Duckduckgo bot\" update 06.06.2021")
    bot.send_message(classes.ConfigFile().permitted_admins[0], "Bot started...")
    bot.delete_webhook(drop_pending_updates=True)
    bot.remove_webhook()
    # db.check_db_exist()

    if config.bot_dev_status == 'heroku':
        bot.remove_webhook()
        app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

    elif config.bot_dev_status == 'dev':
        bot.polling(none_stop=True)

    elif config.bot_dev_status == 'localweb':
        bot.remove_webhook()
        WEBHOOK_HOST = config.webhook_host
        WEBHOOK_PORT = config.webhook_port  # 443, 80, 88 or 8443 (port need to be 'open')
        WEBHOOK_LISTEN = config.webhook_listen  # In some VPS you may need to put here the IP addr
        bot.set_webhook(url=config.webhook_url_base + "/searchbot/" + config.webhook_url_path ,
                        certificate=open(config.webhook_ssl_cert, 'r'))

        # Start flask server
        app.run(host=WEBHOOK_LISTEN,
                port=WEBHOOK_PORT,
                ssl_context=(config.webhook_ssl_cert, config.webhook_ssl_priv),
                debug=True)
    else:
        print("Missing bot mode in config file.")
