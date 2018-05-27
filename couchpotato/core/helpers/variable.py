import collections
import ctypes
import hashlib
import os
import platform
import random
import re
import string
import sys
import traceback

from six.moves import map

from couchpotato.core.helpers.encoding import simplify_string, to_safe_string, ss, sp, to_unicode
from couchpotato.core.logger import CPLog

log = CPLog(__name__)


def fn_escape(pattern):
    return pattern.replace('[', '[[').replace(']', '[]]').replace('[[', '[[]')


def link(src, dst):
    if os.name == 'nt':
        import ctypes
        if ctypes.windll.kernel32.CreateHardLinkW(to_unicode(dst), to_unicode(src), 0) == 0: raise ctypes.WinError()
    else:
        os.link(to_unicode(src), to_unicode(dst))


def symlink(src, dst):
    if os.name == 'nt':
        import ctypes
        if ctypes.windll.kernel32.CreateSymbolicLinkW(to_unicode(dst), to_unicode(src),
                                                      1 if os.path.isdir(src) else 0) in [0,
                                                                                          1280]: raise ctypes.WinError()
    else:
        os.symlink(to_unicode(src), to_unicode(dst))


def get_user_directory():
    try:
        import pwd
        if not os.environ['HOME']:
            os.environ['HOME'] = sp(pwd.getpwuid(os.geteuid()).pw_dir)
    except:
        pass

    return sp(os.path.expanduser('~'))


def get_download_directory():
    user_dir = get_user_directory()

    # OSX
    if 'darwin' in platform.platform().lower():
        return os.path.join(user_dir, 'Downloads')

    if os.name == 'nt':
        return os.path.join(user_dir, 'Downloads')

    return user_dir


def get_data_directory():

    # Windows
    if os.name == 'nt':
        return os.path.join(os.environ['APPDATA'], 'CouchPotato')

    user_dir = get_user_directory()

    # OSX
    if 'darwin' in platform.platform().lower():
        return os.path.join(user_dir, 'Library', 'Application Support', 'CouchPotato')

    # FreeBSD
    if 'freebsd' in sys.platform:
        return os.path.join('/usr/local/', 'couchpotato', 'data')

    # Linux
    return os.path.join(user_dir, '.couchpotato')


def is_dictionary(obj):
    return isinstance(obj, dict)


def merge_dictionaries(a, b, prepend_list=False):
    assert is_dictionary(a), is_dictionary(b)
    dst = a.copy()

    stack = [(dst, b)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                current_dst[key] = current_src[key]
            else:
                if is_dictionary(current_src[key]) and is_dictionary(current_dst[key]):
                    stack.append((current_dst[key], current_src[key]))
                elif isinstance(current_src[key], list) and isinstance(current_dst[key], list):
                    current_dst[key] = current_src[key] + current_dst[key] if prepend_list else current_dst[key] + current_src[key]
                    current_dst[key] = remove_list_duplicates(current_dst[key])
                else:
                    current_dst[key] = current_src[key]
    return dst


def remove_list_duplicates(seq):
    checked = []
    for e in seq:
        if e not in checked:
            checked.append(e)
    return checked


def flatten_list(l):
    if isinstance(l, list):
        return sum(map(flatten_list, l))
    else:
        return l


def md5(text):
    return hashlib.md5(ss(text)).hexdigest()


def sha1(text):
    return hashlib.sha1(text).hexdigest()


def is_local_ip(ip):
    ip = ip.lstrip('htps:/')
    regex = '/(^127\.)|(^192\.168\.)|(^10\.)|(^172\.1[6-9]\.)|(^172\.2[0-9]\.)|(^172\.3[0-1]\.)|(^::1)$/'
    return re.search(regex, ip) is not None or 'localhost' in ip or ip[:4] == '127.'


def get_extension(filename):
    return os.path.splitext(filename)[1][1:]


def clean_host(host, protocol=True, ssl=False, username=None, password=None):
    """Return a cleaned up host with given url options set

    Changes protocol to https if ssl is set to True and http if ssl is set to false.
    >>> clean_host("localhost:80", ssl=True)
    'https://localhost:80/'
    >>> clean_host("localhost:80", ssl=False)
    'http://localhost:80/'

    Username and password is managed with the username and password variables
    >>> clean_host("localhost:80", username="user", password="passwd")
    'http://user:passwd@localhost:80/'

    Output without scheme (protocol) can be forced with protocol=False
    >>> clean_host("localhost:80", protocol=False)
    'localhost:80'
    """

    if not '://' in host and protocol:
        host = ('https://' if ssl else 'http://') + host

    if not protocol:
        host = host.split('://', 1)[-1]

    if protocol and username and password:
        try:
            auth = re.findall('^(?:.+?//)(.+?):(.+?)@(?:.+)$', host)
            if auth:
                log.error('Cleanhost error: auth already defined in url: %s, please remove BasicAuth from url.', host)
            else:
                host = host.replace('://', '://%s:%s@' % (username, password), 1)
        except:
            pass

    host = host.rstrip('/ ')
    if protocol:
        host += '/'

    return host


def get_imdb(txt, check_inside=False, multiple=False):

    if not check_inside:
        txt = simplify_string(txt)
    else:
        txt = ss(txt)

    if check_inside and os.path.isfile(txt):
        output = open(txt, 'r')
        txt = output.read()
        output.close()

    try:
        ids = re.findall('(tt\d{4,7})', txt)

        if multiple:
            return remove_duplicate(['tt%07d' % try_int(x[2:]) for x in ids]) if len(ids) > 0 else []

        return 'tt%07d' % try_int(ids[0][2:])
    except IndexError:
        pass

    return False


def try_int(s, default=0):
    try: return int(s)
    except: return default


def try_float(s):
    try:
        if isinstance(s, str):
            return float(s) if '.' in s else try_int(s)
        else:
            return float(s)
    except: return 0


def nat_sort_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def to_iterable(value):
    if isinstance(value, collections.Iterable):
        return value
    return [value]


def get_identifier(media):
    return media.get('identifier') or media.get('identifiers', {}).get('imdb')


def get_title(media_dict):
    try:
        try:
            return media_dict['title']
        except:
            try:
                return media_dict['titles'][0]
            except:
                try:
                    return media_dict['info']['titles'][0]
                except:
                    try:
                        return media_dict['media']['info']['titles'][0]
                    except:
                        log.error('Could not get title for %s', get_identifier(media_dict))
                        return None
    except:
        log.error('Could not get title for library item: %s', media_dict)
        return None


def possible_titles(raw_title):

    titles = [
        to_safe_string(raw_title).lower(),
        raw_title.lower(),
        simplify_string(raw_title)
    ]

    # replace some chars
    new_title = raw_title.replace('&', 'and')
    titles.append(simplify_string(new_title))

    return remove_duplicate(titles)


def random_string(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def split_string(str, split_on=',', clean=True):
    l = [x.strip() for x in str.split(split_on)] if str else []
    return remove_empty(l) if clean else l


def remove_empty(l):
    return list([_f for _f in l if _f])


def remove_duplicate(l):
    seen = set()
    return [x for x in l if x not in seen and not seen.add(x)]


def dictionary_is_subset(a, b):
    return all([k in b and b[k] == v for k, v in list(a.items())])


# Returns True if sub_folder is the same as or inside base_folder
def is_sub_folder(sub_folder, base_folder):
    if base_folder and sub_folder:
        base = sp(os.path.realpath(base_folder)) + os.path.sep
        subfolder = sp(os.path.realpath(sub_folder)) + os.path.sep
        return os.path.commonprefix([subfolder, base]) == base

    return False


# From SABNZBD
re_password = [re.compile(r'(.+){{([^{}]+)}}$'), re.compile(r'(.+)\s+password\s*=\s*(.+)$', re.I)]


def scan_for_password(name):
    m = None
    for reg in re_password:
        m = reg.search(name)
        if m: break

    if m:
        return m.group(1).strip('. '), m.group(2).strip()


under_pat = re.compile(r'_([a-z])')


def snake_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def remove_pyc(folder, only_excess=True, show_logs=True):

    folder = sp(folder)

    for root, dirs, files in os.walk(folder):

        pyc_files = [filename for filename in files if filename.endswith('.pyc')]
        py_files = set([filename for filename in files if filename.endswith('.py')])
        excess_pyc_files = [pyc_filename for pyc_filename in pyc_files if
                            pyc_filename[:-1] not in py_files] if only_excess else pyc_files

        for excess_pyc_file in excess_pyc_files:
            full_path = os.path.join(root, excess_pyc_file)
            if show_logs: log.debug('Removing old PYC file: %s', full_path)
            try:
                os.remove(full_path)
            except:
                log.error('Couldn\'t remove %s: %s', (full_path, traceback.format_exc()))

        for dir_name in dirs:
            full_path = os.path.join(root, dir_name)
            if len(os.listdir(full_path)) == 0:
                try:
                    os.rmdir(full_path)
                except:
                    log.error('Couldn\'t remove empty directory %s: %s', (full_path, traceback.format_exc()))


def get_free_space(directories):

    single = not isinstance(directories, (tuple, list))
    if single:
        directories = [directories]

    free_space = {}
    for folder in directories:

        size = None
        if os.path.isdir(folder):
            if os.name == 'nt':
                _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), \
                                   ctypes.c_ulonglong()
                if sys.version_info >= (3,) or isinstance(folder, str):
                    fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW #@UndefinedVariable
                else:
                    fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA #@UndefinedVariable
                ret = fun(folder, ctypes.byref(_), ctypes.byref(total), ctypes.byref(free))
                if ret == 0:
                    raise ctypes.WinError()
                return [total.value, free.value]
            else:
                s = os.statvfs(folder)
                size = [s.f_blocks * s.f_frsize / (1024 * 1024), (s.f_bavail * s.f_frsize) / (1024 * 1024)]

        if single: return size

        free_space[folder] = size

    return free_space


def get_size(paths):

    single = not isinstance(paths, (tuple, list))
    if single:
        paths = [paths]

    total_size = 0
    for path in paths:
        path = sp(path)

        if os.path.isdir(path):
            total_size = 0
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    total_size += os.path.getsize(sp(os.path.join(dirpath, f)))

        elif os.path.isfile(path):
            total_size += os.path.getsize(path)

    return total_size / 1048576 # MB


def find(func, iterable):
    for item in iterable:
        if func(item):
            return item

    return None


def compare_versions(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))
