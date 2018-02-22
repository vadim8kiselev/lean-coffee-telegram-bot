# -*- coding: utf-8 -*-
import telebot.util
from telebot import types
import operator


# TODO: Please, move it to src folder

# Configuration ######################################################
bot = telebot.TeleBot('452287428:AAGZN3UERRMHScNzD6tK6IG9h_6AB_HXglY')

owner_id = ''
lean_coffee = {}
themes = set()
voting = False
######################################################################


@bot.message_handler(commands=['lean'])
def lean(message):
    global lean_coffee
    global themes
    global owner_id

    if not owner_id:
        lean_coffee = {}
        themes = set()

        owner_id = message.chat.id
        lean_coffee[str(owner_id)] = {}
        bot.send_message(message.chat.id, 'Lean has started, you are an owner')
    else:
        bot.send_message(message.chat.id, 'Lean session is already in progress')


@bot.message_handler(commands=['signup'])
def register(message):
    if owner_id:
        lean_coffee[str(message.chat.id)] = {}
        if voting:
            markup = types.ReplyKeyboardMarkup(row_width=1)

            for theme in sorted(themes):
                lean_coffee[str(message.chat.id)][theme] = False
                markup.add(types.KeyboardButton('Vote for: ' + theme))

            bot.send_message(message.chat.id, 'Vote started', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'You are registered for participation in lean coffee')
    else:
        bot.send_message(message.chat.id, 'Lean session is not started yet')


@bot.message_handler(commands=['up'])
def up_theme(message):
    global lean_coffee
    global themes
    global voting

    if owner_id:
        if not voting:
            chat_id = str(message.chat.id)
            if chat_id not in lean_coffee.keys():
                lean_coffee[chat_id] = {}

            theme = message.text.replace("/up", "").strip()
            if theme:
                themes.add(theme)
                bot.send_message(message.chat.id, 'You up theme "' + theme + '"')
            else:
                bot.send_message(message.chat.id, 'Upped theme cannot be empty')
        else:
            bot.send_message(message.chat.id, 'Vote is already in progress')
    else:
        bot.send_message(message.chat.id, 'Lean session is not started yet')


@bot.message_handler(commands=['down'])
def down_theme(message):
    global themes
    if owner_id:
        if not voting:
            theme = message.text.replace("/down", "").strip()
            if theme:
                themes.discard(theme)
                bot.send_message(message.chat.id,
                                 'You down theme "' + theme + '"')
            else:
                bot.send_message(message.chat.id, 'Downed theme cannot be empty')
        else:
            bot.send_message(message.chat.id, 'Vote is already in progress')
    else:
        bot.send_message(message.chat.id, 'Lean session is not started yet')


@bot.message_handler(commands=['vote'])
def vote(message):
    global lean_coffee
    global owner_id
    global voting
    if owner_id:
        if message.chat.id == owner_id:
            if not voting:
                if themes:
                    voting = True
                    markup = types.ReplyKeyboardMarkup(row_width=1)

                    for theme in sorted(themes):
                        for participant in lean_coffee.keys():
                            lean_coffee[participant][theme] = False
                        markup.add(types.KeyboardButton('Vote for: ' + theme))

                    for participant in lean_coffee.keys():
                        bot.send_message(participant, 'Vote started', reply_markup=markup)
                else:
                    bot.send_message(owner_id, 'There are no themes to vote')
            else:
                bot.send_message(owner_id, 'Vote is already in progress')
        else:
            bot.send_message(message.chat.id, 'Vote operation allowed for owner only')
    else:
        bot.send_message(message.chat.id, 'Lean session is not started yet')


@bot.message_handler(commands=['stop'])
def stop(message):
    global lean_coffee
    global themes
    global voting

    if owner_id:
        if message.chat.id == owner_id:
            if voting:
                voting = False

                results = {}
                for participant in lean_coffee:
                    for theme in lean_coffee[participant]:
                        if theme in results:
                            results[theme] += 1 if lean_coffee[participant][theme] else 0
                        else:
                            results[theme] = 1 if lean_coffee[participant][theme] else 0

                sorted_tuple = sorted(results.items(), key=operator.itemgetter(1), reverse=True)
                themes_result = '\n'.join([entry[0] + ' (' + str(entry[1]) + ')' for entry in sorted_tuple])

                themes = set()
                for participant in lean_coffee:
                    lean_coffee[participant] = {}

                markup = types.ReplyKeyboardRemove()
                for participant in lean_coffee.keys():
                    bot.send_message(participant, 'Vote stopped', reply_markup=markup)
                    bot.send_message(participant, 'Themes:\n' + themes_result)
            else:
                bot.send_message(owner_id, 'Vote is not started yet')
        else:
            bot.send_message(message.chat.id, 'Stop operation allowed for owner only')
    else:
        bot.send_message(message.chat.id, 'Lean session is not started yet')


@bot.message_handler(commands=['exit'])
def exit(message):
    global lean_coffee
    global owner_id
    global themes
    if owner_id:
        if message.chat.id == owner_id:
            for participant in lean_coffee.keys():
                bot.send_message(participant, 'Lean session has finished. Good bye :)')
            owner_id = ''
            lean_coffee = dict()
            themes = set()
        else:
            bot.send_message(message.chat.id, 'Exit operation allowed for owner only')
    else:
        bot.send_message(message.chat.id, 'Lean session is not started yet')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def text(message):
    if owner_id:
        vote_key = 'Vote for: '
        unvote_key = 'Unvote for: '

        if message.text.startswith(vote_key) or message.text.startswith(unvote_key):

            if message.text.startswith(vote_key):
                lean_coffee[str(message.chat.id)][message.text[len(vote_key):]] = True
            elif message.text.startswith(unvote_key):
                lean_coffee[str(message.chat.id)][message.text[len(unvote_key):]] = False

            votes = lean_coffee[str(message.chat.id)]

            markup = types.ReplyKeyboardMarkup(row_width=1)
            for theme in votes.keys():
                markup.add(types.KeyboardButton((unvote_key if votes[theme] else vote_key) + theme))

            bot.send_message(message.chat.id, 'Vote changed', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Lean session is not started yet')


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except BaseException:
        print 'Connection refused'
