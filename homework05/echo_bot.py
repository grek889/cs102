import telebot
from telebot import apihelper


access_token = '809458576:AAGWdbBqryUxEqAFra7r64s4W3DlY005uzk'
apihelper.proxy = {'https': 'https://54.37.131.235:3128'}

bot = telebot.TeleBot(access_token)

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.polling()

