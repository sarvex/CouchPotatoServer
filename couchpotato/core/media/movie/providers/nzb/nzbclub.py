from couchpotato.core.event import fire_event
from couchpotato.core.helpers.encoding import try_url_encode
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.nzb.nzbclub import Base
from couchpotato.core.media.movie.providers.base import MovieProvider

log = CPLog(__name__)

autoload = 'NZBClub'


class NZBClub(MovieProvider, Base):

    def buildUrl(self, media):
        q = try_url_encode({
            'q': '%s' % fire_event('library.query', media, single=True),
        })

        query = try_url_encode({
            'ig': 1,
            'rpp': 200,
            'st': 5,
            'sp': 1,
            'ns': 1,
        })
        return '%s&%s' % (q, query)
