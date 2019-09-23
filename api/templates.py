#!/usr/bin/env python

class Netwatch:

    def generate(self, host, status, server, notifications, user):

        email = notifications['email']
        sms = notifications['sms']
        telegram = notifications['telegram']

        notifications = "email={}&sms={}&telegram={}".format(email, sms, telegram)

        result = """### CREATED WITH HERMOD API TEMPLATE
local address {}

local name [/tool netwatch get [find host=$address] comment]
local status [/tool netwatch get [find host=$address] status]
local since [/tool netwatch get [find host=$address] since]
local witness [/system identity get name]

# workaround : cannot use variable name on same named key
local ip $address
do {{
    local mac [/ip arp get [find address=$ip] mac-address]
}} on-error={{
    # avoid break on error, do nothing
}}

/log warning \"netwatch: {} $address ($name) since $since\"

# update host in api
local data \"address=$address&status=$status&last_{}=$since&witness=$witness&{}&user={}&mac=$mac\"
do {{
    /tool fetch http-method=put http-data=$data url=\"{}/host/$name\" output=none
}} on-error={{
    /log error \"netwatch: Couldnt PUT data about $address on API\"
}}""".format(host, status.upper(), status, notifications, user, server)

        return result

class Update:

    def generate(self, server):

        result = """### CREATED WITH HERMOD API TEMPLATE
local name [/system identity get name]

local loopback [/ip addr get [find interface=loopback] address]
local uptime [/system resource get uptime]
local architecture [/system resource get architecture-name]
local version [/system resource get version]
local date \"$[/system clock get date] $[/system clock get time]\"

local data \"loopback=$loopback&uptime=$uptime&architecture=$architecture&version=$version&last_seen=$date\"

do {{
    /tool fetch http-method=put http-data=$data url=\"{}/router/$name\" output=none
}} on-error={{
    /log error \"api-put-router: Couldnt PUT data about $name on API\"
}}""".format(server)

        return result
