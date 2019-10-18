import os

def get(type):
    config = {
        "api": {
            "host": os.environ['API_HOST'],
            "port": os.environ['API_PORT'],
            "url": os.environ['API_URL'],
            "protocol": os.environ['API_PROTOCOL'],
            "log_file": os.environ['API_LOG_FILE']
        },
        "db": {
            "host": os.environ['DB_HOST'],
            "port": os.environ['DB_PORT'],
            "database": os.environ['DB_DATABASE'],
            "user": os.environ['DB_USER'],
            "password": os.environ['DB_PASSWORD']
        },
        "redis": {
            "host": os.environ['REDIS_HOST'],
            "port": os.environ['REDIS_PORT'],
            "password": os.environ['REDIS_PASSWORD']
        },
        "smtp": {
            "server": os.environ['SMTP_SERVER'],
            "port": os.environ['SMTP_PORT'],
            "use_tls": os.environ['SMTP_USE_TLS'],
            "user": os.environ['SMTP_USER'],
            "password": os.environ['SMTP_PASSWORD']
        },
        "ovh": {
            "endpoint": os.environ['OVH_ENDPOINT'],
            "application_key": os.environ['OVH_APPLICATION_KEY'],
            "application_secret": os.environ['OVH_APPLICATION_SECRET'],
            "consumer_key": os.environ['OVH_CONSUMER_KEY']
        }
    }

    if type is not None:
        return config[type]

    return config
