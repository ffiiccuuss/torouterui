"""
Helper code for interacting with Tor and modifying the Tor system
configuration.
"""

from TorCtl import TorCtl

def tor_getinfo(conn, key):
    return conn.get_info(key)[key]

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
    if d['circuit_established']:
        d['state'] = 'ESTABLISHED'
    else:
        d['state'] = 'CONNECTING'
    conn.close()
    return d
            

def get_tor_settings():
    """Ask for settings over torctl pipe; don't use augeas"""
    d = dict()
    return d


def save_tor_settings():
    """Commit settings through torctl pipe, then send SAVECONF"""
    pass
