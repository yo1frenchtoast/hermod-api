import urllib.parse
import requests
from dbdriver import select

def send(dest, message):
    user = select('users', {'name': dest})[0]

    token = user['telegrambot_token']
    chatid = user['telegrambot_chatid']

    url = 'https://api.telegram.org/bot'+token+'/sendMessage?chat_id='+str(chatid)+'&text='+urllib.parse.quote(message)

    try:
        result = requests.get(url)
        return result.status_code, None
    except requests.exceptions.RequestException as e:
        print (e)
        return None, e
