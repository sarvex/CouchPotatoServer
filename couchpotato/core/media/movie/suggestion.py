import time

from couchpotato.api import addApiView
from couchpotato.core.event import fire_event, add_event
from couchpotato.core.helpers.variable import split_string, remove_duplicate, get_identifier, get_title
from couchpotato.core.plugins.base import Plugin
from couchpotato.environment import Env

autoload = 'Suggestion'


class Suggestion(Plugin):

    def __init__(self):

        addApiView('suggestion.view', self.suggestView)
        addApiView('suggestion.ignore', self.ignoreView)

        def test():
            time.sleep(1)
            self.suggestView()

        add_event('app.load', test)

    def suggestView(self, limit = 6, **kwargs):
        if self.is_disabled():
            return {
                'success': True,
                'movies': []
            }

        movies = split_string(kwargs.get('movies', ''))
        ignored = split_string(kwargs.get('ignored', ''))
        seen = split_string(kwargs.get('seen', ''))

        cached_suggestion = self.getCache('suggestion_cached')
        if cached_suggestion:
            suggestions = cached_suggestion
        else:

            if not movies or len(movies) == 0:
                active_movies = fire_event('media.with_status', ['active', 'done'], types='movie', single=True)
                movies = [get_identifier(x) for x in active_movies]

            if not ignored or len(ignored) == 0:
                ignored = split_string(Env.prop('suggest_ignore', default=''))
            if not seen or len(seen) == 0:
                movies.extend(split_string(Env.prop('suggest_seen', default='')))

            suggestions = fire_event('movie.suggest', movies=movies, ignore=ignored, single=True)
            self.setCache('suggestion_cached', suggestions, timeout = 6048000)  # Cache for 10 weeks

        medias = []
        for suggestion in suggestions[:int(limit)]:

            # Cache poster
            posters = suggestion.get('images', {}).get('poster', [])
            poster = [x for x in posters if 'tmdb' in x]
            posters = poster if len(poster) > 0 else posters

            cached_poster = fire_event('file.download', url=posters[0], single=True) if len(posters) > 0 else False
            files = {'image_poster': [cached_poster] } if cached_poster else {}

            medias.append({
                'status': 'suggested',
                'title': get_title(suggestion),
                'type': 'movie',
                'info': suggestion,
                'files': files,
                'identifiers': {
                    'imdb': suggestion.get('imdb')
                }
            })

        return {
            'success': True,
            'movies': medias
        }

    def ignoreView(self, imdb = None, limit = 6, remove_only = False, mark_seen = False, **kwargs):

        ignored = split_string(Env.prop('suggest_ignore', default=''))
        seen = split_string(Env.prop('suggest_seen', default=''))

        new_suggestions = []
        if imdb:
            if mark_seen:
                seen.append(imdb)
                Env.prop('suggest_seen', ','.join(set(seen)))
            elif not remove_only:
                ignored.append(imdb)
                Env.prop('suggest_ignore', ','.join(set(ignored)))

            new_suggestions = self.updateSuggestionCache(ignore_imdb = imdb, limit = limit, ignored = ignored, seen = seen)

        if len(new_suggestions) <= limit:
            return {
                'result': False
            }

        # Only return new (last) item
        media = {
            'status': 'suggested',
            'title': get_title(new_suggestions[limit]),
            'type': 'movie',
            'info': new_suggestions[limit],
            'identifiers': {
                'imdb': new_suggestions[limit].get('imdb')
            }
        }

        return {
            'result': True,
            'movie': media
        }

    def updateSuggestionCache(self, ignore_imdb = None, limit = 6, ignored = None, seen = None):

        # Combine with previous suggestion_cache
        cached_suggestion = self.getCache('suggestion_cached') or []
        new_suggestions = []
        ignored = [] if not ignored else ignored
        seen = [] if not seen else seen

        if ignore_imdb:
            suggested_imdbs = []
            for cs in cached_suggestion:
                if cs.get('imdb') != ignore_imdb and cs.get('imdb') not in suggested_imdbs:
                    suggested_imdbs.append(cs.get('imdb'))
                    new_suggestions.append(cs)

        # Get new results and add them
        if len(new_suggestions) - 1 < limit:
            active_movies = fire_event('media.with_status', ['active', 'done'], single=True)
            movies = [get_identifier(x) for x in active_movies]
            movies.extend(seen)

            ignored.extend([x.get('imdb') for x in cached_suggestion])
            suggestions = fire_event('movie.suggest', movies=movies, ignore=remove_duplicate(ignored), single=True)

            if suggestions:
                new_suggestions.extend(suggestions)

        self.setCache('suggestion_cached', new_suggestions, timeout = 3024000)

        return new_suggestions

config = [{
    'name': 'suggestion',
    'groups': [
        {
            'label': 'Suggestions',
            'description': 'Displays suggestions on the home page',
            'name': 'suggestions',
            'tab': 'display',
            'options': [
                {
                    'name': 'enabled',
                    'default': True,
                    'type': 'enabler',
                },
            ],
        },
    ],
}]
