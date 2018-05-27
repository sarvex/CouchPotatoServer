from couchpotato.core.event import add_event
from couchpotato.core.plugins.base import Plugin


class LibraryBase(Plugin):

    _type = None

    def init_type(self):
        add_event('library.types', self.get_type)

    def get_type(self):
        return self._type
