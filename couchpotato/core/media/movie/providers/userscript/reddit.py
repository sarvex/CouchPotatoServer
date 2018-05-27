from couchpotato import fire_event
from couchpotato.core.helpers.variable import split_string
from couchpotato.core.media._base.providers.userscript.base import UserscriptBase

autoload = 'Reddit'


class Reddit(UserscriptBase):

    includes = ['*://www.reddit.com/r/Ijustwatched/comments/*']

    def getMovie(self, url):
        name = split_string(split_string(url, '/ijw_')[-1], '/')[0]

        if name.startswith('ijw_'):
            name = name[4:]

        year_name = fire_event('scanner.name_year', name, single=True)

        return self.search(year_name.get('name'), year_name.get('year'))
