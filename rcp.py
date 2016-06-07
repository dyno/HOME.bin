#!/usr/bin/env python

import re
import sys
import socket
import pexpect
import os
from os.path import basename, exists, expanduser

def remove_known_host(hostname):
    if os.getuid() == 0:
        known_hosts = "/root/.ssh/known_hosts"
    else:
        known_hosts = expanduser("~/.ssh/known_hosts")
    if exists(known_hosts):
        f = open(known_hosts)
        try:
            lines = f.read().splitlines(True)
        finally:
            f.close()

        remote_hostname = ""
        if not re.match(r"^[0-9.]+$", hostname):
            remote_hostname = hostname.split(".")[0]
        remote_ip = socket.gethostbyname(hostname)

        _lines = []
        for line in lines:
            _continue = False
            for h in line.split()[0].split(","):
                if (remote_hostname and h.startswith(remote_hostname)) \
                        or socket.gethostbyname(h) == remote_ip:
                    _continue = True
            if _continue:
                continue
            _lines.append(line)

        f = open(known_hosts, "w")
        try:
            f.writelines(_lines)
        finally:
            f.close()

responses = [
    "(?i)password",                                                 #0, normal
    "(?i)are you sure you want to continue connecting",
    #"(?i)Are you sure you want to continue connecting (yes/no)?",  #1, new cert
    "(?i)permission denied",                                        #2, wrong passwd?
    "(?i)connection closed by remote host",                         #3, close unexpectly
    "B/s ",                                                         #4, transfering
    pexpect.TIMEOUT,                                                #5,
    pexpect.EOF,                                                    #6
    "(?i)No such file or directory",                                #7,
    "(?i)speedup is",                                               #8, end rsync transfer
    "(?i)build(ing)* file list",                                    #9, donnot time out if this is the case
    "(?i)Name or service not known",                                #10, hostname cannot be resolved
    "(?i)No route to host",                                         #11, the remote IP is unreachable
    "(?i)Connection Refused",                                       #12,
    "(?i)Host key verification failed.",                            #13,
    "(?i)rsync error:",                                             #14,
]

def error_out(msg):
    if isinstance(msg, str):
        msg = msg.replace("(?i)", "")
    elif msg == pexpect.TIMEOUT:
        msg = "timeout!"
    elif msg == pexpect.EOF:
        msg = "unexpected EOF!"

    print("encounter '%s'!" % msg)

def no_password_transfer(child):
    while True:
        i = child.expect(responses, timeout=None)
        if i != 4 and i != 9: break

    if i == 6 or i == 8:
        sys.exit(0)
    else:
        error_out(responses[i])
        sys.exit(1)

def password_transfer(child):
    child.sendline(passwd)
    no_password_transfer(child)

if __name__ == "__main__":
    #parse parameter
    try:
        src, dst, passwd = sys.argv[1:]

        remote_host = ""
        if ":" in src:
            remote_host = src.split(":")[0].split("@")[-1]
        if ":" in dst:
            remote_host = dst.split(":")[0].split("@")[-1]

        if remote_host:
            try:
                remove_known_host(remote_host)
            except:
                pass
    except:
        print >> sys.stderr, "usage: %s <src> <dst> <passwd>" % basename(__file__)
        sys.exit(1)

    #start working ...
    rcp_cmd = "rsync --rsh=ssh --archive --compress --partial --checksum --progress --sparse "
    child = pexpect.spawn("%s %s %s" % (rcp_cmd, src, dst))
    i = child.expect(responses, timeout=30)

    if i == 9: # build the file list to be considered
        i = child.expect(responses, timeout=None)

    if i == 8: # no need to transfer any data
        sys.exit(0)

    if i == 4: # no passwd
        no_password_transfer(child)

    if i == 0:
        password_transfer(child)

    if i == 1: #first connection, accept cert
        child.sendline("yes")
        i = child.expect(responses, timeout=None)
        if i == 4 or i == 9:
            no_password_transfer(child)
        elif i == 0:
            password_transfer(child)
        else:
            error_out(responses[i])
            sys.exit(1)
    else:
        error_out(responses[i])
        sys.exit(1)

