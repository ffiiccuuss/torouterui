"""
Helper code for agregating general system status information, and for reading
in system log files.
"""

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
    """
    Example ``df -h /home`` output:

        Filesystem              Size  Used Avail Use% Mounted on
        /dev/mapper/xxxxx-root  231G  184G   35G  85% /

    Example ``free -m`` output:

                    total       used       free     shared    buffers     cached
        Mem:          3862       2292       1570          0        104        689
        -/+ buffers/cache:       1498       2364
        Swap:         7983        202       7781

    Example ``uptime`` output:

         21:38:55 up 7 days,  5:43, 11 users,  load average: 0.60, 0.63, 0.63
    """
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
    """
    Example ``ps aux`` output:

        USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
        root         1  0.0  0.0  10636   676 ?        Ss   Sep08   0:05 init [2]
        root         2  0.0  0.0      0     0 ?        S    Sep08   0:00 [kthreadd]
        root         3  0.0  0.0      0     0 ?        S    Sep08   0:40 [ksoftirqd/0]
        root         6  0.0  0.0      0     0 ?        S    Sep08   0:00 [migration/0]
    """
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
