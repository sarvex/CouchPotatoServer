from couchpotato.core.helpers.encoding import try_url_encode
from couchpotato.core.helpers.variable import get_identifier
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.nzb.binsearch import Base
from couchpotato.core.media.movie.providers.base import MovieProvider
from couchpotato.environment import Env

log = CPLog(__name__)

autoload = 'BinSearch'


class BinSearch(MovieProvider, Base):

    def buildUrl(self, media, quality):
        query = try_url_encode({
            'q': get_identifier(media),
            'm': 'n',
            'max': 400,
            'adv_age': Env.setting('retention', 'nzb'),
            'adv_sort': 'date',
            'adv_col': 'on',
            'adv_nfo': 'on',
            'xminsize': quality.get('size_min'),
            'xmaxsize': quality.get('size_max'),
        })
        return query
