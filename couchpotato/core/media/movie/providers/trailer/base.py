from couchpotato.core.event import add_event
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.base import Provider

log = CPLog(__name__)


class TrailerProvider(Provider):

    type = 'trailer'

    def __init__(self):
        add_event('trailer.search', self.search)

    def search(self, *args, **kwargs):
        pass
