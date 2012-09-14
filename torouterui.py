#!/usr/bin/env python

from flask import Flask, render_template, send_from_directory, request
import argparse
import os

from helpers import sysstatus
from helpers import netif
import config

app = Flask(__name__)


@app.route('/')
def status():
    status = dict()
    status['system'] = sysstatus.get_system_status()
    status['wan'] = netif.get_wan_status()
    status['lan'] = netif.get_lan_status()
    status['wireless'] = netif.get_wireless_status()
    return render_template('home.html', settings=None, status=status)

@app.route('/administer/', methods=['GET', 'POST'])
def administer():
    return render_template('administer.html', settings=None, status=None)

@app.route('/reboot/', methods=['GET', 'POST'])
def administer():
    print request.form
    if request.method == 'GET':
        return render_template('reboot.html', status=None)
    if request.form.has_key('confirm'):
        # TODO: check reboot flag here?
        return render_template('reboot.html', status='rebooting')
    else:
        # XXX: flashing introduces cookies
        #flash("Didn't confirm, not rebooting", "warning")
        return render_template('reboot.html', status=None)


@app.route('/wan/', methods=['GET', 'POST'])
def wan():
    status = dict()
    status['wan'] = netif.get_wan_status()
    return render_template('wan.html', settings=None, status=None)

@app.route('/lan/', methods=['GET', 'POST'])
def lan():
    return render_template('lan.html', settings=None, status=None)

@app.route('/wireless/', methods=['GET', 'POST'])
def wireless():
    return render_template('wireless.html', settings=None, status=None)

@app.route('/tor/', methods=['GET', 'POST'])
def tor():
    return render_template('tor.html', settings=None, status=None)

@app.route('/logs/', methods=['GET'])
def logs():
    logs = dict()
    logs['dmesg'] = sysstatus.get_dmesg()
    logs['syslog'] = sysstatus.get_syslog()
    logs['authlog'] = sysstatus.get_authlog()
    return render_template('logs.html', logs=logs)

@app.route('/processes/', methods=['GET'])
def processes():
    process_list = sysstatus.get_process_list()
    return render_template('processes.html', process_list=process_list)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt',
                               mimetype='text/plain')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
        help="enable debugging interface")
    args = parser.parse_args()
    app.run(debug=args.debug)
