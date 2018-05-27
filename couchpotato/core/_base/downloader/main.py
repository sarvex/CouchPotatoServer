import random
import re
from base64 import b32decode, b16encode

from couchpotato.api import addApiView
from couchpotato.core.event import add_event
from couchpotato.core.helpers.variable import merge_dictionaries
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.base import Provider
from couchpotato.core.plugins.base import Plugin

log = CPLog(__name__)


## This is here to load the static files
class Downloader(Plugin):
    pass


class DownloaderBase(Provider):
    protocol = []
    http_time_between_calls = 0
    status_support = True

    torrent_sources = [
        'https://torcache.net/torrent/%s.torrent',
        'https://itorrents.org/torrent/%s.torrent',
    ]

    torrent_trackers = [
        'udp://tracker.istole.it:80/announce',
        'http://tracker.istole.it/announce',
        'udp://fr33domtracker.h33t.com:3310/announce',
        'http://tracker.publicbt.com/announce',
        'udp://tracker.publicbt.com:80/announce',
        'http://tracker.ccc.de/announce',
        'udp://tracker.ccc.de:80/announce',
        'http://exodus.desync.com/announce',
        'http://exodus.desync.com:6969/announce',
        'http://tracker.publichd.eu/announce',
        'udp://tracker.publichd.eu:80/announce',
        'http://tracker.openbittorrent.com/announce',
        'udp://tracker.openbittorrent.com/announce',
        'udp://tracker.openbittorrent.com:80/announce',
        'udp://open.demonii.com:1337/announce',
    ]

    def __init__(self):
        add_event('download', self._download)
        add_event('download.enabled', self._is_enabled)
        add_event('download.enabled_protocols', self.get_enabled_protocol)
        add_event('download.status', self._get_all_download_status)
        add_event('download.remove_failed', self._remove_failed)
        add_event('download.pause', self._pause)
        add_event('download.process_complete', self._process_complete)
        addApiView('download.%s.test' % self.getName().lower(), self._test)

    def get_enabled_protocol(self):
        for download_protocol in self.protocol:
            if self.is_enabled(manual=True, data={'protocol': download_protocol}):
                return self.protocol

        return []

    def _download(self, data=None, media=None, manual=False, filedata=None):
        if not media: media = {}
        if not data: data = {}

        if self.is_disabled(manual, data):
            return
        return self.download(data=data, media=media, filedata=filedata)

    def download(self, *args, **kwargs):
        return False

    def _get_all_download_status(self, download_ids):
        if self.is_disabled(manual=True, data={}):
            return

        ids = [download_id['id'] for download_id in download_ids if download_id['downloader'] == self.getName()]

        if ids:
            return self.get_all_download_status(ids)
        else:
            return

    def get_all_download_status(self, ids):
        return []

    def _remove_failed(self, release_download):
        if self.is_disabled(manual=True, data={}):
            return

        if release_download and release_download.get('downloader') == self.getName():
            if self.conf('delete_failed'):
                return self.remove_failed(release_download)

            return False
        return

    def remove_failed(self, release_download):
        return

    def _process_complete(self, release_download):
        if self.is_disabled(manual=True, data={}):
            return

        if release_download and release_download.get('downloader') == self.getName():
            if self.conf('remove_complete', default=False):
                return self.process_complete(release_download=release_download,
                                             delete_files=self.conf('delete_files', default=False))

            return False
        return

    def process_complete(self, release_download, delete_files):
        return

    def is_correct_protocol(self, protocol):
        is_correct = protocol in self.protocol

        if not is_correct:
            log.debug("Downloader doesn't support this protocol")

        return is_correct

    def magnet_to_torrent(self, magnet_link):
        torrent_hash = re.findall('urn:btih:([\w]{32,40})', magnet_link)[0].upper()

        # Convert base 32 to hex
        if len(torrent_hash) == 32:
            torrent_hash = b16encode(b32decode(torrent_hash))

        sources = self.torrent_sources
        random.shuffle(sources)

        for source in sources:
            try:
                filedata = self.urlopen(source % torrent_hash, headers={'Referer': source % torrent_hash},
                                        show_error=False)
                if 'torcache' in filedata and 'file not found' in filedata.lower():
                    continue

                return filedata
            except:
                log.debug('Torrent hash "%s" wasn\'t found on: %s', (torrent_hash, source))

        log.error('Failed converting magnet url to torrent: %s', torrent_hash)
        return False

    def download_return_id(self, download_id):
        return {
            'downloader': self.getName(),
            'status_support': self.status_support,
            'id': download_id
        }

    def is_disabled(self, manual=False, data=None):
        if not data: data = {}

        return not self.is_enabled(manual, data)

    def _is_enabled(self, manual, data=None):
        if not data: data = {}

        if not self.is_enabled(manual, data):
            return
        return True

    def is_enabled(self, manual=False, data=None):
        if not data: data = {}

        d_manual = self.conf('manual', default=False)
        return super(DownloaderBase, self).is_enabled() and \
               (d_manual and manual or d_manual is False) and \
               (not data or self.is_correct_protocol(data.get('protocol')))

    def _test(self, **kwargs):
        t = self.test()
        if isinstance(t, tuple):
            return {'success': t[0], 'msg': t[1]}
        return {'success': t}

    def test(self):
        return False

    def _pause(self, release_download, pause=True):
        if self.is_disabled(manual=True, data={}):
            return

        if release_download and release_download.get('downloader') == self.getName():
            self.pause(release_download, pause)
            return True

        return False

    def pause(self, release_download, pause):
        return


class ReleaseDownloadList(list):
    provider = None

    def __init__(self, provider, **kwargs):
        self.provider = provider
        self.kwargs = kwargs

        super(ReleaseDownloadList, self).__init__()

    def extend(self, results):
        for r in results:
            self.append(r)

    def append(self, result):
        new_result = self.fill_result(result)
        super(ReleaseDownloadList, self).append(new_result)

    def fill_result(self, result):
        defaults = {
            'id': 0,
            'status': 'busy',
            'downloader': self.provider.getName(),
            'folder': '',
            'files': [],
        }

        return merge_dictionaries(defaults, result)
