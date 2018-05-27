from couchpotato.core.event import add_event
from couchpotato.core.helpers.encoding import to_unicode
from couchpotato.core.helpers.variable import get_title, split_string, remove_duplicate
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
from couchpotato.core.plugins.score.scores import nameScore, nameRatioScore, \
    sizeScore, providerScore, duplicateScore, partialIgnoredScore, namePositionScore, \
    halfMultipartScore, sceneScore
from couchpotato.environment import Env

log = CPLog(__name__)


class Score(Plugin):

    def __init__(self):
        add_event('score.calculate', self.calculate)

    def calculate(self, nzb, movie):
        """ Calculate the score of a NZB, used for sorting later """

        # Merge global and category
        preferred_words = split_string(Env.setting('preferred_words', section='searcher').lower())
        try:
            preferred_words = remove_duplicate(preferred_words + split_string(movie['category']['preferred'].lower()))
        except: pass

        score = nameScore(to_unicode(nzb['name']), movie['info']['year'], preferred_words)

        for movie_title in movie['info']['titles']:
            score += nameRatioScore(to_unicode(nzb['name']), to_unicode(movie_title))
            score += namePositionScore(to_unicode(nzb['name']), to_unicode(movie_title))

        score += sizeScore(nzb['size'])

        # Torrents only
        if nzb.get('seeders'):
            try:
                score += nzb.get('seeders') * 100 / 15
                score += nzb.get('leechers') * 100 / 30
            except:
                pass

        # Provider score
        score += providerScore(nzb['provider'])

        # Duplicates in name
        score += duplicateScore(nzb['name'], get_title(movie))

        # Merge global and category
        ignored_words = split_string(Env.setting('ignored_words', section='searcher').lower())
        try:
            ignored_words = remove_duplicate(ignored_words + split_string(movie['category']['ignored'].lower()))
        except: pass

        # Partial ignored words
        score += partialIgnoredScore(nzb['name'], get_title(movie), ignored_words)

        # Ignore single downloads from multipart
        score += halfMultipartScore(nzb['name'])

        # Extra provider specific check
        extra_score = nzb.get('extra_score')
        if extra_score:
            score += extra_score(nzb)

        # Scene / Nuke scoring
        score += sceneScore(nzb['name'])

        return score
