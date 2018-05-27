import os
import platform
import signal
import sys
import time
import traceback
import webbrowser
from uuid import uuid4

from tornado.ioloop import IOLoop

from couchpotato.api import addApiView
from couchpotato.core.event import fire_event, add_event
from couchpotato.core.helpers.variable import clean_host, md5, is_sub_folder, compare_versions
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
from couchpotato.environment import Env

log = CPLog(__name__)

autoload = 'Core'


class Core(Plugin):

    ignore_restart = [
        'Core.restart', 'Core.shutdown',
        'Updater.check', 'Updater.autoUpdate',
    ]
    shutdown_started = False

    def __init__(self):
        addApiView('app.shutdown', self.shutdown, docs = {
            'desc': 'Shutdown the app.',
            'return': {'type': 'string: shutdown'}
        })
        addApiView('app.restart', self.restart, docs = {
            'desc': 'Restart the app.',
            'return': {'type': 'string: restart'}
        })
        addApiView('app.available', self.available, docs = {
            'desc': 'Check if app available.'
        })
        addApiView('app.version', self.version_view, docs={
            'desc': 'Get version.'
        })

        add_event('app.shutdown', self.shutdown)
        add_event('app.restart', self.restart)
        add_event('app.load', self.launch_browser, priority=1)
        add_event('app.base_url', self.create_base_url)
        add_event('app.api_url', self.create_api_url)
        add_event('app.version', self.version)
        add_event('app.load', self.check_data_directory)
        add_event('app.load', self.clean_up_folders)
        add_event('app.load.after', self.dependencies)

        add_event('setting.save.core.password', self.md5_password)
        add_event('setting.save.core.api_key', self.check_api_key)

        # Make sure we can close-down with ctrl+c properly
        if not Env.get('desktop'):
            self.signal_handler()

        # Set default urlopen timeout
        import socket
        socket.setdefaulttimeout(30)

        # Don't check ssl by default
        try:
            if sys.version_info >= (2, 7, 9):
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
        except:
            log.debug('Failed setting default ssl context: %s', traceback.format_exc())

    def dependencies(self):

        # Check if lxml is available
        try: from lxml import etree
        except: log.error('LXML not available, please install for better/faster scraping support: `http://lxml.de/installation.html`')

        try:
            import OpenSSL
            v = OpenSSL.__version__
            v_needed = '0.15'
            if compare_versions(OpenSSL.__version__, v_needed) < 0:
                log.error('OpenSSL installed but %s is needed while %s is installed. Run `pip install pyopenssl --upgrade`', (v_needed, v))

            try:
                import ssl
                log.debug('OpenSSL detected: pyopenssl (%s) using OpenSSL (%s)', (v, ssl.OPENSSL_VERSION))
            except:
                pass
        except:
            log.error('OpenSSL not available, please install for better requests validation: `https://pyopenssl.readthedocs.org/en/latest/install.html`: %s', traceback.format_exc())

    def md5_password(self, value):
        return md5(value) if value else ''

    def check_api_key(self, value):
        return value if value and len(value) > 3 else uuid4().hex

    def check_data_directory(self):
        if is_sub_folder(Env.get('data_dir'), Env.get('app_dir')):
            log.error('You should NOT use your CouchPotato directory to save your settings in. Files will get overwritten or be deleted.')

        return True

    def clean_up_folders(self):
        only_clean = ['couchpotato', 'libs', 'init']
        self.deleteEmptyFolder(Env.get('app_dir'), show_error = False, only_clean = only_clean)

    def available(self, **kwargs):
        return {
            'success': True
        }

    def shutdown(self, **kwargs):
        if self.shutdown_started:
            return False

        def shutdown():
            self.init_shutdown()

        if IOLoop.current()._closing:
            shutdown()
        else:
            IOLoop.current().add_callback(shutdown)

        return 'shutdown'

    def restart(self, **kwargs):
        if self.shutdown_started:
            return False

        def restart():
            self.init_shutdown(restart=True)
        IOLoop.current().add_callback(restart)

        return 'restarting'

    def init_shutdown(self, restart=False):
        if self.shutdown_started:
            log.info('Already shutting down')
            return

        log.info('Shutting down' if not restart else 'Restarting')

        self.shutdown_started = True

        fire_event('app.do_shutdown', restart=restart)
        log.debug('Every plugin got shutdown event')

        loop = True
        starttime = time.time()
        while loop:
            log.debug('Asking who is running')
            still_running = fire_event('plugin.running', merge=True)
            log.debug('Still running: %s', still_running)

            if len(still_running) == 0:
                break
            elif starttime < time.time() - 30:  # Always force break after 30s wait
                break

            running = list(set(still_running) - set(self.ignore_restart))
            if len(running) > 0:
                log.info('Waiting on plugins to finish: %s', running)
            else:
                loop = False

            time.sleep(1)

        log.debug('Safe to shutdown/restart')

        loop = IOLoop.current()

        try:
            if not loop._closing:
                loop.stop()
        except RuntimeError:
            pass
        except:
            log.error('Failed shutting down the server: %s', traceback.format_exc())

        fire_event('app.after_shutdown', restart=restart)

    def launch_browser(self):

        if Env.setting('launch_browser'):
            log.info('Launching browser')

            url = self.create_base_url()
            try:
                webbrowser.open(url, 2, 1)
            except:
                try:
                    webbrowser.open(url, 1, 1)
                except:
                    log.error('Could not launch a browser.')

    def create_base_url(self):
        host = Env.setting('host')
        if host == '0.0.0.0' or host == '':
            host = 'localhost'
        port = Env.setting('port')
        ssl = Env.setting('ssl_cert') and Env.setting('ssl_key')

        return '%s:%d%s' % (clean_host(host, ssl=ssl).rstrip('/'), int(port), Env.get('web_base'))

    def create_api_url(self):
        return '%sapi/%s' % (self.create_base_url(), Env.setting('api_key'))

    def version(self):
        ver = fire_event('updater.info', single=True) or {'version': {}}

        if os.name == 'nt': platf = 'windows'
        elif 'Darwin' in platform.platform(): platf = 'osx'
        else: platf = 'linux'

        return '%s - %s-%s - v2' % (platf, ver.get('version').get('type') or 'unknown', ver.get('version').get('hash') or 'unknown')

    def version_view(self, **kwargs):
        return {
            'version': self.version()
        }

    def signal_handler(self):
        if Env.get('daemonized'): return

        def signal_handler(*args, **kwargs):
            fire_event('app.shutdown', single=True)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


config = [{
    'name': 'core',
    'order': 1,
    'groups': [
        {
            'tab': 'general',
            'name': 'basics',
            'description': 'Needs restart before changes take effect.',
            'wizard': True,
            'options': [
                {
                    'name': 'username',
                    'default': '',
                    'ui-meta' : 'rw',
                },
                {
                    'name': 'password',
                    'default': '',
                    'type': 'password',
                },
                {
                    'name': 'port',
                    'default': 5050,
                    'type': 'int',
                    'description': 'The port I should listen to.',
                },
                {
                    'name': 'ipv6',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Also bind the WebUI to ipv6 address',
                },
                {
                    'name': 'ssl_cert',
                    'description': 'Path to SSL server.crt',
                    'advanced': True,
                },
                {
                    'name': 'ssl_key',
                    'description': 'Path to SSL server.key',
                    'advanced': True,
                },
                {
                    'name': 'launch_browser',
                    'default': True,
                    'type': 'bool',
                    'description': 'Launch the browser when I start.',
                    'wizard': True,
                },
                {
                    'name': 'dark_theme',
                    'default': False,
                    'type': 'bool',
                    'description': 'For people with sensitive skin',
                    'wizard': True,
                },
            ],
        },
        {
            'tab': 'general',
            'name': 'advanced',
            'description': "For those who know what they're doing",
            'advanced': True,
            'options': [
                {
                    'name': 'api_key',
                    'default': uuid4().hex,
                    'ui-meta' : 'ro',
                    'description': 'Let 3rd party app do stuff. <a href="../../docs/" target="_self">Docs</a>',
                },
                {
                    'name': 'dereferer',
                    'default': 'http://www.nullrefer.com/?',
                    'description': 'Derefer links to external sites, keep empty for no dereferer. Example: http://www.dereferer.org/? or http://www.nullrefer.com/?.',
                },
                {
                    'name': 'use_proxy',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Route outbound connections via proxy. Currently, only <a href="https://en.wikipedia.org/wiki/Proxy_server#Web_proxy_servers" target=_"blank">HTTP(S) proxies</a> are supported. ',
                },
                {
                    'name': 'proxy_server',
                    'description': 'Override system default proxy server. Currently, only <a href="https://en.wikipedia.org/wiki/Proxy_server#Web_proxy_servers" target=_"blank">HTTP(S) proxies</a> are supported. Ex. <i>\"127.0.0.1:8080\"</i>. Keep empty to use system default proxy server.',
                },
                {
                    'name': 'proxy_username',
                    'description': 'Only HTTP Basic Auth is supported. Leave blank to disable authentication.',
                },
                {
                    'name': 'proxy_password',
                    'type': 'password',
                    'description': 'Leave blank for no password.',
                },
                {
                    'name': 'bookmarklet_host',
                    'description': 'Override default bookmarklet host. This can be useful in a reverse proxy environment. For example: "http://username:password@customHost:1020". Requires restart to take effect.',
                    'advanced': True,
                },
                {
                    'name': 'debug',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Enable debugging.',
                },
                {
                    'name': 'development',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Enable this if you\'re developing, and NOT in any other case, thanks.',
                },
                {
                    'name': 'data_dir',
                    'type': 'directory',
                    'description': 'Where cache/logs/etc are stored. Keep empty for defaults.',
                },
                {
                    'name': 'url_base',
                    'default': '',
                    'description': 'When using mod_proxy use this to append the url with this.',
                },
                {
                    'name': 'permission_folder',
                    'default': '0755',
                    'label': 'Folder CHMOD',
                    'description': 'Can be either decimal (493) or octal (leading zero: 0755). <a href="http://permissions-calculator.org/" target="_blank">Calculate the correct value</a>',
                },
                {
                    'name': 'permission_file',
                    'default': '0644',
                    'label': 'File CHMOD',
                    'description': 'See Folder CHMOD description, but for files',
                },
            ],
        },
    ],
}]
