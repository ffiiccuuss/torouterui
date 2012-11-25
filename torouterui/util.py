"""
Utility functions used by helper code to crudely grab the output of simple UNIX
command line programs, plus a couple misc other functions.
"""

import os
import subprocess

def cli_read(cmd):
    p = os.popen(cmd)
    return ''.join(p.readlines())

def cli_read_lines(cmd):
    p = os.popen(cmd)
    return p.readlines()

def fs_read(path):
    with open(path, 'r') as f:
        return ''.join(f.readlines())

def enable_service(name):
    #os.system('update-rc.d %s defaults &' % name)
    subprocess.Popen(['service', name, 'start'], close_fds=True)

def disable_service(name):
    """Currently, this is never actually called"""
    #os.system('update-rc.d %s remove &' % name)
    subprocess.Popen(['nohup', 'service', name, 'stop'], close_fds=True)

def prefix_to_ipv4_mask(prefixlen):
    assert(prefixlen >= 0)
    assert(prefixlen <= 32)
    mask = (0xFFFFFFFF & (0xFFFFFFFF << (32 - prefixlen)))
    a = (0xFF000000 & mask) >> 24
    b = (0x00FF0000 & mask) >> 16
    c = (0x0000FF00 & mask) >> 8
    d = (0x000000FF & mask)
    return '%d.%d.%d.%d' % (a, b, c, d)
