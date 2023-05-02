import telebot
import random
from telebot.types import ReplyKeyboardMarkup

bot = telebot.TeleBot('5899505119:AAGQNIq6GX67ksEDgR-6WcE4sPEIuAzjyxQ')

user_was_wrong = {}
last_word = {}
game_mode = {}
user_score = {}
dictionary = {}
adding_words_mode = {}

with open("Dictionary.txt", "r", encoding="utf-8") as file:
    for line in file:
        esp_word, rus_word = line.strip().split('-')
        dictionary[esp_word.strip()] = rus_word.strip()

def generate_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("Начать игру")
    markup.add("Выйти из игры")
    markup.add("Я был(а) прав(а)")
    markup.add("Добавить слова")
    markup.add("Остановить добавление слов")
    markup.add("Помощь")
    markup.add("Об авторе")
    return markup

def start_game(chat_id):
    if chat_id in adding_words_mode:
        bot.send_message(chat_id, "Для начала игры выйдите из режима добавления слов.")
        return
    game_mode[chat_id] = True
    user_score[chat_id] = 0
    bot.send_message(chat_id, "Игра началась!", reply_markup=generate_markup())
    send_word(chat_id)
    
def send_help(chat_id):
    bot.send_message(chat_id, "<i>Для старта игры нажмите кнопку 'Начать игру'. Бот начнет присылать вам слова на испанском, в ответе вам нужно написать перевод этого слова на русский. При правильном ответе вам начисляется 1 очко, при неправильном отнимается. В случае если бот несправедливо не зачел вам перевод, нажмите кнопку 'Я был(а) прав(а)'. Для выхода из игры нажмите кнопку 'Выйти из игры'. Для добавления слов в словарь нажмите кнопку 'Добавить слова' и введите слова с переводом через дефис. Чтобы остановить добавление слов, нажмите кнопку 'Остановить добавление слов'.</i>", parse_mode='HTML', reply_markup=generate_markup())
    
def send_author(chat_id):
    bot.send_message(chat_id, "<i>Автор бота Елена Маркеева, создан с любовью к испанскому языку</i>", parse_mode='HTML', reply_markup=generate_markup())

def stop_game(chat_id):
    if chat_id in game_mode:
        del game_mode[chat_id]
        score = user_score[chat_id]
        del user_score[chat_id]
        bot.send_message(chat_id, f"<b>Игра окончена! Ваш счет: {score}</b>", parse_mode='HTML', reply_markup=generate_markup())
    else:
        bot.send_message(chat_id, "Игра не была начата. Используйте /start_game, чтобы начать.", reply_markup=generate_markup())

@bot.message_handler(content_types=['text'], func=lambda message: True)
def get_text_messages(message):
    chat_id = message.chat.id
    parsed = False
    user_input = message.text.strip()
    
    if user_input.startswith('/'):
        parsed = True
        command = user_input[1:]

        if command == 'help':
            send_help(chat_id)
        elif command == 'author':
            send_author(chat_id)        
        elif command == 'start_game':
            start_game(chat_id)
    else:
       parsed = button_handler(chat_id, user_input)        
    if not parsed and chat_id in game_mode:
        parsed = True
        if user_input.lower() == dictionary[last_word[chat_id]]:
            user_score[chat_id] += 1
            user_was_wrong[chat_id] = False
            bot.send_message(chat_id, f"Правильно! +1 очко. Теперь ваш счет: {user_score[chat_id]}")
            send_word(chat_id)
        else:
            user_score[chat_id] -= 1
            user_was_wrong[chat_id] = True
            bot.send_message(chat_id, f"Неправильно! Правильный перевод: {dictionary[last_word[chat_id]]}. -1 очко. Теперь ваш счет: {user_score[chat_id]}")
            send_word(chat_id)
    elif chat_id in adding_words_mode:
        parsed = True
        handle_adding_words(chat_id, user_input)
    if not parsed:
        bot.send_message(chat_id, "Я вас не понимаю. Напишите /help.")

def handle_adding_words(chat_id, user_input):
    try:
        esp_word, rus_word = user_input.split('-')
        esp_word = esp_word.strip().lower()
        rus_word = rus_word.strip().lower()

        if esp_word in dictionary:
            bot.send_message(chat_id, f"Слово '{esp_word}' уже есть в словаре с переводом '{dictionary[esp_word]}'.")
        else:
            dictionary[esp_word] = rus_word

            with open("Dictionary.txt", "a", encoding="utf-8") as file:
                file.write(f"{esp_word} - {rus_word}\n")

            bot.send_message(chat_id, f"Слово '{esp_word}' и его перевод '{rus_word}' были добавлены в словарь.")
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите слово на испанском и его перевод на русском через дефис (например: casa-дом).")

def button_handler(chat_id, user_input):
    if user_input == "Начать игру":
        start_game(chat_id)
    elif user_input == "Выйти из игры":
        stop_game(chat_id)
    elif user_input == "Я был(а) прав(а)":
        handle_correct_answer(chat_id)
    elif user_input == "Добавить слова":
        start_adding_words(chat_id)
    elif user_input == "Остановить добавление слов":
        stop_adding_words(chat_id)
    elif user_input == "Помощь":
        send_help(chat_id)
    elif user_input == "Об авторе":
        send_author(chat_id)
    else:
        return False
    return True

def start_adding_words(chat_id):
    if chat_id in game_mode:
        bot.send_message(chat_id, "Добавление слов невозможно в режиме игры.")
        return
    adding_words_mode[chat_id] = True
    bot.send_message(chat_id, "Введите слово на испанском и его перевод на русском через дефис (например: casa-дом). Для выхода из режима добавления слов нажмите кнопку 'Остановить добавление слов'.", reply_markup=generate_markup())

def send_word(chat_id):
    word = random.choice(list(dictionary.keys()))
    last_word[chat_id] = word
    bot.send_message(chat_id, f"Переведите {last_word[chat_id]}")
    return word

def stop_adding_words(chat_id):
    if chat_id in adding_words_mode:
        del adding_words_mode[chat_id]
        bot.send_message(chat_id, "Вы вышли из режима добавления слов. Ваши слова сохранены для следующих сессий.", reply_markup=generate_markup())
    else:
        bot.send_message(chat_id, "Вы не находитесь в режиме добавления слов. Нажмите кнопку 'Добавить слова', чтобы начать добавление слов.", reply_markup=generate_markup())

def handle_correct_answer(chat_id):
    if chat_id not in game_mode:
        bot.send_message(chat_id, "Игра не была начата. Используйте /start_game, чтобы начать.", reply_markup=generate_markup())
        return

    if chat_id in user_was_wrong and user_was_wrong[chat_id] and chat_id in user_score:
        user_score[chat_id] += 2
        bot.send_message(chat_id, f"Прошу прощения, вы были правы. Теперь ваш счет: {user_score[chat_id]}", reply_markup=generate_markup())
        bot.send_message(chat_id, f"Переведите {last_word[chat_id]}", reply_markup=generate_markup())
        user_was_wrong[chat_id] = False
    elif chat_id in user_score:
        user_score[chat_id] -= 1
        bot.send_message(chat_id, f"Не пытайтесь меня обмануть. Минус балл. Теперь ваш счет: {user_score[chat_id]}", reply_markup=generate_markup())
        bot.send_message(chat_id, f"Переведите {last_word[chat_id]}", reply_markup=generate_markup())

bot.polling(none_stop=True, interval=0)
