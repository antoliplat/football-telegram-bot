from telegram import Update
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackContext
import logging

from const import GREETING_MESSAGE, HELP_MESSAGE
from models import User, Match

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(token='695761069:AAHRgeaFcrILV-N3PCgczJ-jP-vbKrzJcW4', use_context=True)
dispatcher = updater.dispatcher

gamers = []


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=GREETING_MESSAGE)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text='Я не понимаю эту команду')


def register(update: Update, context: CallbackContext):
    telegram_id = update.effective_user.id
    users_count = User.select().where(User.telegram_id == telegram_id).count()

    if users_count == 1:
        context.bot.send_message(chat_id=update.message.chat_id, text='Вы уже зарегистрированы')
    else:
        username = update.effective_user.username
        if username is None:
            username = update.effective_user.full_name
        user = User(username=username, telegram_id=telegram_id)
        user.save()
        context.bot.send_message(chat_id=update.message.chat_id, text='Готово!')


def ready(update: Update, context: CallbackContext):
    if len(gamers) == 2:
        context.bot.send_message(chat_id=update.message.chat_id, text='Игра уже идет...')
        return

    username = User.select().where(User.telegram_id == update.effective_user.id).get().username
    chat_id = update.message.chat_id
    user_id = User.select(User.id).where(User.telegram_id == update.effective_user.id).get().id

    if len(gamers) == 1 and gamers[0]['user_id'] == user_id:
        context.bot.send_message(chat_id=gamers[0]['chat_id'], text='Вы уже подключились к игре.')
        return

    user = {'username': username, 'chat_id': chat_id, 'user_id': user_id}
    gamers.append(user)

    if len(gamers) == 1:
        context.bot.send_message(chat_id=update.message.chat_id, text='Ожидаем противника...')

    if len(gamers) == 2:
        match_players = f'Игра началась.\n{gamers[0]["username"]} - {gamers[1]["username"]}'
        context.bot.send_message(chat_id=gamers[0]['chat_id'], text=match_players)
        context.bot.send_message(chat_id=gamers[1]['chat_id'], text=match_players)


def name(update: Update, context: CallbackContext):
    user = User.select().where(User.telegram_id == update.effective_user.id).get()
    if update.message.text == '/name':
        context.bot.send_message(chat_id=update.message.chat_id, text=user.username)
        return
    new_name = update.message.text.replace('/name ', '')
    user.username = new_name
    user.save()
    context.bot.send_message(chat_id=update.message.chat_id, text=f'Теперь вы будете известны как {new_name}')


def status(update: Update, context: CallbackContext):
    if len(gamers) == 0:
        context.bot.send_message(chat_id=update.message.chat_id, text='Стол свободен!')
    elif len(gamers) == 1:
        context.bot.send_message(chat_id=update.message.chat_id, text=f'{gamers[0]["username"]} ожидает противника')
    elif len(gamers) == 2:
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=f'Стол занят.\nИграют: {gamers[0]["username"]} - {gamers[1]["username"]}')


def score(update: Update, context: CallbackContext, args):
    if len(gamers) == 1:
        context.bot.send_message(chat_id=update.message.chat_id, text='Вы еще не сыграли игру.')
    s: int
    try:
        s = int(update.message.text.replace('/score', ''))
    except ValueError:
        context.bot.send_message(chat_id=update.message.chat_id, text='Неверный формат')
        return
    if s < 0:
        context.bot.send_message(chat_id=update.message.chat_id, text='Количество очков должно быть больше 0.')
    if s > 10:
        context.bot.send_message(chat_id=update.message.chat_id, text='Количество очков должно быть меньше 10.')
    user_id = User.select().where(User.telegram_id == update.effective_user.id).get().id
    user = list(filter(lambda u: u['user_id'] == user_id, gamers))[0]

    if gamers[0].get('score') is not None and gamers[1].get('score') is not None:
        match = Match(first_opponent_user_id=gamers[0]['user_id'], second_opponent_user_id=gamers[1]['user_id'],
                      first_opponent_score=gamers[0]['score'], second_opponent_score=gamers[1]['score'])
        match.save()
        gamers.clear()


def command_info(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text=HELP_MESSAGE)


def error(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text='Произошла ошибка обратитесь к логам')


start_handler = CommandHandler('start', start)
register_handler = CommandHandler('register', register)
unknown_handler = MessageHandler(Filters.command, unknown)
ready_handler = CommandHandler('ready', ready)
name_handler = CommandHandler('name', name)
score_handler = CommandHandler('score', score, pass_args=True)
status_handler = CommandHandler('status', status)
help_handler = CommandHandler('help', command_info)
error_handler = MessageHandler(Filters.all, error)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(ready_handler)
dispatcher.add_handler(name_handler)
dispatcher.add_handler(score_handler)
dispatcher.add_handler(status_handler)
dispatcher.add_handler(help_handler)

dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(unknown_handler)
updater.start_polling()
