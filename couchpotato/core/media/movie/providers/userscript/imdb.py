from couchpotato.core.helpers.variable import get_imdb
from couchpotato.core.media._base.providers.userscript.base import UserscriptBase

autoload = 'IMDB'


class IMDB(UserscriptBase):

    includes = ['*://*.imdb.com/title/tt*', '*://imdb.com/title/tt*']

    def getMovie(self, url):
        return self.getInfo(get_imdb(url))
