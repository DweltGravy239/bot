import logging
import re
import paramiko
import os
from dotenv import load_dotenv
import psycopg2
from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler
from psycopg2 import Error
import subprocess

load_dotenv()
TOKEN = '7042933739:AAGAm8p_HE7HsAVpN--vrUK-AsR_oIl5PP8


# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def execute_command(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    client.close()
    
    return output, error

host = os.environ.get("RM_HOST")
port = os.environ.get("RM_PORT")
username = os.environ.get("RM_USER")
password = os.environ.get("RM_PASSWORD")
connection = None
user1 = os.environ.get("DB_USER")
password1 = os.environ.get("DB_PASSWORD")
host1 = os.environ.get("DB_HOST")
port1 = os.environ.get("DB_PORT")
db = os.environ.get("DB_DATABASE")

def release(update: Update, context):
    
    output = execute_command(host, port, username, password, "lsb_release -a")
    
    update.message.reply_text(output)
def uname(update: Update, context):
    
    output = execute_command(host, port, username, password, "uname")
    update.message.reply_text(output)
    update.message.reply_text("///////////////////////////////////////////////////////////////////")
    output = execute_command(host, port, username, password, "arch")
    update.message.reply_text(output)
    update.message.reply_text("///////////////////////////////////////////////////////////////////")
    output = execute_command(host, port, username, password, "uname -r")
    update.message.reply_text(output)
    update.message.reply_text("///////////////////////////////////////////////////////////////////")
def uptime(update: Update, context):
    
    output = execute_command(host, port, username, password, "uptime")
    
    update.message.reply_text(output)
def df(update: Update, context):
    
    output = execute_command(host, port, username, password, "df -h")
    
    update.message.reply_text(output)
def free(update: Update, context):
    
    output = execute_command(host, port, username, password, "free -h")
    
    update.message.reply_text(output)
def mpstat(update: Update, context):
    
    output = execute_command(host, port, username, password, "mpstat")
    
    update.message.reply_text(output)
def get_w(update: Update, context):
    
    output = execute_command(host, port, username, password, "w -s")
    
    update.message.reply_text(output)
def get_auths(update: Update, context):
    
    output = execute_command(host, port, username, password, "last -n 10 -R")
    
    update.message.reply_text(output)
def get_critical(update: Update, context):
    
    output = execute_command(host, port, username, password, "journalctl -p crit -n 5")
    
    update.message.reply_text(output)
def get_ps(update: Update, context):
    
    output = execute_command(host, port, username, password, "ps -h")
    
    update.message.reply_text(output)
def get_ss(update: Update, context):
    
    output = execute_command(host, port, username, password, "ss | tail -n 10")
    
    update.message.reply_text(output)
def get_apt_listcommand(update: Update, context):
    update.message.reply_text(f'Выберите вариант поиска:')
    update.message.reply_text(f'1. Введите = all, для вывода всех пакетов')
    update.message.reply_text(f'2. Введите название пакета')
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text.strip()
    if user_input.lower() == 'all':
        output = execute_command(host, port, username, password, "apt list | tail -n 10")

    else:
        b = f"apt list --installed | grep {user_input} | tail -n 10"
        output = execute_command(host, port, username, password, b)

    update.message.reply_text(output)
def search_package(update: Update, context: CallbackContext):
    user_input = update.message.text
    f = 'apt list ' + user_input
    update.message.reply_text(f)
    output = execute_command(host, port, username, password, "apt list " + user_input)
    update.message.reply_text(output)
def get_services(update: Update, context):
    
    output = execute_command(host, port, username, password, "systemctl --all | tail -n 10")
    
    update.message.reply_text(output)
def get_logs(update: Update, context):
    
    output = execute_command(host, port, username, password, "docker logs db_repl_image")
    update.message.reply_text(output)




def helpCommand(update: Update, context):
    update.message.reply_text(
    'Список доступных комманд:\n \
    /find_email - поиск email адресов в тексте.\n \
    /find_phone_number - поиск телефонных номеров в\n\
    тексте.\n\
    /verify_password - для проверки надежности пароля.\n\
    /get_release - о релизе.\n\
    /get_uname - об архитектуры процессора, имени хоста\n \
    системы и версии ядра.\n\
    /get_uptime - о времени работы.\n\
    /get_df - сбор информации о состоянии файловой системы.\n\
    /get_free - сбор информации о состоянии оперативной\n\
    памяти.\n\
    /get_mpstat - сбор информации о производительности\n\
    системы.\n\
    /get_w - сбор информации о работающих в данной системе\n\
    пользователях.\n\
    Сбор логов:\n\
    /get_auths -  последние 10 входов в систему.\n\
    /get_critical -  последние 5 критических события.\n\
    /get_ps - сбор информации о запущенных процессах.\n\
    /get_ss - сбор информации об используемых портах.\n\
    /get_apt_list - сбор информации об установленных пакетах.\n\
    /get_services -  сбор информации о запущенных сервисах.\n\
    /get_emails - вывод всех email\n\
    /get_phones - вывод всех phone\n\
    /get_repl_logs - вывод логов репликации'  
    )  
    

def VerifyPasswordCommand(update: Update, context):
    update.message.reply_text(f'Введите ваш пароль:')
    return 'VerifyPassword'
def find_email(update: Update, context):
    try:
        connection = psycopg2.connect(user=user1,
                                  password=password1,
                                  host=host1,
                                  port=port1, 
                                  database=db)
        

        cursor = connection.cursor()
        cursor.execute("select * from email;")
        connection.commit()
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                update.message.reply_text(str(row))  
            logging.info("Команда успешно выполнена")
        else:
            update.message.reply_text("Таблица email пуста")
            logging.info("Команда успешно выполнена")
    except Exception as error:
        logging.error(f'Ошибка при работе с PostgreSQL {error}')



def find_phone(update: Update, context):
    try:
        connection = psycopg2.connect(user=user1,
                                  password=password1,
                                  host=host1,
                                  port=port1, 
                                  database=db)
        update.message.reply_text('Подключение успешно')
        cursor = connection.cursor()
        cursor.execute("select * from phone;")
        connection.commit()
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                update.message.reply_text(str(row))  
            logging.info("Команда успешно выполнена")
        else:
            update.message.reply_text("Таблица email пуста")
            logging.info("Команда успешно выполнена")
    except Exception as error:
        logging.error(f'Ошибка при работе с PostgreSQL {error}')




INPUT_TEXT_EMAIL, CONFIRM_SAVE_EMAIL = range(2)
INPUT_TEXT_PHONE, CONFIRM_SAVE_PHONE = range(2)


def findemailaddresscommand(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f'Введите адрес электронной почты для поиска:')
    
    return INPUT_TEXT_EMAIL

def findemailaddress (update: Update, context: CallbackContext) -> int:
    user_input1 = update.message.text

    #email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_regex = re.compile(r'\b[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+)*' \
                r'@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')

    EmailList = email_regex.findall(user_input1)

    if not EmailList:
        update.message.reply_text('Почтовой адрес не найден :(')
        return ConversationHandler.END
    else:
        context.user_data['EmailList'] = EmailList
        email_addresses = '\n'.join(EmailList)
        update.message.reply_text(f'Найденные адреса электронной почты:\n{email_addresses}')
        update.message.reply_text(f'Хотите записать его в базу данных? (yes or not)')
        return CONFIRM_SAVE_EMAIL




    
def handle_confirmation(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "yes":
        print('Подключение успешно1')
        EmailList = context.user_data['EmailList']
        try:
            print('Подключение успешно2')
            connection = psycopg2.connect(user=user1,
                                          password=password1,
                                          host=host1,
                                          port=port1, 
                                          database=db)
            update.message.reply_text('Подключение успешно')
            cursor = connection.cursor()
            for email in EmailList:
                cursor.execute('INSERT INTO email (email) VALUES (%s) ON CONFLICT DO NOTHING', (email,))
            connection.commit()
            update.message.reply_text("Адреса успешно записаны в базу данных.")
            logging.info("Адреса успешно записаны в базу данных.")
        except Exception as error:
            logging.error(f'Ошибка при работе с PostgreSQL {error}')
            update.message.reply_text('Произошла ошибка при записи в базу данных.')
    if user_input.lower() == 'no':
        update.message.reply_text("Хорошо, адреса не будут записаны в базу данных.")
    if user_input.lower() != 'no' and user_input != 'yes':
         update.message.reply_text('Вы ввели недопустимый символ')
    return ConversationHandler.END






def VerifyPassword (update: Update, context):
    user_input2 = update.message.text
    passwordregex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')
    passresult = passwordregex.search(user_input2)
    if passresult != None:
        update.message.reply_text(f'Пароль сложный')
    else:
        update.message.reply_text(f'Пароль легкий')
    return ConversationHandler.END

def findPhoneNumbersCommand(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f'Введите текст для поиска телефонных номеров: ')

    return INPUT_TEXT_PHONE

def findPhoneNumbers (update: Update, context: CallbackContext) -> int:
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    
    
    phone_regex = re.compile(
        r'(?:\+7|8)\s?[-(]?\d{3}[-)\s]?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}')
       
    phone_list = phone_regex.findall(user_input)
    phone_numbers = '\n'.join(phone_list)
    if not phone_list: 
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    else: 
        context.user_data['phone_list'] = phone_list
        
        update.message.reply_text(f'Найденные адреса телефонных номеров:\n{phone_numbers}') 
        update.message.reply_text(f'Хотите записать их в базу данных? (yes or not)')
    return CONFIRM_SAVE_PHONE

def phone_confirm(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "yes":
        print('Подключение успешно1')
        phone_list = context.user_data['phone_list']
        try:
            print('Подключение успешно2')
            connection = psycopg2.connect(user=user1,
                                          password=password1,
                                          host=host1,
                                          port=port1, 
                                          database=db)
            update.message.reply_text('Подключение успешно')
            cursor = connection.cursor()
            for phone in phone_list:
                cursor.execute('INSERT INTO phone (phonenumber) VALUES (%s) ON CONFLICT DO NOTHING', (phone,))
            connection.commit()
            update.message.reply_text("Адреса успешно записаны в базу данных.")
            logging.info("Адреса успешно записаны в базу данных.")
        except Exception as error:
            logging.error(f'Ошибка при работе с PostgreSQL {error}')
            update.message.reply_text('Произошла ошибка при записи в базу данных.')
    if user_input.lower() == 'no':
        update.message.reply_text("Хорошо, адреса не будут записаны в базу данных.")
    if user_input.lower() != 'no' and user_input != 'yes':
         update.message.reply_text('Вы ввели недопустимый символ')
    
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)
def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            INPUT_TEXT_PHONE: [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            CONFIRM_SAVE_PHONE: [MessageHandler(Filters.text & ~Filters.command, phone_confirm)],
        },
        fallbacks=[]
    )
    convHandlerFindEmail = ConversationHandler(
      entry_points=[CommandHandler('find_email',findemailaddresscommand)],
      states={
        INPUT_TEXT_EMAIL: [MessageHandler(Filters.text & ~Filters.command, findemailaddress)],
        CONFIRM_SAVE_EMAIL: [MessageHandler(Filters.text & ~Filters.command, handle_confirmation)]
      },
      fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
      entry_points=[CommandHandler('verify_password',VerifyPasswordCommand)],
      states={
          'VerifyPassword': [MessageHandler(Filters.text & ~Filters.command, VerifyPassword)],
      },
      fallbacks=[]
    )
    convHandlerget_list = ConversationHandler(
      entry_points=[CommandHandler('get_apt_list',get_apt_listcommand)],
      states={
          'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
      },
      fallbacks=[]
    )
	
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler('get_release', release))
    dp.add_handler(CommandHandler('get_uname', uname))
    dp.add_handler(CommandHandler('get_uptime', uptime))
    dp.add_handler(CommandHandler('get_df', df))
    dp.add_handler(CommandHandler('get_free', free))
    dp.add_handler(CommandHandler('get_mpstat', mpstat))
    dp.add_handler(CommandHandler('get_w', get_w))
    dp.add_handler(CommandHandler('get_auths', get_auths))
    dp.add_handler(CommandHandler('get_critical', get_critical))
    dp.add_handler(CommandHandler('get_ps', get_ps))
    dp.add_handler(CommandHandler('get_ss', get_ss))
    dp.add_handler(convHandlerget_list)
    dp.add_handler(CommandHandler('get_services', get_services))
    dp.add_handler(CommandHandler('get_repl_logs', get_logs))
    dp.add_handler(CommandHandler('get_emails', find_email))
    dp.add_handler(CommandHandler('get_phones', find_phone))
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
