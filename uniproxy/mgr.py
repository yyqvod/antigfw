#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@date: 2012-05-25
@author: shell.xu
'''
import base64, logging, cStringIO
import serve
from http import *

logger = logging.getLogger('manager')

def auth_manager(func):
    def realfunc(ps, req, stream):
        managers = ps.config['managers']
        if not managers: return func(ps, req, stream)
        auth = req.get_header('authorization')
        if auth:
            username, password = base64.b64decode(auth[6:]).split(':')
            if managers.get(username, None) == password:
                return func(ps, req, stream)
        logging.info('access to %s without auth' % req.uri.split('?', 1)[0])
        response_http(stream, 401, headers=[('WWW-Authenticate', 'Basic realm="managers"')])
    return realfunc

@serve.ProxyServer.register('/')
@auth_manager
def mgr_socks_stat(ps, req, stream):
    body = '''<html><body>
<table><tr><td>socks</td><td>stat</td></tr>%s</table><p/>
active connections<table><tr><td>source</td><td>method</td><td>url</td>
<td>type</td></tr>%s</table></body></html>''' % (
        ''.join(['''<tr><td>%s</td><td>%s</td></tr>''' % (s.name, s.stat())
                 for s in ps.sockcfg]),
        ''.join(('''<tr><td>%s:%d</td><td>%s</td><td>%s</td><td>%s</td></tr>''' % (
                addr[0], addr[1], req.method, req.uri.split('?', 1)[0],
                'socks' if usesocks else 'direct')
                 for req, usesocks, addr in ps.worklist)))
    req.recv_body(stream)
    response_http(stream, 200, body=body)

@serve.ProxyServer.register('/reload')
@auth_manager
def mgr_reload(ps, req, stream):
    ps.init()
    req.recv_body(stream)
    response_http(stream, 302, headers=[('location', '/')])

@serve.ProxyServer.register('/quit')
@auth_manager
def mgr_quit(req, stream): sys.exit(-1)

@serve.ProxyServer.register('/domain')
@auth_manager
def mgr_domain_list(ps, req, stream):
    domain_template='''<html><body><form action="/add" method="POST"><input name="domain"/><input type="submit" name="submit"/></form><pre>%s</pre></body></html>'''
    strs = cStringIO.StringIO()
    ps.filter.save(strs)
    req.recv_body(stream)
    response_http(stream, 200, body=domain_template % strs.getvalue())

@serve.ProxyServer.register('/add')
@auth_manager
def mgr_domain_add(ps, req, stream):
    strs = cStringIO.StringIO()
    req.recv_body(stream, strs.write)
    form = dict([i.split('=', 1) for i in strs.getvalue().split('&')])
    if form.get('domain', '') and form['domain'] not in ps.filter:
        try:
            with open(ps.config['filter'][0], 'a') as fo:
                fo.write(form['domain'] + '\n')
        except: pass
        ps.filter.add(form['domain'])
    response_http(stream, 302, headers=[('location', '/domain')])
