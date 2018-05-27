from couchpotato.core.helpers.encoding import to_unicode
from couchpotato.core.helpers.encoding import try_url_encode
from couchpotato.core.helpers.variable import split_string
from couchpotato.core.logger import CPLog
from couchpotato.core.notifications.base import Notification


log = CPLog(__name__)

autoload = 'Join'


class Join(Notification):

    # URL for request
    url = 'https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?title=%s&text=%s&deviceId=%s&icon=%s'

    # URL for notification icon
    icon = try_url_encode(
        'https://raw.githubusercontent.com/CouchPotato/CouchPotatoServer/master/couchpotato/static/images/icons/android.png')

    def notify(self, message = '', data = None, listener = None):
        if not data: data = {}

        # default for devices
        device_default = [None]

        apikey = self.conf('apikey')
        if apikey is not None:
            # Add apikey to request url
            self.url = self.url + '&apikey=' + apikey
            # If api key is present, default to sending to all devices
            device_default = ['group.all']

        devices = self.getDevices() or device_default
        successful = 0
        for device in devices:
            response = self.urlopen(
                self.url % (self.default_title, try_url_encode(to_unicode(message)), device, self.icon))

            if response:
                successful += 1
            else:
                log.error('Unable to push notification to Join device with ID %s' % device)

        return successful == len(devices)

    def getDevices(self):
        return split_string(self.conf('devices'))


config = [{
    'name': 'join',
    'groups': [
        {
            'tab': 'notifications',
            'list': 'notification_providers',
            'name': 'join',
            'options': [
                {
                    'name': 'enabled',
                    'default': 0,
                    'type': 'enabler',
                },
                {
                    'name': 'devices',
                    'default': '',
                    'description': 'IDs of devices to notify, or group to send to if API key is specified (ex: group.all)'
                },
                {
                    'name': 'apikey',
                    'default': '',
                    'advanced': True,
                    'description': 'API Key for sending to all devices, or group'
                },
                {
                    'name': 'on_snatch',
                    'default': 0,
                    'type': 'bool',
                    'advanced': True,
                    'description': 'Also send message when movie is snatched.',
                },
            ],
        }
    ],
}]
