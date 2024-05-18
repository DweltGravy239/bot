import logging
import re
import paramiko
import os
from dotenv import load_dotenv
import psycopg2
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import subprocess


# Загрузка переменных окружения из .env файла
load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Настройка логирования
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для старта бота
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

# Функция для выполнения команды на удаленном сервере
def execute_command(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    client.close()
    
    return output, error

# Загрузка учетных данных для удаленного сервера из переменных окружения
host = os.environ.get("RM_HOST1")
port = os.environ.get("RM_PORT")
username = os.environ.get("RM_USER")
password = os.environ.get("RM_PASSWORD")

# Загрузка учетных данных для базы данных из переменных окружения
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_DATABASE")

# Функции для обработки различных команд
def release(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "lsb_release -a")
    update.message.reply_text(output)

def uname(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "uname -a")
    
def uptime(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "uptime")
    update.message.reply_text(output)

def df(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "df -h")
    update.message.reply_text(output)

def free(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "free -h")
    update.message.reply_text(output)

def mpstat(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "mpstat | head -n 5")
    update.message.reply_text(output)

def get_w(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "w -s")
    update.message.reply_text(output)

def get_auths(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "last -n 10 -R")
    update.message.reply_text(output)

def get_critical(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "journalctl -p crit -n 5")
    update.message.reply_text(output)

def get_ps(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "ps aux | head -n 5")
    update.message.reply_text(output)

def get_ss(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "ss -tulwn")
    update.message.reply_text(output)

def get_apt_listcommand(update: Update, context: CallbackContext):
    update.message.reply_text(f'Выберите вариант поиска:\n1. Введите = all, для вывода всех пакетов\n2. Введите название пакета')
    return 'get_apt_list'


def get_apt_list(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()
    if user_input.lower() == 'all':
        output = execute_command(host, port, username, password, "apt list | tail -n 10")
    else:
        command = f"apt list --installed | grep {user_input} | tail -n 10"
        output = execute_command(host, port, username, password, command)
    update.message.reply_text(output)

def search_package(update: Update, context: CallbackContext):
    user_input = update.message.text
    command = f"apt list {user_input}"
    output = execute_command(host, port, username, password, command)
    update.message.reply_text(output)

def get_services(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "systemctl list-units --type=service | head -n 5")
    update.message.reply_text(output)

def get_logs(update: Update, context: CallbackContext):
    output = execute_command(host, port, username, password, "cat /var/log/postgresql/postgresql-14-main.log | grep replication | head -10")
    update.message.reply_text(output)

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Список доступных команд:\n'
        '/find_email - поиск email адресов в тексте.\n'
        '/find_phone_number - поиск телефонных номеров в тексте.\n'
        '/verify_password - для проверки надежности пароля.\n'
        '/get_release - информация о релизе.\n'
        '/get_uname - информация об архитектуре процессора, имени хоста и версии ядра.\n'
        '/get_uptime - информация о времени работы.\n'
        '/get_df - информация о состоянии файловой системы.\n'
        '/get_free - информация о состоянии оперативной памяти.\n'
        '/get_mpstat - информация о производительности системы.\n'
        '/get_w - информация о работающих в системе пользователях.\n'
        '/get_auths - последние 10 входов в систему.\n'
        '/get_critical - последние 5 критических событий.\n'
        '/get_ps - информация о запущенных процессах.\n'
        '/get_ss - информация об используемых портах.\n'
        '/get_apt_list - информация об установленных пакетах.\n'
        '/get_services - информация о запущенных сервисах.\n'
        '/get_emails - вывод всех email адресов.\n'
        '/get_phones - вывод всех телефонных номеров.\n'
        '/get_repl_logs - вывод логов репликации.'
    )

def verify_password_command(update: Update, context: CallbackContext):
    update.message.reply_text(f'Введите ваш пароль:')
    return 'VerifyPassword'

def find_email(update: Update, context: CallbackContext):
    try:
        connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM email;")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                update.message.reply_text(str(row))
        else:
            update.message.reply_text("Таблица email пуста")
    except Exception as error:
        logging.error(f'Ошибка при работе с PostgreSQL {error}')

def find_phone(update: Update, context: CallbackContext):
    try:
        connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_name)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone;")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                update.message.reply_text(str(row))
        else:
            update.message.reply_text("Таблица phone пуста")
    except Exception as error:
        logging.error(f'Ошибка при работе с PostgreSQL {error}')

# Определение состояний для ConversationHandler
INPUT_TEXT_EMAIL, CONFIRM_SAVE_EMAIL = range(2)
INPUT_TEXT_PHONE, CONFIRM_SAVE_PHONE = range(2)

def find_email_address_command(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f'Введите адрес электронной почты для поиска:')
    return INPUT_TEXT_EMAIL


def find_email_address(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    email_list = email_regex.findall(user_input)
    email_list = list(set(email_list))
    if not email_list:
        update.message.reply_text('Почтовый адрес не найден :(')
        return ConversationHandler.END
    else:
        context.user_data['email_list'] = email_list
        email_addresses = '\n'.join(email_list)
        update.message.reply_text(f'Найденные адреса электронной почты:\n{email_addresses}')
        update.message.reply_text(f'Хотите записать его в базу данных? (yes или no)')
        return CONFIRM_SAVE_EMAIL

def handle_confirmation(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "yes":
        email_list = context.user_data['email_list']
        try:
            connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_name)
            cursor = connection.cursor()
            for email in email_list:
                cursor.execute('INSERT INTO email (email) VALUES (%s) ON CONFLICT DO NOTHING', (email,))
            connection.commit()
            update.message.reply_text("Адреса успешно записаны в базу данных.")
        except Exception as error:
            logging.error(f'Ошибка при работе с PostgreSQL {error}')
            update.message.reply_text('Произошла ошибка при записи в базу данных.')
    elif user_input.lower() == 'no':
        update.message.reply_text("Хорошо, адреса не будут записаны в базу данных.")
    else:
        update.message.reply_text('Вы ввели недопустимый символ')
    return ConversationHandler.END

def get_repl_logs(update: Update, context: CallbackContext):
    user = update.effective_user
    logging.info(f'Calling command /get_repl_logs - User:{user.full_name}')
    command = "cat /var/log/postgresql/postgresql.log | grep repl | tail -n 15"
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or res.stderr.decode():
        update.message.reply_text("Can not open log file!")
    else:
        update.message.reply_text(res.stdout.decode().strip('\n'))

def verify_password(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    password_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$')
    pass_result = password_regex.search(user_input)
    if pass_result:
        update.message.reply_text(f'Пароль сложный')
    else:
        update.message.reply_text(f'Пароль легкий')
    return ConversationHandler.END

def find_phone_numbers_command(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(f'Введите текст для поиска телефонных номеров: ')
    return INPUT_TEXT_PHONE


def find_phone_numbers(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    phone_regex = re.compile(r'(?<!\d)(?:\+7|8)[- ]?\d{3}[- ]?\d{3}[- ]?\d{2}[- ]?\d{2}(?!\d)')
    phone_list = phone_regex.findall(user_input)
    phone_list = list(set(phone_list))
    phone_numbers = '\n'.join(phone_list)
    if not phone_list:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    else:
        context.user_data['phone_list'] = phone_list
        update.message.reply_text(f'Найденные телефонные номера:\n{phone_numbers}')
        update.message.reply_text(f'Хотите записать их в базу данных? (yes или no)')
        return CONFIRM_SAVE_PHONE

def phone_confirm(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    if user_input.lower() == "yes":
        phone_list = context.user_data['phone_list']
        try:
            connection = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_name)
            cursor = connection.cursor()
            for phone in phone_list:
                cursor.execute('INSERT INTO phone (phonenumber) VALUES (%s) ON CONFLICT DO NOTHING', (phone,))
            connection.commit()
            update.message.reply_text("Телефонные номера успешно записаны в базу данных.")
        except Exception as error:
            logging.error(f'Ошибка при работе с PostgreSQL {error}')
            update.message.reply_text('Произошла ошибка при записи в базу данных.')
    elif user_input.lower() == 'no':
        update.message.reply_text("Хорошо, номера не будут записаны в базу данных.")
    else:
        update.message.reply_text('Вы ввели недопустимый символ')
    return ConversationHandler.END

def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Conversation handlers for various commands
    conv_handler_find_phone_numbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numbers_command)],
        states={
            INPUT_TEXT_PHONE: [MessageHandler(Filters.text & ~Filters.command, find_phone_numbers)],
            CONFIRM_SAVE_PHONE: [MessageHandler(Filters.text & ~Filters.command, phone_confirm)],
        },
        fallbacks=[]
    )

    conv_handler_find_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_address_command)],
        states={
            INPUT_TEXT_EMAIL: [MessageHandler(Filters.text & ~Filters.command, find_email_address)],
            CONFIRM_SAVE_EMAIL: [MessageHandler(Filters.text & ~Filters.command, handle_confirmation)]
        },
        fallbacks=[]
    )

    conv_handler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_command)],
        states={
            'VerifyPassword': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    conv_handler_get_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listcommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )


    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(conv_handler_find_phone_numbers)
    dp.add_handler(conv_handler_find_email)
    dp.add_handler(conv_handler_verify_password)
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
    dp.add_handler(conv_handler_get_list)
    dp.add_handler(CommandHandler('get_services', get_services))
    dp.add_handler(CommandHandler('get_repl_logs', get_logs))
    dp.add_handler(CommandHandler('get_emails', find_email))
    dp.add_handler(CommandHandler('get_phones', find_phone))

    # Register a handler for text messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
