
import os

from util import *

def get_system_status():
    d = dict()
    d['hostname'] = cli_read('hostname')
    d['fqdn'] = cli_read('hostname -f')
    d['domain'] = cli_read('hostname -d')
    d['current_time'] = cli_read('date -R')
    d['uptime'] = cli_read('uptime')
    return d

def get_dmesg():
    try:
        return cli_read('dmesg')
    except IOError:
        return None

def get_authlog():
    try:
        with open('/var/log/auth.log') as f:
            return '\n'.join(f.readlines())
    except IOError:
        return None

def get_syslog():
    try:
        with open('/var/log/syslog') as f:
            return '\n'.join(f.readlines())
    except IOError:
        return None

def get_process_list():
    plist = list()
    first = True
    for l in cli_read_lines('ps aux --sort -%mem')[1:]:
        l = l.split()
        plist.append(dict(
            user = l[0],
            pid = l[1],
            perc_cpu = l[2],
            perc_mem = l[3],
            status_code = l[7],
            started = l[8],
            time = l[9],
            command = ' '.join(l[10:])))
    return plist
