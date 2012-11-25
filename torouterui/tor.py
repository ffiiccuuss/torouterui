"""
Helper code for interacting with Tor and modifying the Tor system
configuration.
"""
import os
import time

from TorCtl import TorCtl
import util

def tor_getinfo(conn, key):
    return conn.get_info(key)[key]

def tor_getoption(conn, key):
    return conn.get_option(key)[0][1]

def get_tor_status():
    """Ask for status over torctl pipe"""
    d = dict()
    try:
        f = open('/var/run/tor/tor.pid', 'r')
        f.close()
    except IOError, ioe:
        if ioe.errno == 13:
            # "Permission denied"
            d['state'] = 'PERMISSION_DENIED'
            return d
        elif ioe.errno == 2:
            # "No such file or directory"
            d['state'] = 'DISABLED'
            return d
        else:
            raise ioe
    conn = TorCtl.connect()
    if not conn:
        d['state'] = 'DISABLED'
        return d
    d['version'] = tor_getinfo(conn, 'version')
    d['traffic_read_bytes'] = int(tor_getinfo(conn, 'traffic/read'))
    d['traffic_written_bytes'] = int(tor_getinfo(conn, 'traffic/written'))
    d['version_current'] = tor_getinfo(conn, 'status/version/current')
    d['circuit_established'] = bool(
        tor_getinfo(conn, 'status/circuit-established'))
    d['is_alive'] = conn.is_live()
    if d['circuit_established']:
        d['state'] = 'ESTABLISHED'
    else:
        d['state'] = 'CONNECTING'
    conn.close()
    return d
            

def get_tor_settings():
    """Ask for settings over torctl pipe; don't use augeas"""
    d = dict()
    conn = TorCtl.connect()
    if not conn:
        # couldn't connect; will need to display error to user
        return None
    d['tor_relaybandwidthrateKBps'] = \
        int(int(tor_getoption(conn, 'RelayBandwidthRate'))/1024.)
    d['tor_relaybandwidthburstKBps'] = \
        int(int(tor_getoption(conn, 'RelayBandwidthBurst'))/1024.)

    d['tor_sockslistenaddress'] = tor_getoption(conn, 'SocksListenAddress')
    d['tor_virtualaddrnetwork'] = tor_getoption(conn, 'VirtualAddrNetwork')
    d['tor_translistenaddress'] = tor_getoption(conn, 'TransListenAddress')
    d['tor_dnslistenaddress'] = tor_getoption(conn, 'DNSListenAddress')

    d['tor_enable'] = (not bool(int(tor_getoption(conn, 'DisableNetwork')))) and 'true'
    if tor_getoption(conn, 'ExitPolicy') == 'reject *:*':
        d['tor_exitnodeenable'] = False
    else:
        d['tor_exitnodeenable'] = 'true'

    orport = tor_getoption(conn, 'ORPort')
    bridgerelay = tor_getoption(conn, 'BridgeRelay')
    if orport == 'auto' and bridgerelay == '0':
        d['tor_relaytype'] = 'relay'
    elif orport == 'auto' and bridgerelay == '1':
        d['tor_relaytype'] = 'bridge'
    elif orport == '0':
        d['tor_relaytype'] = 'none'
    else:
        print "WARNING: unknown tor_relaytype state"
        d['tor_relaytype'] = 'unknown'

    conn.close()
    return d

def restart_tor():
    grepcode = os.system("grep '^DisableNetwork 1' /etc/tor/torrc")
    if grepcode == 512:
        # permission denied
        raise IOError("Don't have permission to read /etc/tor/torrc")
    elif grepcode == 0:
        pass # found
    else:
        if os.system('echo "DisableNetwork 1" >> /etc/tor/torrc') != 0:
            raise IOError("Don't have permission to write /etc/tor/torrc")
    util.enable_service('tor')
    time.sleep(3)
    conn = TorCtl.connect()
    if not conn:
        raise Exception("Could not start tor daemon!")
    conn.close()

def save_tor_settings(form):
    """Commit settings through torctl pipe, then send SAVECONF"""
    conn = TorCtl.connect()
    if not conn:
        raise Exception("couldn't connect to tor daemon; need to boot up tor daemon in disabled state")

    conn.set_option('RelayBandwidthRate',
                    "%dKB" % int(form['tor_relaybandwidthrateKBps']))
    conn.set_option('RelayBandwidthBurst',
                    "%dKB" % int(form['tor_relaybandwidthburstKBps']))

    conn.set_option('DNSListenAddress', form['tor_dnslistenaddress'])
    conn.set_option('SocksListenAddress', form['tor_sockslistenaddress'])
    conn.set_option('VirtualAddrNetwork', form['tor_virtualaddrnetwork'])
    conn.set_option('TransListenAddress', form['tor_translistenaddress'])

    if form.get('tor_enable') == 'true':
        conn.set_option('DisableNetwork', '0')
    else:
        conn.set_option('DisableNetwork', '1')

    if form.get('tor_exitnodeenable') == 'true':
        conn.set_option('ExitPolicy', '')
    else: 
        conn.set_option('ExitPolicy', 'reject *:*')

    if form['tor_relaytype'] == 'relay':
        conn.set_options([('ORPort', 'auto'), ('BridgeRelay', '0')])
    elif form['tor_relaytype'] == 'bridge':
        conn.set_options([('ORPort', 'auto'), ('BridgeRelay', '1')])
    else:   # type = 'none'
        conn.set_options([('ORPort', '0'), ('BridgeRelay', '0')])

    conn.save_conf() 
    conn.close()

