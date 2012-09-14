
import os

from util import *

def parse_ip(ifname):
    """
    Example ip link show string:

        2: eth0: <BROADCAST,MULTICAST> mtu 1500 qdisc pfifo_fast state DOWN mode DEFAULT qlen 1000
            link/ether 00:12:34:56:78:90 brd ff:ff:ff:ff:ff:ff
    """
    d = dict()
    ipinfo = cli_read_lines('ip addr show %s' % ifname)
    if 0 == len(ipinfo):
        raise KeyError('No such interface: ' + ifname)
    iplinkl = ipinfo[0].split()
    d['ifname'] = iplinkl[1][:-1]
    val_indexes = {'mtu': 3, 'qdisc': 5, 'state': 7, 'mode': 9, 'qlen': 11}
    for k, v in val_indexes.iteritems():
        if len(iplinkl) > v and iplinkl[v] == k:
            d[k] = iplinkl[v+1]
    d['ipv4addrs'] = list()
    d['ipv6addrs'] = list()
    for l in ipinfo[1:]:
        # iterate through the address lines
        l = l.split()
        if l[0] == "link/ether":
            d['mac'] = l[1]
        elif l[0] == "inet":
            d['ipv4addrs'].append(dict(
                 addr=l[1].split('/')[0],
                 prefix=int(l[1].split('/')[1]),
                 mask=prefix_to_ipv4_mask(int(l[1].split('/')[1])),
                 scope=l[5]))
        elif l[0] == "inet6":
            d['ipv6addrs'].append(dict(
                 addr=l[1].split('/')[0],
                 prefix=int(l[1].split('/')[1]),
                 scope=l[3]))
    print d['ipv6addrs']
    return d

def get_wan_status(ifname='eth1'):
    d = dict()
    try:
        d.update(parse_ip(ifname))
    except KeyError:
        None
    return d

def get_lan_status(ifname='eth0'):
    d = dict()
    try:
        d.update(parse_ip(ifname))
    except KeyError:
        None
    return d

def get_wireless_status(ifname='wlan0'):
    d = dict()
    try:
        d.update(parse_ip(ifname))
    except KeyError, ke:
        raise ke
        return None
    return d

