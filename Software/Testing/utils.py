import requests
from config import BOT_TOKEN, BOT_CHATID

#! Telegram Notification
def telegramNotificationSend(botMessage):
    bot_token = BOT_TOKEN  
    bot_chatID = BOT_CHATID
    sendMessage = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + \
                '&parse_mode=Markdown&text=' + botMessage

    requests.get(sendMessage)

#! Encryption stuff
# x = sha256_crypt.encrypt("1234")
# print(x)
    