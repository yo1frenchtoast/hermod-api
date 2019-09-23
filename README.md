# HERMOD : Monitoring notification API for RouterOS

Monitoring actions for RouterOS netwatch

https://en.wikipedia.org/wiki/Herm%C3%B3%C3%B0r
`Hermóðr the Brave (Old Norse "war-spirit";[1] anglicized as Hermod) is a figure in Norse mythology, a son of the god Odin. He is often considered the messenger of the gods.`

## Getting started

### Docker-compose

### Before you begin

You need to :
- setup OVH API
- setup env config file

#### OVH SMS : API configuration

Please follow python-ovh documentation to get config variables : https://github.com/ovh/python-ovh/blob/master/README.rst

#### API Configuration

NOTE : DB and REDIS hosts are based on docker-compose services names (docker internal DNS names)

.env file sample
```
API_HOST=0.0.0.0
API_PORT=9090
API_URL=hermod.api.domain.tld
API_PROTOCOL=http
API_LOG_FILE=hermod-api.log

DB_HOST=db
DB_PORT=3306
DB_DATABASE=hermod_api
DB_USER=hermod
DB_PASSWORD=hermod_password

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

SMTP_SERVER=smtp.domain.tld
SMTP_PORT=587
SMTP_USE_TLS=yes
SMTP_USER=user@domain.tld
SMTP_PASSWORD=smtp_password

OVH_ENDPOINT=ovh-eu
OVH_APPLICATION_KEY=
OVH_APPLICATION_SECRET=
OVH_CONSUMER_KEY=
```
#### Build and run

```
docker-compose up --build -d
```

### Database table definitions

Initialization is done by docker-compose, init file provided in db/init.sql

#### Users
```
CREATE TABLE users(
    name    TEXT UNIQUE NOT NULL,
    email   TEXT NOT NULL,
    phone   TEXT NOT NULL,
    sms_account     TEXT,
    telegrambot_token   TEXT,
    telegrambot_chatid  TEXT
);
```

#### Routers
```
CREATE TABLE routers(
    name        TEXT UNIQUE NOT NULL,
    loopback    TEXT NOT NULL,
    uptime      TEXT,
    architecture    TEXT,
    version         TEXT,
    last_seen       TEXT
);
```

#### Hosts
```
CREATE TABLE hosts(
    name    TEXT UNIQUE NOT NULL,
    address TEXT NOT NULL,
    status      TEXT,
    last_down   TEXT,
    last_up     TEXT,
    duration    TEXT,
    witness     TEXT
);
```

### HTTP call examples

#### GET
Get json of requested entity

- list of all routers:

```
curl http://127.0.0.1:9090/router
```

- specific user:

```
curl http://127.0.01:9090/user/admin
```

#### POST
Add new entity

- add new router:

```
curl -X POST -d "loopback=10.0.10.1" http://127.0.0.1:9090/router/test1
```

#### PUT
Modiy existing entity

- set phone and email address on user:

```
curl -X PUT -d "phone='+336684684984'&email=test@test.test" http://127.0.0.1:9090/user/test1
```

#### DELETE
Remove entity

- delete router 'test1':

```
curl -X DELETE http://127.0.0.1:9090/router/test1
```

### Mikrotik scripts

#### '/router' PUT

script: name=api-put-router source=

```
local name [/system identity get name]
local loopback [/ip addr get [find interface=loopback] address]
local uptime [/system resource get uptime]
local architecture [/system resource get architecture-name]
local version [/system resource get version]
local date "$[/system clock get date] $[/system clock get time]"
local data "loopback=$loopback&uptime=$uptime&architecture=$architecture&version=$version&last_seen=$date"
do {
    /tool fetch http-method=put http-data=$data url="http://API_SERVER_ADDRESS:9090/router/$name" output=none
} on-error={
    /log error "api-put-router: Couldnt PUT data about $name on API"
}

``` 
**Don't forget to replace API_SERVER_ADDRESS on fetch**

scheduler: name=api-put-router start-time=jan/01/1970 start-time=00:00:00 interval=5m on-event=

```
/system script run api-put-router
```

#### '/host' PUT

netwatch: down-script=

```
local address 192.168.1.10

local name [/tool netwatch get [find host=$address] comment]
local status [/tool netwatch get [find host=$address] status]
local since [/tool netwatch get [find host=$address] since]
local witness [/system identity get name]

/log warning "netwatch: DOWN $address ($name) since $since"

# update host in db
local data "address=$address&status=$status&last_down=$since&witness=$witness"
do {
    /tool fetch http-method=put http-data=$data url="http://API_SERVER_ADDRESS:9090/host/$name" output=none
} on-error={
    /log error "netwatch: Couldnt PUT data about $address on API"
}

# send notification
local notifications "email=1&telegram=1"
do {
    /tool fetch http-method=post http-data=$notifications url="http://API_SERVER_ADDRESS:9090/host/$name/notification/USER" output=none
} on-error={
    /log error "netwatch: Couldnt POST notifications for $address on API"
}
```
**Don't forget to Replace API_SERVER_ADDRESS and USER on fetch**

netwatch: up-script=

```
local address 192.168.1.10

local name [/tool netwatch get [find host=$address] comment]
local status [/tool netwatch get [find host=$address] status]
local since [/tool netwatch get [find host=$address] since]
local witness [/system identity get name]

/log warning "netwatch: UP $address ($name) since $since"

local data "address=$address&status=$status&last_up=$since&witness=$witness"
do {
    /tool fetch http-method=put http-data=$data url="http://API_SERVER_ADDRESS:9090/host/$name" output=none
} on-error={
    /log error "netwatch: Couldnt PUT data about $address on API"
}

# send notification
local notifications "email=1&telegram=1"
do {
    /tool fetch http-method=post http-data=$notifications url="http://API_SERVER_ADDRESS:9090/host/$name/notification/USER" output=none
} on-error={
    /log error "netwatch: Couldnt POST notifications for $address on API"
}
```
**Don't forget to Replace API_SERVER_ADDRESS and USER on fetch**

