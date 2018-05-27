from couchpotato.core.helpers.encoding import try_url_encode
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.torrentz import Base
from couchpotato.core.media.movie.providers.base import MovieProvider

log = CPLog(__name__)

autoload = 'Torrentz'


class Torrentz(MovieProvider, Base):

    def buildUrl(self, title, media, quality):
        return try_url_encode('%s %s' % (title, media['info']['year']))
