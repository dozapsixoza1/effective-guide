import telebot
from telebot import types

# Сюда вставляй токен от BotFather
TOKEN = '8325321626:AAF-3UDkhPrNWXCS2cOgfWDS9uDtNg0mNIE'
bot = telebot.TeleBot(TOKEN)

# Айдишники: твой и твоего кента (замени на реальные числа)
ADMIN_IDS = [7950038145, 8273405303]

# Словарь для запоминания, какому юзеру сейчас отвечает админ
admin_reply_state = {}

@bot.message_handler(commands=['start'])
def start_message(message):
    if message.chat.id in ADMIN_IDS:
        bot.send_message(message.chat.id, "Привет, админ! Бот запущен, ждём вопросы от пользователей.")
    else:
        # Приветствие для обычных юзеров
        bot.send_message(
            message.chat.id, 
            "Привет! Задай свой вопрос прямо сюда, и мы ответим в ближайшее время. 👇"
        )

# Обработка сообщений от обычных пользователей
@bot.message_handler(func=lambda message: message.chat.id not in ADMIN_IDS)
def handle_user_question(message):
    markup = types.InlineKeyboardMarkup()
    # В callback_data зашиваем ID юзера, чтобы знать, кому отправлять ответ
    btn = types.InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{message.chat.id}")
    markup.add(btn)

    user_info = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    # Отправляем вопрос всем админам
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(
                admin_id, 
                f"🔔 <b>Новый вопрос от {user_info} (ID: {message.chat.id}):</b>\n\n{message.text}", 
                parse_mode='HTML',
                reply_markup=markup
            )
        except Exception as e:
            pass # Если админ заблокировал бота, просто пропускаем
    
    bot.send_message(message.chat.id, "✅ Твой вопрос отправлен! Ожидай ответа.")

# Обработка нажатия на кнопку "Ответить" админом
@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def callback_reply(call):
    # Вытаскиваем ID пользователя из callback_data
    user_id = int(call.data.split("_")[1])
    
    # Запоминаем, что этот админ сейчас будет отвечать этому юзеру
    admin_reply_state[call.message.chat.id] = user_id
    
    msg = bot.send_message(
        call.message.chat.id, 
        "✍️ Напиши текст ответа, который нужно отправить пользователю:"
    )
    # Ждем следующее сообщение от админа и передаем его в функцию send_reply_to_user
    bot.register_next_step_handler(msg, send_reply_to_user)

# Функция отправки ответа пользователю
def send_reply_to_user(message):
    admin_id = message.chat.id
    
    if admin_id in admin_reply_state:
        user_id = admin_reply_state[admin_id]
        try:
            # Отправляем ответ пользователю
            bot.send_message(
                user_id, 
                f"📩 <b>Ответ от администрации:</b>\n\n{message.text}", 
                parse_mode='HTML'
            )
            bot.send_message(admin_id, "✅ Ответ успешно отправлен!")
        except Exception as e:
            bot.send_message(admin_id, f"❌ Ошибка при отправке (возможно, юзер заблокировал бота).")
        
        # Очищаем состояние после ответа
        del admin_reply_state[admin_id]
    else:
        bot.send_message(admin_id, "Что-то пошло не так. Попробуй нажать кнопку «Ответить» еще раз.")

# Запуск бота на постоянную работу
if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
