import os

from couchpotato.core.database import Database
from couchpotato.core.event import fire_event, add_event
from couchpotato.core.helpers.encoding import to_unicode
from couchpotato.core.loader import Loader
from couchpotato.core.settings import Settings
from couchpotato.core.softchroot import SoftChroot


class Env(object):

    _appname = 'CouchPotato'

    ''' Environment variables '''
    _app = None
    _encoding = 'UTF-8'
    _debug = False
    _dev = False
    _settings = Settings()
    _database = Database()
    _loader = Loader()
    _softchroot = SoftChroot()
    _cache = None
    _options = None
    _args = None
    _quiet = False
    _daemonized = False
    _desktop = None
    _http_opener = None

    ''' Data paths and directories '''
    _app_dir = ""
    _data_dir = ""
    _cache_dir = ""
    _db = ""
    _log_path = ""

    @staticmethod
    def doDebug():
        return Env._debug

    @staticmethod
    def get(attr, str=False):
        if str:
            return to_unicode(getattr(Env, '_' + attr))
        else:
            return getattr(Env, '_' + attr)

    @staticmethod
    def all():
        ret = ''
        for attr in ['encoding', 'debug', 'args', 'app_dir', 'data_dir', 'desktop', 'options']:
            ret += '%s=%s ' % (attr, Env.get(attr))

        return ret

    @staticmethod
    def set(attr, value):
        return setattr(Env, '_' + attr, value)

    @staticmethod
    def setting(attr, section = 'core', value = None, default = '', type = None):

        s = Env.get('settings')

        # Return setting
        if value is None:
            return s.get(attr, default = default, section = section, type = type)

        # Set setting
        s.add_section(section)
        s.set(section, attr, value)
        s.save()

        return s

    @staticmethod
    def prop(identifier, value = None, default = None):
        s = Env.get('settings')
        if value is None:
            v = s.get_property(identifier)
            return v if v else default

        s.set_property(identifier, value)

    @staticmethod
    def getPermission(setting_type):
        perm = Env.get('settings').get('permission_%s' % setting_type, default = '0777')
        if perm[0] == '0':
            return int(perm, 8)
        else:
            return int(perm)

    @staticmethod
    def fireEvent(*args, **kwargs):
        return fire_event(*args, **kwargs)

    @staticmethod
    def addEvent(*args, **kwargs):
        return add_event(*args, **kwargs)

    @staticmethod
    def getPid():
        try:
            try:
                parent = os.getppid()
            except:
                parent = None
            return '%d %s' % (os.getpid(), '(%d)' % parent if parent and parent > 1 else '')
        except:
            return 0

    @staticmethod
    def getIdentifier():
        return '%s %s' % (Env.get('appname'), fire_event('app.version', single=True))
