#!/usr/bin/python

import re
import sys
import paramiko
import getpass

def main():

    router = raw_input("Enter ip address or hostname of the router to apply rule : ")
    username = raw_input("Enter username to connect to the router : ")
    host = raw_input("Enter ip address of the netwatch target host : ")
    name = raw_input("Enter name of the netwatch target host : ")
    user = raw_input("Enter user to notify, defined in API : ")
    print """
    notification level:
     - 0 = only routeros log
     - 1 = + email
     - 2 = + email + telegram
     - 3 = + email + sms
     - 4 = + email + telegram + sms
     """
    level = raw_input("Enter notification level (explanations above) : ")
    server = raw_input("Enter full http/s url of the api server (ex: http://api.test.org:12345) : ")

    notifications = ''
    if level == '0':
        pass
    elif level == '1':
        notifications = 'email=1'
    elif level == '2':
        notifications = 'email=1&telegram=1'
    elif level == '3':
        notifications = 'email=1&sms=1'
    elif level == '4':
        notifications = 'email=1&telegram=1&sms=1'
    else:
        print "Cannot determinate notification level : {}".format(level)
        sys.exit(0)

    if not re.match("^https?:\/\/.*:\d*$", server):
        print "Error on API server url : {}".format(server)
        sys.exit(0)

    down_script = """### CREATED BY SCRIPT deploy-netwatch_rule.py
local address {0}

local name [/tool netwatch get [find host=$address] comment]
local status [/tool netwatch get [find host=$address] status]
local since [/tool netwatch get [find host=$address] since]
local witness [/system identity get name]

/log warning \"netwatch: DOWN $address ($name) since $since\"

# update host in db
local data \"address=$address&status=$status&last_down=$since&witness=$witness\"
do {{
    /tool fetch http-method=put http-data=$data url=\"{1}/host/$name\" output=none
}} on-error={{
    /log error \"netwatch: Couldnt PUT data about $address on API\"
}}

# send notification
local notifications \"{2}\"
do {{
    /tool fetch http-method=post http-data=$notifications url=\"{1}/host/$name/notification/{3}\" output=none
}} on-error={{
    /log error \"netwatch: Couldnt POST notifications for $address on API\"
}}""".format(host, server, notifications, user)

    up_script = """### CREATED BY SCRIPT deploy-netwatch_rule.py
local address {0}

local name [/tool netwatch get [find host=$address] comment]
local status [/tool netwatch get [find host=$address] status]
local since [/tool netwatch get [find host=$address] since]
local witness [/system identity get name]

/log warning \"netwatch: UP $address ($name) since $since\"

# update host in db
local data \"address=$address&status=$status&last_up=$since&witness=$witness\"
do {{
    /tool fetch http-method=put http-data=$data url=\"{1}/host/$name\" output=none
}} on-error={{
    /log error \"netwatch: Couldnt PUT data about $address on API\"
}}

# send notification
local notifications \"{2}\"
do {{
    /tool fetch http-method=post http-data=$notifications url=\"{1}/host/$name/notification/{3}\" output=none
}} on-error={{
    /log error \"netwatch: Couldnt POST notifications for $address on API\"
}}""".format(host, server, notifications, user)

    cmd = "/tool netwatch add host={} comment={} down-script={} up-script={}".format(host, name, down_script, up_script)

    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(router, username='ansible')

        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
    finally:
        ssh.close()

    return result

if __name__ == "__main__":
    main()
