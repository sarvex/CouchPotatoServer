from couchpotato.core.event import fire_event
from couchpotato.core.helpers.encoding import try_url_encode
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.bithdtv import Base
from couchpotato.core.media.movie.providers.base import MovieProvider

log = CPLog(__name__)

autoload = 'BiTHDTV'


class BiTHDTV(MovieProvider, Base):
    cat_ids = [
        ([2], ['bd50']),
    ]
    cat_backup_id = 7 # Movies

    def buildUrl(self, media, quality):
        query = try_url_encode({
            'search': fire_event('library.query', media, single=True),
            'cat': self.getCatId(quality)[0]
        })
        return query
