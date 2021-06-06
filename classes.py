import logging

import py7zr
import time
import os
import requests
import configparser

from sys import platform
from bs4 import BeautifulSoup as bs

import google_search


class ConfigFile:
    def __init__(self):
        # TODO: Finish this with a getters and setters
        self.configparser_class = configparser.ConfigParser()
        self.thisfolder = os.path.dirname(os.path.abspath(__file__))

        self.config_file = self.configparser_class.read(os.path.join(self.thisfolder, 'config.ini'))
        self.permitted_admins = self.configparser_class.get('DEFAULT', 'ADMIN_IDS').split(',')

        self.limitation_title_words = self.configparser_class.get('CONSTANTS', 'LIMITATION_TITLE_WORDS')
        self.limitation_of_length = self.configparser_class.get('CONSTANTS', 'LIMITATION_OF_LENGTH')
        self.minimum_question_words = self.configparser_class.get('CONSTANTS', 'MINIMUM_QUESTION_WORDS')
        self.webhook_host = self.configparser_class.get('DEFAULT', 'WEBHOOK_HOST')
        self.webhook_port = self.configparser_class.get('DEFAULT', 'WEBHOOK_PORT')

        self.bot_dev_status = self.configparser_class.get('DEFAULT', 'BOT_STATUS')
        if self.bot_dev_status != 'dev':
            self.telegram_token = self.configparser_class.get('DEFAULT', 'TelegramToken')
        else:
            self.telegram_token = self.configparser_class.get('DEFAULT', 'TelegramTokenTest')

        self.webhook_listen = self.configparser_class.get('DEFAULT',
                                                          'WEBHOOK_LISTEN')

        self.webhook_ssl_cert = self.configparser_class.get('DEFAULT',
                                                            'WEBHOOK_SSL_CERT')
        self.webhook_ssl_priv = self.configparser_class.get('DEFAULT',
                                                            'WEBHOOK_SSL_PRIV')
        self.heroku_url = self.configparser_class.get('DEFAULT', 'HEROKU_URL')
        self.webhook_url_base = "https://%s:%s" % (self.webhook_host, self.webhook_port)
        self.webhook_url_path = "/%s/" % self.telegram_token

        # Google CSE keys
        google_search.SEARCH_ENGINE_ID = self.configparser_class.get('DEFAULT', 'GOOGLE_CSE_ENGINE_ID')
        google_search.API_KEY = self.configparser_class.get('DEFAULT', 'GOOGLE_CSE_API')
        google_search.MAX_SEARCH_RESULTS = int(self.configparser_class.get('CONSTANTS', 'MAX_SEARCH_RESULTS'))



class LoggerClass:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.script_location = os.path.dirname(__file__)
        self.current_time = time.strftime('%Y_%m_%d-%H_%M_%S')
        self.logs_file_location = ''
        self.filename_only = f"{self.current_time}.log"
        self.full_path_with_filename = fr"{self.logs_file_location}\logs\{self.filename_only}"

        self.logs_file_folder = self.log_files_path_by_os()
        self.archive_name = ''
        self.logs_files_list = []

        # Logger configurations
        self.log_formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            filemode='a',
            format=f'{self.log_formatter}',
            level=logging.INFO
        )
        timefmt = time.strftime("%a, %d %b %Y %H:%M:%S +0200", time.gmtime())
        fmt = logging.Formatter(self.log_formatter, datefmt=timefmt)

        # Starting the logging in the configured path for the log files
        try:
            fh = logging.FileHandler(
                filename=f'{self.logs_file_folder}{self.filename_only}',
                encoding='utf-8'
            )
            # self.logger.addHandler(fh)
        except Exception as e:
            logging.error(e)
            os.mkdir(self.logs_file_folder)
            logging.info(f'{self.logs_file_folder} folder created')
            logging.info(f'Logs folder exists? {os.path.exists(self.logs_file_folder)}')
            fh = logging.FileHandler(
                filename=f'{self.logs_file_folder}{self.filename_only}',
                encoding='utf-8'
            )
        self.logger.addHandler(fh)
        fh.setFormatter(fmt)

        self.logger.info(f'The script running on {platform}...')

    def log_files_path_by_os(self):
        """This function checks the OS that the script is running on and sets the local path of the script.

        :return: logs file location by OS name (platform).
        """
        if platform == "linux" or platform == "linux2":
            self.logs_file_location = f"{self.script_location}/logs/"
            self.logger.info(f'logs file location: {self.logs_file_location}')
            return self.logs_file_location
        elif platform == "win32":
            self.logs_file_location = f"{self.script_location}\\logs\\"
            self.logger.info(f'logs file location for {platform}: {self.logs_file_location}')
            return self.logs_file_location
        else:
            # TODO: Place a configurable logs location in Config.ini file
            return self.logger.info(f'The OS is "{platform}", please configure the logs path.')

    def logs_file_handler(self):
        """Opening the latest ".log" file that created.

        :return: ".log" file name and opens it by open().
        """
        file_location = f"{self.logs_file_location}{self.current_time}.log"

        try:
            file_handle = open(file_location, 'rb')
            return file_handle
        except Exception as e:
            logging.error(e)

    # TODO: Move this to files class
    def log_files_compressor(self):
        """Compressing to 7z file the logs folder.

        :return: the compressed file ready to be sent
        """
        with py7zr.SevenZipFile(f"{self.logs_file_folder}{self.current_time}.7z", 'w') as archive:
            archive.writeall(self.logs_file_folder)

        self.archive_name = archive.filename
        file_handle = open(f"{self.logs_file_folder}{self.current_time}.7z", 'rb')

        return file_handle

    # TODO: Move this to files class
    def log_files_counter(self):
        """This function counts the log files

        :return: Counter of the log files inside the logs folder.
        """
        DIR = self.logs_file_location
        counter = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
        self.logs_files_list.append([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

        return counter

    # TODO: Move this to files class
    def zip_file_remover(self, file=None):
        if file is not None:
            os.remove(file)
        # TODO: Remove all the log files after the ZIP file removed
        try:
            for filename_index in range(len(self.logs_files_list)):
                os.remove(f"{self.logs_file_folder}{self.logs_files_list[0][filename_index]}")
                print(f"{self.logs_file_folder}{self.logs_files_list[0][filename_index]}")
            self.log_files_counter()
            if self.logs_files_list == 0:
                return "File {} was removed and all other log files was removed.".format(file)
            else:
                return f"Found {len(self.logs_files_list)} files in the folder."
        except Exception as e:
            self.log_files_counter()
            return e


class ChatInformation:
    """
    This class handles all the usename informations sorts.
    """
    def __init__(self, message=None):
        self.post_steps = {}
        self.message_to_remove_id = None
        try:
            self.message = message
            self.chat_id = message.chat.id
            self.message_text = message.text
            self.message_id = message.message_id
            self.message_id_from_bot = ""
            self.forwarded_message_type = message.forward_from.content_type
            self.forwarded_from_chat = message.forward_from.forward_from_chat
            self.forwarded_from_message_id = message.forwarded_from_message_id
        except:
            return


class MessageStrings:
    def help(self):
        self.msg = f"""
    ברוכים הבאים לבוט החיפוש של האתר Devhub.co.il!
     על ידי הבוט הנ"ל תוכלו לבצע חיפוש בגוגל למה שתרצו 
    רשימת פקודות: 
    /s שורת החיפוש שלכם
    /links
    /help    
        """
        return self.msg

    def start(self):
        self.msg = f"""
    רשימת פקודות: 
    /s שורת החיפוש שלכם
    /links
    /help    
        """

        return self.msg

    def links(self):
        return '''
    ◀️ קישורי אתר:
[🔗 עמוד הבית](https://devhub.co.il/boards) [🔗 מדריכים](https://devhub.co.il/boards/tutorials)
[🔗 פעילות אחרונה](https://devhub.co.il/boards/discover) [🔗 חיפוש בפורום](https://devhub.co.il/boards/search)

    ◀️ קישורי טלגרם:
[🔗 קהילה בטלגרם](https://t.me/devhubilg) [🔗 ערוץ עדכונים](https://t.me/devhubil)
[🔗 בוט שאלות ותשובות](https://t.me/Devhub_bot) [🔗 בוט חיפוש בגוגל](https://t.me/devhubgoogle_bot)

    ◀️ עוד בטלגרם:
[🔗 Python](https://t.me/devhubpython) [🔗 C languages](https://t.me/devhubc)
[🔗 dot NET](https://t.me/devhubdotnet) [🔗 DevOps](https://t.me/devhubdevops)
[🔗 Powershell](https://t.me/devhubps) [🔗 IT ותמיכה טכנית](https://t.me/devhubit)
[🔗 MongoDB](https://t.me/devhubmongodb)
    ◀️ קישורי וואטסאפ:
[🔗 קהילה בוואטסאפ](https://chat.whatsapp.com/KAnjACMh4X61RpfqwO5RpX)
'''


class Search:
    def __init__(self, name_search=None):
        self.name = name_search
        self.thepage = None
        self.websites_list = []
        self.websites_titles_list = []
        self.new_websites_url_list = []
        self.new_websites_titles_list = []
        self.file_urls = []

        # Single desciption and title for link postage
        self.website_description = ''
        self.website_picture = ''
        self.website_title = ''
        self.website_url = ''
        self.website_urls = []
        self.regex_url_pattern = r"^(http[s]?:\/\/)?([^:\/\s]+)(:([^\/]*))?(\/\w+\.)*([^#?\s]+)(\?([^#]*))?(#(.*))?$"
        self.MAX_SEARCH_RESULTS = 5

    def new_gsearch(self):
        import google_search
        google_searcher = google_search.Gsearch(self.name)
        google_searcher.results()


    def Gsearch(self, ) -> list:

        from googlesearch import search

        self.websites_list = search(self.name, num_results=self.MAX_SEARCH_RESULTS, lang='he')

        return self.websites_list

    def search_titles(self, websites_list):
        files_class = Files()
        logger_class = LoggerClass()
        len_list = len(websites_list)

        if len(self.websites_titles_list) != 0:  # Addition resets the titles list
            self.websites_titles_list = []

        for i in range(len_list):
            itisfile = files_class.isitfile(websites_list[i])
            logger_class.logger.info("link from websites_list: " + websites_list[i])

            if not itisfile and websites_list[i] != None:
                try:
                    r = requests.get(websites_list[i])
                    soup = bs(r.content.strip(), 'html.parser')
                    self.websites_titles_list.append(soup.select_one('title').text)
                except Exception as e:
                    r = "ללא כותרת"
                    return e
            # Can't remember which issue this resolves
             # elif i == 0:
                 # return self.websites_titles_list
                 # return websites_list[i]
            else:
                filename = files_class.filename(websites_list[i])
                self.websites_titles_list.append(filename)
                self.file_urls.append(websites_list[i])
        return self.websites_titles_list

    def search_description(self, websites):
        self.website_url = websites
        for i in range(len(self.website_url)):
            r = requests.get(self.website_url[i])
            soup = bs(r.content, 'html.parser')
            try:
                self.website_description = soup.find("meta", {"name": "description"})['content']
                self.website_picture = soup.find("meta", {"property": "og:image"})['content']
                self.website_title = soup.select_one('title').text

                if self.website_title == '':
                    self.website_title = self.website_description.split(sep=' ')[:10]
                    self.website_title = ' '.join(self.website_title)
                return {self.website_description, self.website_picture, self.website_title}
            except:
                self.website_description = soup.select_one('title').text
                if self.website_title == '':
                    self.website_title = self.website_description.split(sep=' ')[:10]
                    self.website_title = ' '.join(self.website_title)

                # Check if the title is already exists
                elif self.website_title != self.website_description:
                    self.website_title = self.website_description.split(sep=' ')[:10]
                    self.website_title = ' '.join(self.website_title)

                return {self.website_description, self.website_title}

    def search_title_url_merger(self, urls_list, titles_list):
        result_dict = []
        if len(urls_list) == len(titles_list):
            for index in range(len(urls_list)):
                result_dict.append(dict(zip(titles_list[index], [urls_list[index]])))
            return result_dict
        else:
            return "The URLs and the Titles amount not the same."


class Files:
    def isitfile(self, link=None, links=None):
        """ This function finds a file extention.
        May receive Single string or a List of strings (Usually preferred URL style)

        :param link: may be list or single URL
        :return: Boolean
        """
        if links is not None:
            for files in range(len(link)):
                get_basename = links[files].split('.')[-1]

                if get_basename == 'pdf':
                    logging.info(f"PDF file found: {get_basename}")
                    return True
                else:
                    logging.info("PDF file not found")
                    return False
        elif link is not None:
            try:
                get_basename = link.split('.')[-1]

                if get_basename == 'pdf':
                    logging.info(f"PDF file found: {get_basename}")
                    return True
                else:
                    logging.info("PDF file not found")
                    return False
            except Exception as e:
                logging.info("EXCEPTION: ", e)

    def filename(self, link=None):
        """ This function gets a link and parses it to a full filename.

        :param link: the URL to the filename
        :return: only the filename with the extension
        """
        from urllib.parse import urlparse
        global get_basename, parse_object

        # Get the filename from the URL
        parse_object = urlparse(link).path.split('.')[-1]
        if parse_object == 'pdf':
            return urlparse(link).path.split('/')[-1]
        else:
            return link


class BotMisc(ConfigFile):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.premitted_users = self.permitted_admins  # [67785586, 12655213]

    def check_premission(self, user_id):
        self.user_is_admin = False

        if str(user_id) in self.premitted_users:
            self.user_is_admin = True
        return self.user_is_admin


if __name__ == "__main__":
    print(f"The application started for testing from {__file__}.")
    files_class = Files()
    resulting = files_class.isitfile('https://www.hawaiipublicschools.org/DOE%20Forms/CTE/RIASEC.pdf')
    print(resulting)
    # google_search = Search('googalah')
    # search = google_search.Gsearch()
    # webparingresult = google_search.search_titles(search)
    # google_search.search_description(search)

    urls_list = [r'https://rnd.ebay.co.il/', r'https://www.ebay.co.il/sell/israel-ebay-shipping-platform-manual/', r'https://www.gov.il/en/departments/israel_national_cyber_directorate']
    website_description = Search()
    for links_index in urls_list:
        website_description.search_description(links_index)
        print("Link: {}\nTitle:{}\nDescription:{}".format(links_index,
                                                           website_description.website_title,
                                                           website_description.website_description))

    print("Finished.")
