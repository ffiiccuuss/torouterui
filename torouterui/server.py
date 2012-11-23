
from torouterui import app, __version__
import argparse

def main():
    """Primary entry-point for torouterui.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug',
        action='store_true',
        help="enable debugging interface")
    parser.add_argument('--host',
        default="127.0.0.1",
        help="listen on this host/IP")
    parser.add_argument('--port',
        type=int,
        default=5050,
        help="listen on this port")
    parser.add_argument('--lanif',
        default="eth1",
        help="local ethernet interface (eth0 or eth1)")
    parser.add_argument('--wanif',
        default="eth0",
        help="upstream ethernet interface (eth0 or eth1)")
    parser.add_argument('--wifiif',
        default="uap0",
        help="wifi interface (uap0 or wlan0)")
    args = parser.parse_args()
    app.config['TOROUTERVERSION'] = __version__
    app.config['LAN_IF'] = args.lanif
    app.config['WAN_IF'] = args.wanif
    app.config['WIFI_IF'] = args.wifiif
    app.run(debug=args.debug, host=args.host, port=args.port)
