from couchpotato.core.event import fire_event, add_event
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
from couchpotato.environment import Env

log = CPLog(__name__)

autoload = 'Desktop'


if Env.get('desktop'):

    class Desktop(Plugin):

        def __init__(self):

            desktop = Env.get('desktop')
            desktop.setSettings({
                'base_url': fire_event('app.base_url', single=True),
                'api_url': fire_event('app.api_url', single=True),
                'api': Env.setting('api'),
            })

            # Events from desktop
            desktop.addEvents({
                'onClose': self.on_close,
            })

            # Events to desktop
            add_event('app.after_shutdown', desktop.afterShutdown)
            add_event('app.load', desktop.onAppLoad, priority=110)

        def on_close(self, event):
            return fire_event('app.shutdown', single=True)

else:

    class Desktop(Plugin):
        pass
