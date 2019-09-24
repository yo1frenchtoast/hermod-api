FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ENV API_HOST="0.0.0.0" \
  API_PORT="9090" \
  API_URL="hermod.api.domain.tld" \
  API_PROTOCOL="http" \
  API_LOG_FILE="hermod-api.log" \
  DB_HOST="db" \
  DB_PORT="3306" \
  DB_DATABASE="hermod_api" \
  DB_USER="hermod" \
  DB_PASSWORD="hermod_password" \
  REDIS_HOST="redis" \
  REDIS_PORT="6379" \
  REDIS_PASSWORD="" \
  SMTP_SERVER="smtp.domain.tld" \
  SMTP_PORT="587" \
  SMTP_USE_TLS="yes" \
  SMTP_USER="user@domain.tld" \
  SMTP_PASSWORD="smtp_password" \
  OVH_ENDPOINT="ovh-eu" \
  OVH_APPLICATION_KEY="" \
  OVH_APPLICATION_SECRET="" \
  OVH_CONSUMER_KEY=""

COPY . .

WORKDIR ./api
CMD [ "python", "api.py" ]
