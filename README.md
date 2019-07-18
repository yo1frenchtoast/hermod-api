# HERMOD : Monitoring notification API for RouterOS

Monitoring actions for RouterOS netwatch

https://en.wikipedia.org/wiki/Herm%C3%B3%C3%B0r
`Hermóðr the Brave (Old Norse "war-spirit";[1] anglicized as Hermod) is a figure in Norse mythology, a son of the god Odin. He is often considered the messenger of the gods.`

## Getting started

### Installation

```
cd /opt/
git clone REPO
cp -r REPO/hermod-api/ ./
pip install -r hermod-api/requirements.txt
```

To enable systemd service :

```
cp hermod-api/hermod-api.service /lib/systemd/system/hermod-api.service
systemctl daemon-reload
systemctl enable hermod-api.service
service hermod-api.service start
```

### Docker

```
docker build -t hermod-api .
```

```
docker run -it -v /data/hermod-api/config.ini:/usr/src/app/api/config.ini --name hermod-api hermod-api
```

### Configuration
sample
```
[API]
host = 0.0.0.0
port = 5000
url = hermod.api.domain.tld
protocol = http
log_file = hermod-api.log

[SMTP]
server=smtp.domain.tld
port=587
use_tls=yes
user=admin@domain.tld
password=mySup3r53cureP455w0rd
```

### Database table definitions

/opt/hermod-api/api/data.db

#### Users
```
sqlite> CREATE TABLE users(
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
sqlite> CREATE TABLE routers(
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
sqlite> CREATE TABLE hosts(
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
curl http://127.0.0.1:5000/router
```

- specific user:

```
curl http://127.0.01:5000/user/admin
```

#### POST
Add new entity

- add new router:

```
curl -X POST -d "loopback=10.0.10.1" http://127.0.0.1:5000/router/test1
```

#### PUT
Modiy existing entity

- set phone and email address on user:

```
curl -X PUT -d "phone='+336684684984'&email=test@test.test" http://127.0.0.1:5000/user/test1
```

#### DELETE
Remove entity

- delete router 'test1':

```
curl -X DELETE http://127.0.0.1:5000/router/test1
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
    /tool fetch http-method=put http-data=$data url="http://API_SERVER_ADDRESS:5000/router/$name" output=none
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
    /tool fetch http-method=put http-data=$data url="http://API_SERVER_ADDRESS:5000/host/$name" output=none
} on-error={
    /log error "netwatch: Couldnt PUT data about $address on API"
}

# send notification
local notifications "email=1&telegram=1"
do {
    /tool fetch http-method=post http-data=$notifications url="http://API_SERVER_ADDRESS:5000/host/$name/notification/USER" output=none
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
    /tool fetch http-method=put http-data=$data url="http://API_SERVER_ADDRESS:5000/host/$name" output=none
} on-error={
    /log error "netwatch: Couldnt PUT data about $address on API"
}

# send notification
local notifications "email=1&telegram=1"
do {
    /tool fetch http-method=post http-data=$notifications url="http://API_SERVER_ADDRESS:5000/host/$name/notification/USER" output=none
} on-error={
    /log error "netwatch: Couldnt POST notifications for $address on API"
}
```
**Don't forget to Replace API_SERVER_ADDRESS and USER on fetch**

### OVH SMS : API configuration

Please follow python-ovh documentation to create config file : https://github.com/ovh/python-ovh/blob/master/README.rst
