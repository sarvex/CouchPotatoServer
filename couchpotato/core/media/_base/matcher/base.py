from couchpotato.core.event import add_event
from couchpotato.core.helpers.encoding import simplify_string
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin

log = CPLog(__name__)


class MatcherBase(Plugin):
    type = None

    def __init__(self):
        if self.type:
            add_event('%s.matcher.correct' % self.type, self.correct)

    def correct(self, chain, release, media, quality):
        raise NotImplementedError()

    def flatten_info(self, info):
        # Flatten dictionary of matches (chain info)
        if isinstance(info, dict):
            return dict([(key, self.flatten_info(value)) for key, value in list(info.items())])

        # Flatten matches
        result = None

        for match in info:
            if isinstance(match, dict):
                if result is None:
                    result = {}

                for key, value in list(match.items()):
                    if key not in result:
                        result[key] = []

                    result[key].append(value)
            else:
                if result is None:
                    result = []

                result.append(match)

        return result

    def construct_from_raw(self, match):
        if not match:
            return None

        parts = [
            ''.join([
                y for y in x[1:] if y
            ]) for x in match
        ]

        return ''.join(parts)[:-1].strip()

    def simplify_value(self, value):
        if not value:
            return value

        if isinstance(value, str):
            return simplify_string(value)

        if isinstance(value, list):
            return [self.simplify_value(x) for x in value]

        raise ValueError("Unsupported value type")

    def chain_match(self, chain, group, tags):
        info = self.flatten_info(chain.info[group])

        found_tags = []
        for tag, accepted in list(tags.items()):
            values = [self.simplify_value(x) for x in info.get(tag, [None])]

            if any([val in accepted for val in values]):
                found_tags.append(tag)

        log.debug('tags found: %s, required: %s' % (found_tags, list(tags.keys())))

        if set(tags.keys()) == set(found_tags):
            return True

        return all([key in found_tags for key, value in list(tags.items())])
