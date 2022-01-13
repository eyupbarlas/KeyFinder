import requests
from config import BOT_TOKEN, BOT_CHATID

#! For colored console outputs
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


#! Telegram Notification
def telegramNotificationSend(botMessage):
    bot_token = BOT_TOKEN  
    bot_chatID = BOT_CHATID
    sendMessage = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + \
                '&parse_mode=Markdown&text=' + botMessage

    requests.get(sendMessage)

#! Encryption stuff
# from passlib.hash import sha256_crypt
# x = sha256_crypt.encrypt("")
# print(x)


    