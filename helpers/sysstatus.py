
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

def get_resources_status():
    d = dict()
    disk_info = cli_read_lines('df -h /home')[1].split()
    d['disk_used'] = disk_info[2]
    d['disk_avail'] = disk_info[1]
    d['disk_percent'] = int(disk_info[4][:-1])

    ram_info = cli_read_lines('free -m')[1].split()
    d['ram_used'] = "%sMB" % ram_info[2]
    d['ram_avail'] = "%sMB" % ram_info[1]
    d['ram_percent'] = int(float(ram_info[2])/float(ram_info[1]) * 100.0)

    d['cpu_cores'] = 1
    for l in open('/proc/cpuinfo', 'r'):
        if l.split(":")[0].strip() == "cpu cores":
            d['cpu_cores'] = int(l.split(":")[-1].strip())
            break
    cpu_info = cli_read('uptime')
    d['cpu_load'] = cpu_info.split()[-3].strip(',')
    d['cpu_percent'] = int(float(d['cpu_load'])/float(d['cpu_cores']) * 100.0)
    return d

def get_dmesg():
    try:
        return cli_read('dmesg')
    except IOError:
        return None

def get_authlog():
    try:
        with open('/var/log/auth.log') as f:
            return ''.join(f.readlines())
    except IOError:
        return None

def get_syslog():
    try:
        with open('/var/log/syslog') as f:
            return ''.join(f.readlines())
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
