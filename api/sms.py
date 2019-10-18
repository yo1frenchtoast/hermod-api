import ovh
import config
from dbdriver import select

config = config.get('ovh')

client = ovh.Client(
    endpoint='ovh-eu',
    application_key=config['application_key'],
    application_secret=config['application_secret'],
    consumer_key=config['consumer_key']
)

def send(dest, message):
    user = select('users', {'name': dest})[0]

    phone = user['phone']
    account = user['sms_account']

    result = client.post('/sms/'+account+'/jobs',
        message=message,
        receivers=[phone],
        senderForResponse=True
    )

    return result

