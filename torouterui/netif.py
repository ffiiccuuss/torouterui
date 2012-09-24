"""
Helper functions for working with network interfaces and network configuration
(including WiFi).
"""

import os
import augeas

from torouterui import app
from util import *

def parse_ip(ifname):
    """
    Calls the ``ip`` command and parse the output to collect current status
    information about a given network interface (specified by ifname argument).

    Returns a dictionary, notably always including a 'state' string value.

    If the interface can not be found at all, raises a KeyError.

    Example ``ip link show`` string:

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
    if 'LOWER_UP' in iplinkl[2][1:-1].split(","):
        d['state'] = "RUNNING"
    elif 'NO-CARRIER' in iplinkl[2][1:-1].split(","):
        d['state'] = "DISCONNECTED"
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
    return d

def parse_iw(ifname):
    """
    Calls the ``iw`` command and parse the output to collect current status
    information about a given network interface (specified by ifname argument).

    Returns a dictionary, notably always including a 'state' string value.

    If the interface can not be found at all, raises a KeyError.

    Example `iw dev wlan0 link` string (sic):

        Connected to c0:25:06:51:22:9b (on wlan0)
                SSID: fleischfressendepflanze
                freq: 2427
                RX: 73744193 bytes (456838 packets)
                TX: 3269174 bytes (19709 packets)
                signal: -44 dBm
                tx bitrate: 72.2 MBit/s MCS 7 short GI

                bss flags:
                dtim period:    0
                beacon int:     100
    """
    d = dict()
    iwinfo = cli_read_lines('iw dev %s link' % ifname)
    if 0 == len(iwinfo):
        raise KeyError('No such interface: ' + ifname)
    if iwinfo[0].strip() == "Not connected.":
        d['radio_state'] = "disabled"
        return d
    else:
        d['radio_state'] = "enabled"
    for l in iwinfo:
        l = l.strip()
        if l.startswith("SSID:"):
            d['ssid'] = l[6:].strip()
        elif l.startswith("freq:"):
            d['freq'] = "%sMHz" % l.split()[-1].strip()
        elif l.startswith("signal:"):
            d['signal_dbm'] = l.split()[1]
        elif l.startswith("tx bitrate:"):
            d['signal_throughput'] = ' '.join(l.split()[2:4])
    return d

def read_augeas_ifinfo(ifname):
    d = dict()
    aug = augeas.Augeas(flags=augeas.Augeas.NO_MODL_AUTOLOAD)
    aug.set("/augeas/load/Interfaces/lens", "Interfaces.lns")
    aug.set("/augeas/load/Interfaces/incl", "/etc/network/interfaces")
    aug.load()
    for iface in aug.match("/files/etc/network/interfaces/iface"):
        if aug.get(iface) == ifname:
            if aug.get(iface + "/family") == 'inet':
                d['ipv4method'] = aug.get(iface + "/method")
                if d['ipv4method'] == 'manual':
                    d['ipv4method'] = 'disabled'
                d['ipv4addr'] = aug.get(iface + "/address")
                d['ipv4netmask'] = aug.get(iface + "/netmask")
                d['ipv4gateway'] = aug.get(iface + "/gateway")
                d['ipv4mtu'] = aug.get(iface + "/mtu")
                d['ipv4mac'] = aug.get(iface + "/hwaddress")
            elif aug.get(iface + "/family") == 'inet6':
                # handle ipv6 stuff
                pass
            aug.close()
            return d
    aug.close()
    return None

def write_augeas_ifinfo(ifname, settings, method='disabled'):
    d = dict()
    aug = augeas.Augeas(flags=augeas.Augeas.NO_MODL_AUTOLOAD)
    aug.set("/augeas/load/Interfaces/lens", "Interfaces.lns")
    aug.set("/augeas/load/Interfaces/incl", "/etc/network/interfaces")
    aug.load()
    path = None
    for iface in aug.match("/files/etc/network/interfaces/iface"):
        if aug.get(iface) == ifname and aug.get(iface + "/family") == 'inet':
            path = iface
    if not path:
        # insert iface
        if len(aug.match("/files/etc/network/interfaces/iface")) == 0:
            # no interfaces at all, insert wherever
            path = "/files/etc/network/interfaces/iface"
            aug.set(path, ifname)
        else:
            aug.insert("/files/etc/network/interfaces/iface", "iface",
                before=False)
            path = aug.match("/files/etc/network/interfaces/iface")[-1]
            aug.set(path, ifname)
    assert path, "require path to be set"
    aug.set(path + "/family", 'inet')
    if method == 'disabled':
        aug.set(path + "/method", 'manual')
        aug.remove(path + "/address")
        aug.remove(path + "/netmask")
        aug.remove(path + "/gateway")
    elif method == 'dhcp':
        aug.set(path + "/method", 'dhcp')
        aug.remove(path + "/address")
        aug.remove(path + "/netmask")
        aug.remove(path + "/gateway")
    elif method == 'static':
        aug.set(path + "/method", 'static')
        aug.set(path + "/address", str(settings['ipv4addr']))
        aug.set(path + "/netmask", str(settings['ipv4netmask']))
        aug.set(path + "/gateway", str(settings['ipv4gateway']))
    else:
        raise ValueError("unrecognized network interface method: " + method)
    print "committing with  augeas..."
    aug.save()
    print "augeas errors: %s" % aug.get("/augeas/error")
    aug.close()

def get_wan_status(ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['WAN_IF']
    d = dict()
    try:
        d.update(parse_ip(ifname))
    except KeyError:
        return None
    return d

def get_lan_status(ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['LAN_IF']
    d = dict()
    try:
        d.update(parse_ip(ifname))
    except KeyError:
        return None
    return d

def get_wifi_status(ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['WIFI_IF']
    d = dict()
    try:
        d.update(parse_ip(ifname))
    except KeyError, ke:
        return None
    if ifname.startswith('wlan'):
        d.update(parse_iw(ifname))
    else:
        raise NotImplementedError("uap wifi status not yet implemented")
    return d

def get_wan_settings(ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['WAN_IF']
    return read_augeas_ifinfo(ifname)

def save_wan_settings(form, ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['WAN_IF']
    write_augeas_ifinfo(ifname, method=form['ipv4method'], settings=form)
    if form['ipv4method'] == 'disabled':
        print "ifdown..."
        os.system("ifdown %s" % ifname)
    else:
        print "ifup..."
        os.system("ifdown %s" % ifname)
        os.system("ifup %s &" % ifname)

def get_lan_settings(ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['LAN_IF']
    d = read_augeas_ifinfo(ifname)
    return d

def save_lan_settings(form, ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['LAN_IF']
    write_augeas_ifinfo(ifname, method=form['ipv4method'], settings=form)
    if form['ipv4method'] == 'disabled':
        print "ifdown..."
        os.system("ifdown %s" % ifname)
    else:
        print "ifup..."
        os.system("ifdown %s" % ifname)
        os.system("ifup %s &" % ifname)

def get_wifi_settings(ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['WIFI_IF']
    #d = read_augeas_ifinfo(ifname)
    d = dict()
    if not d:
        return d
    if ifname.startswith('wlan'):
        d.update(dict())    # extra wireless settings
    else:
        raise NotImplementedError("uap wifi settings not yet implemented")
    return d

def save_wifi_settings(ifname=None):
    if not ifname:
        # grab configuration at run time, not earlier
        ifname = app.config['WIFI_IF']
    pass

def is_valid_ipv4(s):
    # TODO: this is a hack
    l = s.split('.')
    if not len(l) == 4:
        return False
    try:
        l = map(int, l)
    except ValueError:
        return False
    if l[0] > 255 or l[1] > 255 or l[2] > 255 or l[3] > 255:
        return False
    if l[0] == 0 or l[3] == 0:
        return False
    return True

def is_valid_ipv4mask(s):
    # TODO: this is a hack
    l = s.split('.')
    if not len(l) == 4:
        return False
    try:
        l = map(int, l)
    except ValueError:
        return False
    if l[0] > 255 or l[1] > 255 or l[2] > 255 or l[3] > 255:
        return False
    return True

