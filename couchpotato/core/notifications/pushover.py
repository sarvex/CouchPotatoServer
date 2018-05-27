from couchpotato.core.helpers.encoding import to_unicode
from couchpotato.core.helpers.variable import get_title, get_identifier
from couchpotato.core.logger import CPLog
from couchpotato.core.notifications.base import Notification


log = CPLog(__name__)

autoload = 'Pushover'


class Pushover(Notification):

    api_url = 'https://api.pushover.net'

    def notify(self, message = '', data = None, listener = None):
        if not data: data = {}

        api_data = {
            'user': self.conf('user_key'),
            'token': self.conf('api_token'),
            'message': to_unicode(message),
            'priority': self.conf('priority'),
            'sound': self.conf('sound'),
        }

        if data and get_identifier(data):
            api_data.update({
                'url': to_unicode('http://www.imdb.com/title/%s/' % get_identifier(data)),
                'url_title': to_unicode('%s on IMDb' % get_title(data)),
            })

        try:
            data = self.urlopen('%s/%s' % (self.api_url, '1/messages.json'),
                headers = {'Content-type': 'application/x-www-form-urlencoded'},
                data = api_data)
            log.info2('Pushover responded with: %s', data)
            return True
        except:
            return False



config = [{
    'name': 'pushover',
    'groups': [
        {
            'tab': 'notifications',
            'list': 'notification_providers',
            'name': 'pushover',
            'options': [
                {
                    'name': 'enabled',
                    'default': 0,
                    'type': 'enabler',
                },
                {
                    'name': 'user_key',
                    'description': 'Register on pushover.net to get one.'
                },
                {
                    'name': 'api_token',
                    'description': '<a href="https://pushover.net/apps/clone/couchpotato" target="_blank">Register on pushover.net</a> to get one.',
                    'advanced': True,
                    'default': 'YkxHMYDZp285L265L3IwH3LmzkTaCy',
                },
                {
                    'name': 'priority',
                    'default': 0,
                    'type': 'dropdown',
                    'values': [('Lowest', -2), ('Low', -1), ('Normal', 0), ('High', 1)],
                },
                {
                    'name': 'on_snatch',
                    'default': 0,
                    'type': 'bool',
                    'advanced': True,
                    'description': 'Also send message when movie is snatched.',
                },
                {
                    'name': 'sound',
                    'advanced': True,
                    'description': 'Define <a href="https://pushover.net/api%23sounds" target="_blank">custom sound</a> for Pushover alert.'
                },
            ],
        }
    ],
}]
