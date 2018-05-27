import os

from couchpotato.core.event import add_event
from couchpotato.core.helpers.variable import try_int
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
from couchpotato.environment import Env

log = CPLog(__name__)

autoload = 'ClientScript'


class ClientScript(Plugin):

    paths = {
        'style': [
            'style/combined.min.css',
        ],
        'script': [
            'scripts/combined.vendor.min.js',
            'scripts/combined.base.min.js',
            'scripts/combined.plugins.min.js',
        ],
    }

    def __init__(self):
        add_event('clientscript.get_styles', self.get_styles)
        add_event('clientscript.get_scripts', self.get_scripts)

        self.make_relative()

    def make_relative(self):

        for static_type in self.paths:

            updates_paths = []
            for rel_path in self.paths.get(static_type):
                file_path = os.path.join(Env.get('app_dir'), 'couchpotato', 'static', rel_path)
                core_url = 'static/%s?%d' % (rel_path, try_int(os.path.getmtime(file_path)))

                updates_paths.append(core_url)

            self.paths[static_type] = updates_paths

    def get_styles(self, *args, **kwargs):
        return self.get('style', *args, **kwargs)

    def get_scripts(self, *args, **kwargs):
        return self.get('script', *args, **kwargs)

    def get(self, type):
        if type in self.paths:
            return self.paths[type]

        return []
