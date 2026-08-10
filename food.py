import os

import telebot
import schedule
import threading
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


load_dotenv()

# ====== Налаштування ======
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
FORM_FILE = os.getenv("FORM_URL")
DEFAULT_REMIND_HOURS = 3  # Автоматичне нагадування через 3 години

bot = telebot.TeleBot(TOKEN)

# ====== Стани користувачів ======
user_ids = set()
user_status = {}          # True = заповнив, False = не заповнив
manual_remind = {}        # {chat_id: datetime наступного нагадування}

# ====== Надсилання форми ======
def send_weekly_form(chat_id):
    user_status[chat_id] = False
    if chat_id in manual_remind:
        del manual_remind[chat_id]

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✔ Заповнив(ла)", callback_data="done"),
        InlineKeyboardButton("⏰ Нагадати пізніше", callback_data="remind")
    )

    bot.send_message(
        chat_id,
        f"Привіт! 👋\nБудь ласка, заповніть меню на тиждень.\n"
        f"Термін заповнення: до неділі 14:00\n"
        f"➡ Посилання на форму: {FORM_FILE}",
        reply_markup=markup
    )

# ====== Старт ======
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_ids.add(chat_id)
    if chat_id not in user_status:
        user_status[chat_id] = False

    if chat_id != ADMIN_ID:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("✔ Заповнив(ла)"), KeyboardButton("⏰ Нагадати пізніше"))
        bot.send_message(chat_id,
                         "Привіт! Я буду надсилати форму щоп’ятниці о 17:00 😊",
                         reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✏ Змінити меню", callback_data="change_form"))
        bot.send_message(chat_id, "Привіт, сонечко! Можеш змінити меню:", reply_markup=markup)

# ====== Обробка ReplyKeyboard ======
@bot.message_handler(func=lambda msg: msg.text in ["✔ Заповнив(ла)", "⏰ Нагадати пізніше"])
def handle_buttons(message):
    chat_id = message.chat.id
    remove_markup = ReplyKeyboardRemove()

    if message.text == "✔ Заповнив(ла)":
        user_status[chat_id] = True
        stop_reminders(chat_id)
        bot.send_message(chat_id, "Дякую! ❤️ Гарного дня!", reply_markup=remove_markup)

    elif message.text == "⏰ Нагадати пізніше":
        send_time_choice(chat_id)

# ====== Вибір часу нагадування ======
def send_time_choice(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("30 хв", callback_data="remind_30"),
        InlineKeyboardButton("1 година", callback_data="remind_60"),
        InlineKeyboardButton("2 години", callback_data="remind_120")
    )
    bot.send_message(chat_id, "Через скільки нагадати?", reply_markup=markup)
    # Автоматичне нагадування через 3 години, якщо користувач нічого не обрав
    manual_remind[chat_id] = datetime.now() + timedelta(hours=DEFAULT_REMIND_HOURS)

# ====== Callback inline кнопок ======
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "done":
        user_status[chat_id] = True
        stop_reminders(chat_id)
        bot.answer_callback_query(call.id, "Дякуємо! ❤️")
        bot.send_message(chat_id, "Дякую! Гарного дня!")

    elif call.data == "remind":
        send_time_choice(chat_id)
        bot.answer_callback_query(call.id)

    elif call.data.startswith("remind_"):
        minutes = int(call.data.split("_")[1])
        manual_remind[chat_id] = datetime.now() + timedelta(minutes=minutes)
        bot.answer_callback_query(call.id, f"Добре! Нагадування через {minutes} хв. ⏰")

    elif call.data == "change_form" and chat_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        bot.send_message(ADMIN_ID, "Введи нове посилання на форму:")
        bot.register_next_step_handler(call.message, save_new_form)
    elif call.data == "change_form":
        bot.answer_callback_query(call.id, "⛔ Немає прав")

# ====== Збереження нового меню ======
def save_new_form(message):
    global FORM_FILE
    if message.chat.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Ти не адмін.")
        return
    FORM_FILE = message.text.strip()
    bot.reply_to(message, f"✅ Меню оновлено!\n{FORM_FILE}")

# ====== Перевірка нагадувань ======
def check_manual_reminders():
    now = datetime.now()
    for chat_id, remind_time in list(manual_remind.items()):
        if now >= remind_time:
            if not user_status.get(chat_id, False):
                bot.send_message(chat_id,
                                 f"⏰ Нагадування! Ви ще не заповнили меню.\n➡ {FORM_FILE}")
                # повтор через 3 години
                manual_remind[chat_id] = now + timedelta(hours=3)
            else:
                del manual_remind[chat_id]

def stop_reminders(chat_id):
    if chat_id in manual_remind:
        del manual_remind[chat_id]

# ====== Потік для перевірки нагадувань ======
def reminder_runner():
    while True:
        check_manual_reminders()
        time.sleep(60)  # перевірка кожну хвилину

threading.Thread(target=reminder_runner, daemon=True).start()

# ====== Розсилка і адміністраторські нагадування ======
def friday_send_parents():
    for chat_id in user_ids:
        if chat_id != ADMIN_ID:
            send_weekly_form(chat_id)

def friday_reminder_admin():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✏ Змінити меню", callback_data="change_form"))
    bot.send_message(ADMIN_ID, "П’ятниця 10:00! Час зробити меню на тиждень:", reply_markup=markup)

def sunday_summary_admin():
    not_done = [str(uid) for uid, done in user_status.items() if not done and uid != ADMIN_ID]
    if not_done:
        bot.send_message(ADMIN_ID, f"Підсумок: ці користувачі не заповнили форму:\n{', '.join(not_done)}")
    else:
        bot.send_message(ADMIN_ID, "Всі батьки заповнили форму ✅")

# ====== Розклад ======
schedule.every().friday.at("10:00").do(friday_reminder_admin)
schedule.every().friday.at("17:00").do(friday_send_parents)
schedule.every().sunday.at("14:00").do(sunday_summary_admin)

def schedule_runner():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=schedule_runner, daemon=True).start()

print("✅ Бот працює...")
bot.polling()
