# -*- coding: utf-8 -*-
import telebot
import random
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

bot = telebot.TeleBot('5899505119:AAGQNIq6GX67ksEDgR-6WcE4sPEIuAzjyxQ')

user_was_wrong = {}
last_word = {}
game_mode = {}
user_score = {}
dictionary = {}

with open("Dictionary2.txt", "r", encoding="utf-8") as file:
    for line in file:
        eng_word, rus_word = line.strip().split('-')
        dictionary[eng_word.strip()] = rus_word.strip()

@bot.message_handler(commands=['start_game'])
def start_game(message):
    chat_id = message.chat.id
    game_mode[chat_id] = True
    user_score[chat_id] = 0
    bot.send_message(chat_id, "Игра началась!")
    send_word(chat_id)

@bot.message_handler(commands=['stop_game'])
def stop_game(message):
    chat_id = message.chat.id
    if chat_id in game_mode:
        del game_mode[chat_id]
        score = user_score[chat_id]
        del user_score[chat_id]

        bot.send_message(chat_id, f"<b>Игра окончена! Ваш счет: {score}</b>", parse_mode='HTML')
    else:
        bot.send_message(chat_id, "Игра не была начата. Используйте /start_game, чтобы начать.")

def send_word(chat_id):
    word = random.choice(list(dictionary.keys()))
    last_word[chat_id] = word
    bot.send_message(chat_id, f"Переведите {last_word[chat_id]}")
    return word

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.chat.id
    user_input = message.text.strip()
    parsed = button_handler(message)
    if chat_id in game_mode and not parsed:
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
    if chat_id not in game_mode and not parsed:
        if message.text.lower() == "/help":
            bot.send_message(chat_id, "<i>Для старта игры введите команду /start_game или нажмите кнопку 'Начать игру' Бот начнет присылать вам слова на испанском, в ответе вам нужно написать перевод этого слова на русский. В случае если вы бот несправедливо не зачел вам перевод, нажмите кнопку 'Я был(а) прав(а)' Для выхода из игры введите команду /stop_game или нажмите кнопку 'Выйти из игры'</i>", parse_mode='HTML', reply_markup=generate_markup())
        else:
            bot.send_message(chat_id, "Я вас не понимаю. Напишите /help.")

def generate_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.add("Начать игру")
    markup.add("Выйти из игры")
    markup.add("Я был(а) прав(а)")
    markup.add("Помощь")
    markup.add("Об авторе")
    return markup

def button_handler(message):
    chat_id = message.chat.id

    if message.text == "Начать игру":
        start_game(message)
        return True
    elif message.text == "Выйти из игры":
        stop_game(message)
        return True
    elif message.text == "Я был(а) прав(а)":
        if chat_id not in game_mode:
            bot.send_message(chat_id, "Игра не была начата. Используйте /start_game, чтобы начать.")
            return True            
        if chat_id in user_was_wrong and user_was_wrong[chat_id] and chat_id in user_score:
            user_score[chat_id] += 2
            bot.send_message(chat_id, f"Прошу прощения, вы были правы. Теперь ваш счет: {user_score[chat_id]}")
            bot.send_message(chat_id, f"Переведите {last_word[chat_id]}")
            user_was_wrong[chat_id] = False
        elif chat_id in user_score:
            user_score[chat_id] -= 1
            bot.send_message(chat_id, f"Не пытайтесь меня обмануть. Минус балл. Теперь ваш счет: {user_score[chat_id]}")
            bot.send_message(chat_id, f"Переведите {last_word[chat_id]}")
        return True
    elif message.text == "Помощь":
        bot.send_message(chat_id, "<i>Для старта игры введите команду /start_game или нажмите кнопку 'Начать игру'. Бот начнет присылать вам слова на испанском, в ответе вам нужно написать перевод этого слова на русский. При правильном ответе вам начисляется 1 очко, при неправильном отнимается. В случае если бот несправедливо не зачел вам перевод, нажмите кнопку 'Я был(а) прав(а)' Для выхода из игры введите команду /stop_game или нажмите кнопку 'Выйти из игры'</i>", parse_mode='HTML', reply_markup=generate_markup())
        return True
    elif message.text == "Об авторе":
        bot.send_message(chat_id, "<i>Автор бота Елена Маркеева, создан с любовью к испанскому языку</i>", parse_mode='HTML')
        return True

bot.polling(none_stop=True, interval=0)
