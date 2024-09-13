import telebot #fix dependence
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

def generate_markup(mode):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    if mode == "main":
        markup.add("Начать игру", "Добавить слова", "Помощь", "Об авторе")
    elif mode == "game":
        markup.add("Выйти из игры", "Я был(а) прав(а)")
    elif mode == "adding_words":
        markup.add("Остановить добавление слов")
    return markup

def start_game(chat_id):
    if chat_id in adding_words_mode:
        bot.send_message(chat_id, "Для начала игры выйдите из режима добавления слов.")
        return
    game_mode[chat_id] = True
    user_score[chat_id] = 0
    bot.send_message(chat_id, "Игра началась!", reply_markup=generate_markup("game"))
    send_word(chat_id)
    
def send_help(chat_id):
    bot.send_message(chat_id, "<i>Чтобы начать игру, нажмите кнопку 'Начать игру'. Бот начнет отправлять вам слова на испанском языке, а ваша задача - написать перевод этого слова на русский. За каждый правильный ответ вы получаете 1 балл, а за каждый неправильный - теряете 1 балл. Если вы считаете, что бот несправедливо не засчитал ваш правильный ответ, нажмите кнопку 'Я был(а) прав(а)'. Чтобы закончить игру, нажмите кнопку 'Выйти из игры'. Если вы хотите добавить слова в словарь, нажмите кнопку 'Добавить слова' и введите слова с их переводом через дефис. Чтобы прекратить добавление слов, нажмите кнопку 'Остановить добавление слов'.</i>", parse_mode='HTML', reply_markup=generate_markup("main"))
    
def send_author(chat_id):
    bot.send_message(chat_id, "<i>Автор бота Елена Маркеева, создан с любовью к испанскому языку</i>", parse_mode='HTML', reply_markup=generate_markup("main"))

def stop_game(chat_id):
    if chat_id in game_mode:
        del game_mode[chat_id]
        score = user_score[chat_id]
        del user_score[chat_id]
        bot.send_message(chat_id, f"<b>Игра окончена! Ваш счет: {score}</b>", parse_mode='HTML', reply_markup=generate_markup("main"))
    else:
        bot.send_message(chat_id, "Игра не была начата. Используйте /start_game, чтобы начать.", reply_markup=generate_markup("main"))

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
        bot.send_message(chat_id, "Для добавления слов выйдите из режима игры.")
        return
    adding_words_mode[chat_id] = True
    bot.send_message(chat_id, "Введите слово на испанском и его перевод на русском через дефис (например: casa-дом). Для выхода из режима добавления слов нажмите кнопку 'Остановить добавление слов'.", reply_markup=generate_markup("adding_words"))

def send_word(chat_id):
    word = random.choice(list(dictionary.keys()))
    last_word[chat_id] = word
    bot.send_message(chat_id, f"Переведите {last_word[chat_id]}")
    return word

def stop_adding_words(chat_id):
    if chat_id in adding_words_mode:
        del adding_words_mode[chat_id]
        bot.send_message(chat_id, "Вы вышли из режима добавления слов. Ваши слова сохранены для следующих сессий.", reply_markup=generate_markup("main"))
    else:
        bot.send_message(chat_id, "Вы не находитесь в режиме добавления слов. Нажмите кнопку 'Добавить слова', чтобы начать добавление слов.", reply_markup=generate_markup("main"))

def handle_correct_answer(chat_id):
    if chat_id not in game_mode:
        bot.send_message(chat_id, "Игра не была начата. Используйте /start_game, чтобы начать.", reply_markup=generate_markup("main"))
        return

    if chat_id in user_was_wrong and user_was_wrong[chat_id] and chat_id in user_score:
        user_score[chat_id] += 2
        bot.send_message(chat_id, f"Прошу прощения, вы были правы. Теперь ваш счет: {user_score[chat_id]}", reply_markup=generate_markup("game"))
        bot.send_message(chat_id, f"Переведите {last_word[chat_id]}", reply_markup=generate_markup("game"))
        user_was_wrong[chat_id] = False
    elif chat_id in user_score:
        user_score[chat_id] -= 1
        bot.send_message(chat_id, f"Не пытайтесь меня обмануть, вы не совершили ошибку. Минус балл. Теперь ваш счет: {user_score[chat_id]}", reply_markup=generate_markup("game"))
        bot.send_message(chat_id, f"Переведите {last_word[chat_id]}", reply_markup=generate_markup("game"))

bot.polling(none_stop=True, interval=0)
