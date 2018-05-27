import os
import re
import traceback
import unicodedata
from string import ascii_letters, digits
from urllib.parse import quote_plus

import six
from chardet import detect

from couchpotato.core.logger import CPLog

log = CPLog(__name__)


def to_safe_string(original):
    valid_chars = "-_.() %s%s" % (ascii_letters, digits)
    cleaned_filename = unicodedata.normalize('NFKD', to_unicode(original)).encode('ASCII', 'ignore')
    valid_string = ''.join(c for c in cleaned_filename if c in valid_chars)
    return ' '.join(valid_string.split())


def simplify_string(original):
    string = strip_accents(original.lower())
    string = to_safe_string(' '.join(re.split('\W+', string)))
    split = re.split('\W+|_', string.lower())
    return to_unicode(' '.join(split))


def to_unicode(original, *args):
    try:
        if isinstance(original, str):
            return original
        else:
            try:
                return six.text_type(original, *args)
            except:
                try:
                    from couchpotato.environment import Env
                    return original.decode(Env.get("encoding"))
                except:
                    try:
                        detected = detect(original)
                        try:
                            if detected.get('confidence') > 0.8:
                                return original.decode(detected.get('encoding'))
                        except:
                            pass

                        return ek(original, *args)
                    except:
                        raise
    except:
        log.error('Unable to decode value "%s..." : %s ', (repr(original)[:20], traceback.format_exc()))
        return 'ERROR DECODING STRING'


def ss(original, *args):
    u_original = to_unicode(original, *args)
    try:
        from couchpotato.environment import Env
        return u_original.encode(Env.get('encoding'))
    except Exception as e:
        log.debug('Failed ss encoding char, force UTF8: %s', e)
        try:
            return u_original.encode(Env.get('encoding'), 'replace')
        except:
            return u_original.encode('utf-8', 'replace')


def sp(path, *args):

    # Standardise encoding, normalise case, path and strip trailing '/' or '\'
    if not path or len(path) == 0:
        return path

    # convert windows path (from remote box) to *nix path
    if os.path.sep == '/' and '\\' in path:
        path = '/' + path.replace(':', '').replace('\\', '/')

    path = os.path.normpath(ss(path, *args))

    # Remove any trailing path separators
    if path != os.path.sep:
        path = path.rstrip(os.path.sep)

    # Add a trailing separator in case it is a root folder on windows (crashes guessit)
    if len(path) == 2 and path[1] == ':':
        path = path + os.path.sep

    # Replace *NIX ambiguous '//' at the beginning of a path with '/' (crashes guessit)
    path = re.sub('^//', '/', path)

    return path


def ek(original, *args):
    if isinstance(original, str):
        try:
            from couchpotato.environment import Env
            return original.decode(Env.get('encoding'), 'ignore')
        except UnicodeDecodeError:
            raise

    return original


def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', to_unicode(s)) if unicodedata.category(c) != 'Mn'))


def try_url_encode(s):
    new = six.u('')
    if isinstance(s, dict):
        for key, value in list(s.items()):
            new += six.u('&%s=%s') % (key, try_url_encode(value))

        return new[1:]
    else:
        for letter in ss(s):
            try:
                new += quote_plus(letter)
            except:
                new += letter

    return new
