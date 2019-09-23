#!/usr/bin/python

import re
import sys
import json
import requests
import paramiko
import getpass

def main():
    if len(sys.argv) > 0 and len(sys.argv) == 8:
        args = sys.argv
        args.pop(0)
        print args
        (router, username, host, name, user, level, server) = args
    else:
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

    notifications = {}
    if level == '0':
        pass
    elif level == '1':
        notifications = {'email': 1}
    elif level == '2':
        notifications = {'email': 1, 'telegram': 1}
    elif level == '3':
        notifications = {'email': 1, 'sms': 1}
    elif level == '4':
        notifications = {'email': 1, 'telegram': 1, 'sms': 1}
    else:
        print "Cannot determinate notification level : {}".format(level)
        sys.exit(0)

    if not re.match("^https?:\/\/.*:\d*$", server):
        print "Error on API server url : {}".format(server)
        sys.exit(0)

    data = notifications
    data['user'] = user
    data['server'] = server

    r = requests.get("{}/host/template/{}".format(server, host), data=data)

    content = json.loads(r.content)

    down_script = json.dumps(content['down'])
    up_script = json.dumps(content['up'])

    cmd = "/tool netwatch add host={} comment={} down-script={} up-script={}".format(host, name, down_script, up_script)
    cmd = cmd.replace("$", "\$")
    print cmd

    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(router, username=username)

        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
    finally:
        ssh.close()

    return result

if __name__ == "__main__":
    main()
