import configparser
import traceback
from hashlib import md5

from CodernityDB.hash_index import HashIndex

from couchpotato.api import addApiView
from couchpotato.core.event import add_event, fire_event
from couchpotato.core.helpers.encoding import to_unicode
from couchpotato.core.helpers.variable import merge_dictionaries, try_int, try_float


class Settings(object):

    options = {}
    types = {}

    def __init__(self):

        addApiView('settings', self.view, docs = {
            'desc': 'Return the options and its values of settings.conf. Including the default values and group ordering used on the settings page.',
            'return': {'type': 'object', 'example': """{
    // objects like in __init__.py of plugin
    "options": {
        "moovee" : {
            "groups" : [{
                "description" : "SD movies only",
                "name" : "#alt.binaries.moovee",
                "options" : [{
                    "default" : false,
                    "name" : "enabled",
                    "type" : "enabler"
                }],
                "tab" : "providers"
            }],
            "name" : "moovee"
        }
    },
    // object structured like settings.conf
    "values": {
        "moovee": {
            "enabled": false
        }
    }
}"""}
        })

        addApiView('settings.save', self.save_view, docs={
            'desc': 'Save setting to config file (settings.conf)',
            'params': {
                'section': {'desc': 'The section name in settings.conf'},
                'name': {'desc': 'The option name'},
                'value': {'desc': 'The value you want to save'},
            }
        })

        add_event('database.setup', self.database_setup)

        self.file = None
        self.p = None
        self.log = None
        self.directories_delimiter = "::"

    def set_file(self, config_file):
        self.file = config_file

        self.p = configparser.RawConfigParser()
        self.p.read(config_file)

        from couchpotato.core.logger import CPLog
        self.log = CPLog(__name__)

        self.connect_events()

    def database_setup(self):
        fire_event('database.setup_index', 'property', PropertyIndex)

    def parser(self):
        return self.p

    def sections(self):
        res = list(filter(self.is_section_readable, self.p.sections()))
        return res

    def connect_events(self):
        add_event('settings.options', self.add_options)
        add_event('settings.register', self.register_defaults)
        add_event('settings.save', self.save)

    def register_defaults(self, section_name, options=None, save=True):
        if not options: options = {}

        self.add_section(section_name)

        for option_name, option in list(options.items()):
            self.set_default(section_name, option_name, option.get('default', ''))

            # Set UI-meta for option (hidden/ro/rw)
            if option.get('ui-meta'):
                value = option.get('ui-meta')
                if value:
                    value = value.lower()
                    if value in ['hidden', 'rw', 'ro']:
                        meta_option_name = option_name + self.option_meta_suffix()
                        self.set_default(section_name, meta_option_name, value)
                    else:
                        self.log.warning('Wrong value for option %s.%s : ui-meta can not be equal to "%s"', (section_name, option_name, value))

            # Migrate old settings from old location to the new location
            if option.get('migrate_from'):
                if self.p.has_option(option.get('migrate_from'), option_name):
                    previous_value = self.p.get(option.get('migrate_from'), option_name)
                    self.p.set(section_name, option_name, previous_value)
                    self.p.remove_option(option.get('migrate_from'), option_name)

            if option.get('type'):
                self.set_type(section_name, option_name, option.get('type'))

        if save:
            self.save()

    def set(self, section, option, value):
        if not self.is_option_writable(section, option):
            self.log.warning('set::option "%s.%s" isn\'t writable', (section, option))
            return None
        if self.is_option_meta(section, option):
            self.log.warning('set::option "%s.%s" cancelled, since it is a META option', (section, option))
            return None

        return self.p.set(section, option, value)

    def get(self, option = '', section = 'core', default = None, type = None):
        if self.is_option_meta(section, option):
            self.log.warning('get::option "%s.%s" cancelled, since it is a META option', (section, option))
            return None

        tp = type
        try:
            tp = self.get_type(section, option) if not tp else tp

            if hasattr(self, 'get%s' % tp.capitalize()):
                return getattr(self, 'get%s' % tp.capitalize())(section, option)
            else:
                return self.get_unicode(section, option)

        except:
            return default

    def delete(self, option = '', section = 'core'):
        if not self.is_option_writable(section, option):
            self.log.warning('delete::option "%s.%s" isn\'t writable', (section, option))
            return None

        if self.is_option_meta(section, option):
            self.log.warning('set::option "%s.%s" cancelled, since it is a META option', (section, option))
            return None

        self.p.remove_option(section, option)
        self.save()

    def get_enabler(self, section, option):
        return self.get_bool(section, option)

    def get_bool(self, section, option):
        try:
            return self.p.getboolean(section, option)
        except:
            return self.p.get(section, option) == 1

    def get_int(self, section, option):
        try:
            return self.p.getint(section, option)
        except:
            return try_int(self.p.get(section, option))

    def get_float(self, section, option):
        try:
            return self.p.getfloat(section, option)
        except:
            return try_float(self.p.get(section, option))

    def get_directories(self, section, option):
        value = self.p.get(section, option)

        if value:
            return list(map(str.strip, str.split(value, self.directories_delimiter)))
        return []

    def get_unicode(self, section, option):
        value = self.p.get(section, option).decode('unicode_escape')
        return to_unicode(value).strip()

    def get_values(self):
        from couchpotato.environment import Env

        values = {}
        soft_chroot = Env.get('softchroot')

        # TODO : There is two commented "continue" blocks (# COMMENTED_SKIPPING). They both are good...
        #        ... but, they omit output of values of hidden and non-readable options
        #        Currently, such behaviour could break the Web UI of CP...
        #        So, currently this two blocks are commented (but they are required to
        #        provide secure hidding of options.
        for section in self.sections():

            # COMMENTED_SKIPPING
            #if not self.isSectionReadable(section):
            #    continue

            values[section] = {}
            for option in self.p.items(section):
                (option_name, option_value) = option

                #skip meta options:
                if self.is_option_meta(section, option_name):
                    continue

                # COMMENTED_SKIPPING
                #if not self.isOptionReadable(section, option_name):
                #    continue

                value = self.get(option_name, section)

                is_password = self.get_type(section, option_name) == 'password'
                if is_password and value:
                    value = len(value) * '*'

                # chrootify directory before sending to UI:
                if (self.get_type(section, option_name) == 'directory') and value:
                    try: value = soft_chroot.abs2chroot(value)
                    except: value = ""
                # chrootify directories before sending to UI:
                if (self.get_type(section, option_name) == 'directories'):
                    if (not value):
                        value = []
                    try:
                        value = list(map(soft_chroot.abs2chroot, value))
                    except : value = []

                values[section][option_name] = value

        return values

    def save(self):
        with open(self.file, 'wb') as configfile:
            self.p.write(configfile)

    def add_section(self, section):
        if not self.p.has_section(section):
            self.p.add_section(section)

    def set_default(self, section, option, value):
        if not self.p.has_option(section, option):
            self.p.set(section, option, value)

    def set_type(self, section, option, type):
        if not self.types.get(section):
            self.types[section] = {}

        self.types[section][option] = type

    def get_type(self, section, option):
        tp = None
        try: tp = self.types[section][option]
        except: tp = 'unicode' if not tp else tp
        return tp

    def add_options(self, section_name, options):
        # no additional actions (related to ro-rw options) are required here
        if not self.options.get(section_name):
            self.options[section_name] = options
        else:
            self.options[section_name] = merge_dictionaries(self.options[section_name], options)

    def get_options(self):
        """Returns dict of UI-readable options

        To check, whether the option is readable self.isOptionReadable() is used
        """

        res = {}

        # it is required to filter invisible options for UI, but also we should
        # preserve original tree for server's purposes.
        # So, next loops do one thing: copy options to res and in the process
        #   1. omit NON-READABLE (for UI) options,  and
        #   2. put flags on READONLY options
        for section_key in list(self.options.keys()):
            section_orig = self.options[section_key]
            section_name = section_orig.get('name') if 'name' in section_orig else section_key
            if self.is_section_readable(section_name):
                section_copy = {}
                section_copy_groups = []
                for section_field in section_orig:
                    if section_field.lower() != 'groups':
                        section_copy[section_field] = section_orig[section_field]
                    else:
                        for group_orig in section_orig['groups']:
                            group_copy = {}
                            group_copy_options = []
                            for group_field in group_orig:
                                if group_field.lower() != 'options':
                                    group_copy[group_field] = group_orig[group_field]
                                else:
                                    for option in group_orig[group_field]:
                                        option_name = option.get('name')
                                        # You should keep in mind, that READONLY = !IS_WRITABLE
                                        # and IS_READABLE is a different thing
                                        if self.is_option_readable(section_name, option_name):
                                            group_copy_options.append(option)
                                            if not self.is_option_writable(section_name, option_name):
                                                option['readonly'] = True
                            if len(group_copy_options)>0:
                                group_copy['options'] = group_copy_options
                                section_copy_groups.append(group_copy)
                if len(section_copy_groups)>0:
                    section_copy['groups'] = section_copy_groups
                    res[section_key] = section_copy

        return res

    def view(self, **kwargs):
        return {
            'options': self.get_options(),
            'values': self.get_values()
        }

    def save_view(self, **kwargs):

        section = kwargs.get('section')
        option = kwargs.get('name')
        value = kwargs.get('value')

        if not self.is_option_writable(section, option):
            self.log.warning('Option "%s.%s" isn\'t writable', (section, option))
            return {
                'success' : False,
            }

        from couchpotato.environment import Env
        soft_chroot = Env.get('softchroot')

        if self.get_type(section, option) == 'directory':
            value = soft_chroot.chroot2abs(value)

        if self.get_type(section, option) == 'directories':
            import json
            value = json.loads(value)
            if not (value and isinstance(value, list)):
                value = []
            value = list(map(soft_chroot.chroot2abs, value))
            value = self.directories_delimiter.join(value)

        # See if a value handler is attached, use that as value
        new_value = fire_event('setting.save.%s.%s' % (section, option), value, single=True)

        self.set(section, option, (new_value if new_value else value).encode('unicode_escape'))
        self.save()

        # After save (for re-interval etc)
        fire_event('setting.save.%s.%s.after' % (section, option), single=True)
        fire_event('setting.save.%s.*.after' % section, single=True)

        return {
            'success': True
        }

    def is_section_readable(self, section):
        meta = 'section_hidden' + self.option_meta_suffix()
        try:
            return not self.p.getboolean(section, meta)
        except: pass

        # by default - every section is readable:
        return True

    def is_option_readable(self, section, option):
        meta = option + self.option_meta_suffix()
        if self.p.has_option(section, meta):
            meta_v = self.p.get(section, meta).lower()
            return (meta_v == 'rw') or (meta_v == 'ro')

        # by default - all is writable:
        return True

    def option_readable_check_and_warn(self, section, option):
        x = self.is_option_readable(section, option)
        if not x:
            self.log.warning('Option "%s.%s" isn\'t readable', (section, option))
        return x

    def is_option_writable(self, section, option):
        meta = option + self.option_meta_suffix()
        if self.p.has_option(section, meta):
            return self.p.get(section, meta).lower() == 'rw'

        # by default - all is writable:
        return True

    def option_meta_suffix(self):
        return '_internal_meta'

    def is_option_meta(self, section, option):
        """ A helper method for detecting internal-meta options in the ini-file

        For a meta options used following names:
        * section_hidden_internal_meta = (True | False) - for section visibility
        * <OPTION>_internal_meta = (ro|rw|hidden) - for section visibility

        """

        suffix = self.option_meta_suffix()
        return option.endswith(suffix)

    def get_property(self, identifier):
        from couchpotato import get_db

        db = get_db()
        prop = None
        try:
            propert = db.get('property', identifier, with_doc = True)
            prop = propert['doc']['value']
        except ValueError:
            propert = db.get('property', identifier)
            fire_event('database.delete_corrupted', propert.get('_id'))
        except:
            self.log.debug('Property "%s" doesn\'t exist: %s', (identifier, traceback.format_exc(0)))

        return prop

    def set_property(self, identifier, value=''):
        from couchpotato import get_db

        db = get_db()

        try:
            p = db.get('property', identifier, with_doc = True)
            p['doc'].update({
                'identifier': identifier,
                'value': to_unicode(value),
            })
            db.update(p['doc'])
        except:
            db.insert({
                '_t': 'property',
                'identifier': identifier,
                'value': to_unicode(value),
            })


class PropertyIndex(HashIndex):
    _version = 1

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '32s'
        super(PropertyIndex, self).__init__(*args, **kwargs)

    def make_key(self, key):
        return md5(key).hexdigest()

    def make_key_value(self, data):
        if data.get('_t') == 'property':
            return md5(data['identifier']).hexdigest(), None
