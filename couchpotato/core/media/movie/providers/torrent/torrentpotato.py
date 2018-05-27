from couchpotato.core.helpers.encoding import try_url_encode
from couchpotato.core.helpers.variable import get_identifier
from couchpotato.core.helpers.variable import get_title
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.torrentpotato import Base
from couchpotato.core.media.movie.providers.base import MovieProvider

log = CPLog(__name__)

autoload = 'TorrentPotato'


class TorrentPotato(MovieProvider, Base):

    def buildUrl(self, media, host):
        arguments = try_url_encode({
            'user': host['name'],
            'passkey': host['pass_key'],
            'imdbid': get_identifier(media),
            'search': get_title(media) + ' ' + str(media['info']['year']),
        })
        return '%s?%s' % (host['host'], arguments)
