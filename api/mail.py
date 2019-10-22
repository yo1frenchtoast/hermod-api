import config
import smtplib
from dbdriver import select

config = config.get('smtp')

server = smtplib.SMTP(config['server'], int(config['port']))
server.ehlo()

if config['use_tls'] == 'yes':
    server.starttls()
server.login(config['user'], config['password'])

def send(dest, message):
    user = select('users', {'name': dest})[0]

    email = user['email']

    message = "Subject : {}\n\n".format(message)

    try:
        result = server.sendmail(config['user'], email, message)
        return result, None
    except smtplib.SMTPException as e:
        print (e)
        return None, e
    finally:
        server.close()
