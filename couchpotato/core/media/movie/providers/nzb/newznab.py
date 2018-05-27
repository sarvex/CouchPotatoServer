from couchpotato.core.helpers.encoding import try_url_encode
from couchpotato.core.helpers.variable import get_identifier
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.nzb.newznab import Base
from couchpotato.core.media.movie.providers.base import MovieProvider

log = CPLog(__name__)

autoload = 'Newznab'


class Newznab(MovieProvider, Base):

    def buildUrl(self, media, host):

        query = try_url_encode({
            't': 'movie',
            'imdbid': get_identifier(media).replace('tt', ''),
            'apikey': host['api_key'],
            'extended': 1
        })

        if len(host.get('custom_tag', '')) > 0:
            query = '%s&%s' % (query, host.get('custom_tag'))

        if len(host['custom_category']) > 0:
            query = '%s&cat=%s' % (query, host['custom_category'])

        return query
