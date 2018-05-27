import threading
import time
import traceback
import uuid
from operator import itemgetter

from CodernityDB.database import RecordDeleted
from tornado.ioloop import IOLoop

from couchpotato import get_db
from couchpotato.api import addApiView, addNonBlockApiView
from couchpotato.core.event import add_event, fire_event
from couchpotato.core.helpers.encoding import to_unicode
from couchpotato.core.helpers.variable import try_int, split_string
from couchpotato.core.logger import CPLog
from couchpotato.core.notifications.base import Notification
from couchpotato.environment import Env
from .index import NotificationIndex, NotificationUnreadIndex

log = CPLog(__name__)


class CoreNotifier(Notification):

    _database = {
        'notification': NotificationIndex,
        'notification_unread': NotificationUnreadIndex
    }

    m_lock = None

    listen_to = [
        'media.available',
        'renamer.after', 'movie.snatched',
        'updater.available', 'updater.updated',
        'core.message', 'core.message.important',
    ]

    def __init__(self):
        super(CoreNotifier, self).__init__()

        add_event('notify', self.notify)
        add_event('notify.frontend', self.frontend)

        addApiView('notification.markread', self.markAsRead, docs = {
            'desc': 'Mark notifications as read',
            'params': {
                'ids': {'desc': 'Notification id you want to mark as read. All if ids is empty.', 'type': 'int (comma separated)'},
            },
        })

        addApiView('notification.list', self.listView, docs = {
            'desc': 'Get list of notifications',
            'params': {
                'limit_offset': {'desc': 'Limit and offset the notification list. Examples: "50" or "50,30"'},
            },
            'return': {'type': 'object', 'example': """{
    'success': True,
    'empty': bool, any notification returned or not,
    'notifications': array, notifications found,
}"""}
        })

        addNonBlockApiView('notification.listener', (self.addListener, self.removeListener))
        addApiView('notification.listener', self.listener)

        fire_event('schedule.interval', 'core.check_messages', self.checkMessages, hours=12, single=True)
        fire_event('schedule.interval', 'core.clean_messages', self.cleanMessages, seconds=15, single=True)

        add_event('app.load', self.clean)

        if not Env.get('dev'):
            add_event('app.load', self.checkMessages)

        self.messages = []
        self.listeners = []
        self.m_lock = threading.Lock()

    def clean(self):
        try:
            db = get_db()
            for n in db.all('notification', with_doc = True):
                if n['doc'].get('time', 0) <= (int(time.time()) - 2419200):
                    db.delete(n['doc'])
        except:
            log.error('Failed cleaning notification: %s', traceback.format_exc())

    def markAsRead(self, ids = None, **kwargs):

        ids = split_string(ids) if ids else None

        try:
            db = get_db()
            for x in db.all('notification_unread', with_doc = True):
                if not ids or x['_id'] in ids:
                    x['doc']['read'] = True
                    db.update(x['doc'])
            return {
                'success': True
            }
        except:
            log.error('Failed mark as read: %s', traceback.format_exc())

        return {
            'success': False
        }

    def listView(self, limit_offset = None, **kwargs):

        db = get_db()

        if limit_offset:
            splt = split_string(limit_offset)
            limit = try_int(splt[0])
            offset = try_int(0 if len(splt) is 1 else splt[1])
            results = db.all('notification', limit = limit, offset = offset, with_doc = True)
        else:
            results = db.all('notification', limit = 200, with_doc = True)

        notifications = []
        for n in results:
            notifications.append(n['doc'])

        return {
            'success': True,
            'empty': len(notifications) == 0,
            'notifications': notifications
        }

    def checkMessages(self):

        prop_name = 'messages.last_check'
        last_check = try_int(Env.prop(prop_name, default=0))

        messages = fire_event('cp.messages', last_check=last_check, single=True) or []

        for message in messages:
            if message.get('time') > last_check:
                message['sticky'] = True  # Always sticky core messages

                message_type = 'core.message.important' if message.get('important') else 'core.message'
                fire_event(message_type, message=message.get('message'), data=message)

            if last_check < message.get('time'):
                last_check = message.get('time')

        Env.prop(prop_name, value = last_check)

    def notify(self, message = '', data = None, listener = None):
        if not data: data = {}

        n = {
            '_t': 'notification',
            'time': int(time.time()),
        }

        try:
            db = get_db()

            n['message'] = to_unicode(message)

            if data.get('sticky'):
                n['sticky'] = True
            if data.get('important'):
                n['important'] = True

            db.insert(n)

            self.frontend(type = listener, data = n)

            return True
        except:
            log.error('Failed notify "%s": %s', (n, traceback.format_exc()))

    def frontend(self, type = 'notification', data = None, message = None):
        if not data: data = {}

        log.debug('Notifying frontend')

        self.m_lock.acquire()
        notification = {
            'message_id': str(uuid.uuid4()),
            'time': time.time(),
            'type': type,
            'data': data,
            'message': message,
        }
        self.messages.append(notification)

        while len(self.listeners) > 0 and not self.shuttingDown():
            try:
                listener, last_id = self.listeners.pop()
                IOLoop.current().add_callback(listener, {
                    'success': True,
                    'result': [notification],
                })
            except:
                log.debug('Failed sending to listener: %s', traceback.format_exc())

        self.listeners = []
        self.m_lock.release()

        log.debug('Done notifying frontend')

    def addListener(self, callback, last_id = None):

        if last_id:
            messages = self.getMessages(last_id)
            if len(messages) > 0:
                return callback({
                    'success': True,
                    'result': messages,
                })

        self.m_lock.acquire()
        self.listeners.append((callback, last_id))
        self.m_lock.release()


    def removeListener(self, callback):

        self.m_lock.acquire()
        new_listeners = []
        for list_tuple in self.listeners:
            try:
                listener, last_id = list_tuple
                if listener != callback:
                    new_listeners.append(list_tuple)
            except:
                log.debug('Failed removing listener: %s', traceback.format_exc())

        self.listeners = new_listeners
        self.m_lock.release()

    def cleanMessages(self):

        if len(self.messages) == 0:
            return

        log.debug('Cleaning messages')
        self.m_lock.acquire()

        time_ago = (time.time() - 15)
        self.messages[:] = [m for m in self.messages if (m['time'] > time_ago)]

        self.m_lock.release()
        log.debug('Done cleaning messages')

    def getMessages(self, last_id):

        log.debug('Getting messages with id: %s', last_id)
        self.m_lock.acquire()

        recent = []
        try:
            index = list(map(itemgetter('message_id'), self.messages)).index(last_id)
            recent = self.messages[index + 1:]
        except:
            pass

        self.m_lock.release()
        log.debug('Returning for %s %s messages', (last_id, len(recent)))

        return recent

    def listener(self, init = False, **kwargs):

        messages = []

        # Get last message
        if init:
            db = get_db()

            notifications = db.all('notification')

            for n in notifications:

                try:
                    doc = db.get('id', n.get('_id'))
                    if doc.get('time') > (time.time() - 604800):
                        messages.append(doc)
                except RecordDeleted:
                    pass

        return {
            'success': True,
            'result': messages,
        }
