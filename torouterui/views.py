"""
Main Flask web application code for the torouter user interface.  See also
README and TODO.

Run ``./torouterui.py --help`` for command line argument options; see bottom of
this file for that code.

The code that actually interacts with the operating system is the /helpers
directory.

This code under a BSD license; see LICENSE file included with this code.

<https://trac.torproject.org/projects/tor/wiki/doc/Torouter>
"""

from flask import Flask, render_template, send_from_directory, request
import os

from torouterui import app
import torouterui.sysstatus as sysstatus
import torouterui.netif as netif
import torouterui.tor as tor


@app.route('/')
def statuspage():
    status = dict()
    status['system'] = sysstatus.get_system_status()
    status['resources'] = sysstatus.get_resources_status()
    status['wan'] = netif.get_wan_status()
    status['lan'] = netif.get_lan_status()
    status['wifi'] = netif.get_wifi_status()
    status['tor'] = tor.get_tor_status()
    return render_template('home.html', settings=None, status=status)

@app.route('/reboot/', methods=['GET', 'POST'])
def rebootpage():
    msg = list()
    if request.method == 'GET':
        return render_template('reboot.html', status=None)
    elif 'confirm' in request.form:
        # TODO: actually execute reboot
        #os.system('reboot &')
        return render_template('reboot.html', status='rebooting')
    else:
        msg.append(("error", "Didn't confirm, not rebooting",),)
        return render_template('reboot.html', status=None, messages=msg)

@app.route('/wan/', methods=['GET', 'POST'])
def wanpage():
    msg = list()
    status = dict(wan=netif.get_wan_status())
    if not status['wan']:
        msg.append(("error",
            "Interface not detected, can not be configured."),)
        return render_template('wan.html', form=None, status=status,
            messages=msg, formerr=None)
    if request.method == 'GET':
        form = netif.get_wan_settings()
        return render_template('wan.html', form=form, status=status,
            formerr=None)
    # Got this far, need to validate form
    formerr = dict()
    if request.form['ipv4method'] == 'disabled':
        pass    # no further validation
    elif request.form['ipv4method'] == 'dhcp':
        pass    # no further validation
    elif request.form['ipv4method'] == 'static':
        if not netif.is_valid_ipv4(request.form['ipv4addr']):
            formerr['ipv4addr'] = "Not a valid IPv4 address"
        if not netif.is_valid_ipv4mask(request.form['ipv4netmask']):
            formerr['ipv4netmask'] = "Not a valid IPv4 netmask"
        if not netif.is_valid_ipv4(request.form['ipv4gateway']):
            formerr['ipv4gateway'] = "Not a valid IPv4 address"
    else:
        ke = KeyError("Invalid net config method: %s" % form['ipv4method'])
        print ke
        raise ke
    if len(formerr.keys()) > 0:
        msg.append(("error",
            "Please correct the validation issues below"),)
    else:
        # Ok, we have a valid form, now to commit it
        try:
            netif.save_wan_settings(request.form)
            msg.append(("success",
                "Configuration saved! Check logs for any errors"),)
        except IOError, ioerr:
            msg.append(("error",
                "Was unable to commit changes... permissions problem? \"%s\""
                    % ioerr))
    return render_template('wan.html', form=request.form, status=status,
            formerr=formerr, messages=msg)

@app.route('/lan/', methods=['GET', 'POST'])
def lanpage():
    msg = list()
    status = dict()
    status['lan'] = netif.get_lan_status()
    if not status['lan']:
        msg.append(("error",
            "Interface not detected, can not be configured."),)
        return render_template('lan.html', form=None, status=status,
            messages=msg, formerr=None)
    if request.method == 'GET':
        form = netif.get_lan_settings()
        return render_template('lan.html', form=form, status=status,
            formerr=None)
    # Got this far, need to validate form
    formerr = dict()
    if request.form.get('ipv4enable') != 'true':
        pass    # no further validation
    else:
        if not netif.is_valid_ipv4(request.form['ipv4addr']):
            formerr['ipv4addr'] = "Not a valid IPv4 address"
        if not netif.is_valid_ipv4mask(request.form['ipv4netmask']):
            formerr['ipv4netmask'] = "Not a valid IPv4 netmask"
        if not netif.is_valid_ipv4(request.form['dhcpbase']):
            formerr['dhcpbase'] = "Not a valid IPv4 address"
        if not netif.is_valid_ipv4(request.form['dhcptop']):
            formerr['dhcptop'] = "Not a valid IPv4 address"
        if not netif.is_valid_ipv4mask(request.form['dhcpnetmask']):
            formerr['dhcpnetmask'] = "Not a valid IPv4 netmask"
    if len(formerr.keys()) > 0:
        msg.append(("error",
            "Please correct the validation issues below"),)
    else:
        # Ok, we have a valid form, now to commit it
        try:
            netif.save_lan_settings(request.form)
            msg.append(("success",
                "Configuration saved! Check logs for any errors"),)
        except IOError, ioerr:
            msg.append(("error",
                "Was unable to commit changes... permissions problem? \"%s\""
                    % ioerr))
        except Exception, err:
            msg.append(("error",
                "Was unable to commit changes... \"%s\"" % err))
            raise err
    return render_template('lan.html', form=request.form, status=status,
            formerr=formerr, messages=msg)

@app.route('/wifi/', methods=['GET', 'POST'])
def wifipage():
    msg = list()
    status = dict()
    status['wifi'] = netif.get_wifi_status()
    if not status['wifi']:
        msg.append(("error",
            "Interface not detected, can not be configured."),)
        return render_template('wifi.html', form=None, status=status,
            messages=msg, formerr=None)
    if request.method == 'GET':
        form = netif.get_wifi_settings()
        return render_template('wifi.html', form=form, status=status,
            formerr=None)
    # Got this far, need to validate form
    formerr = dict()
    if request.form['ipv4method'] == 'disabled':
        pass    # no further validation
    elif request.form['ipv4method'] == 'static':
        if not netif.is_valid_ipv4(request.form['ipv4addr']):
            formerr['ipv4addr'] = "Not a valid IPv4 address"
        if not netif.is_valid_ipv4mask(request.form['ipv4netmask']):
            formerr['ipv4netmask'] = "Not a valid IPv4 netmask"
        if not netif.is_valid_ipv4(request.form['ipv4gateway']):
            formerr['ipv4gateway'] = "Not a valid IPv4 address"
    else:
        ke = KeyError("Invalid method: %s" % form['ipv4method'])
        print ke
        raise ke
    if len(formerr.keys()) > 0:
        msg.append(("error",
            "Please correct the validation issues below"),)
    else:
        # Ok, we have a valid form, now to commit it
        try:
            netif.save_wifi_settings(request.form)
            msg.append(("success",
                "Configuration saved! Check logs for any errors"),)
        except IOError, ioerr:
            msg.append(("error",
                "Was unable to commit changes... permissions problem? \"%s\""
                    % ioerr))
        except Exception, e:
            msg.append(("error",
                "Was unable to commit changes... \"%s\"" % e))
    return render_template('wifi.html', form=request.form, status=status,
            formerr=formerr, messages=msg)
    return render_template('wifi.html', settings=None, status=None)

@app.route('/tor/', methods=['GET', 'POST'])
def torpage():
    msg = list()
    status = dict()
    status['tor'] = tor.get_tor_status()
    if request.method == 'GET':
        if status['tor']['state'] == 'DISABLED':
            msg.append(("warning",
                "Could not connect to Tor daemon for control. Will try to restart daemon if settings are saved from this page."),)
            form = None
        else:
            form = tor.get_tor_settings()
            print form
        return render_template('tor.html', form=form, status=status,
            formerr=None, messages=msg)
    # Got this far, need to validate form
    formerr = dict()
    # TODO: form validation
    if len(formerr.keys()) > 0:
        msg.append(("error",
            "Please correct the validation issues below"),)
    else:
        # Ok, we have a valid form, now to commit it
        try:
            tor.save_tor_settings(request.form)
            msg.append(("success",
                "Configuration saved! Check logs for any errors"),)
        except Exception, err:
            msg.append(("error",
                "Was unable to commit changes...\"%s\""
                    % err))
    return render_template('tor.html', settings=None, status=None,
        form=request.form, formerr=None, messages=msg)

@app.route('/logs/', methods=['GET'])
def logspage():
    logs = dict()
    logs['dmesg'] = sysstatus.get_dmesg()
    logs['syslog'] = sysstatus.get_syslog()
    logs['authlog'] = sysstatus.get_authlog()
    logs['tor'] = sysstatus.get_torlog()
    return render_template('logs.html', logs=logs)

@app.route('/processes/', methods=['GET'])
def processespage():
    process_list = sysstatus.get_process_list()
    return render_template('processes.html', process_list=process_list)

@app.route('/favicon.ico')
def favicon():
    """ Simple static redirect """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    """ "Just in case?" """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt',
                               mimetype='text/plain')

