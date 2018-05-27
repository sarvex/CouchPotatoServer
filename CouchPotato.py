#!/usr/bin/env python

import logging
import os
import select
import signal
import socket
import subprocess
import sys
import traceback
from logging import handlers
from os.path import dirname

# Root path
base_path = dirname(os.path.abspath(__file__))

# Insert local directories into path
sys.path.insert(0, os.path.join(base_path, 'libs'))

from couchpotato.environment import Env
from couchpotato.core.helpers.variable import get_data_directory, remove_pyc


# Remove pyc files before dynamic load (sees .pyc files regular .py modules)
remove_pyc(base_path)


class Loader(object):

    do_restart = False

    def __init__(self):

        # Get options via arg
        from couchpotato.runner import getOptions
        self.options = getOptions(sys.argv[1:])

        # Load settings
        settings = Env.get('settings')
        settings.set_file(self.options.config_file)

        # Create data dir if needed
        if self.options.data_dir:
            self.data_dir = self.options.data_dir
        else:
            self.data_dir = os.path.expanduser(Env.setting('data_dir'))

        if self.data_dir == '':
            self.data_dir = get_data_directory()

        if not os.path.isdir(self.data_dir):
            os.makedirs(self.data_dir)

        # Create logging dir
        self.log_dir = os.path.join(self.data_dir, 'logs')
        if not os.path.isdir(self.log_dir):
            os.makedirs(self.log_dir)

        # Logging
        from couchpotato.core.logger import CPLog
        self.log = CPLog(__name__)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%H:%M:%S')
        hdlr = handlers.RotatingFileHandler(os.path.join(self.log_dir, 'error.log'), 'a', 500000, 10)
        hdlr.setLevel(logging.CRITICAL)
        hdlr.setFormatter(formatter)
        self.log.logger.addHandler(hdlr)

    def add_signals(self):
        signal.signal(signal.SIGINT, self.on_exit)
        signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

        from couchpotato.core.event import add_event
        add_event('app.do_shutdown', self.set_restart)

    def set_restart(self, restart):
        self.do_restart = restart
        return True

    def on_exit(self, signal, frame):
        from couchpotato.core.event import fire_event
        fire_event('app.shutdown', single=True)

    def run(self):

        self.add_signals()

        from couchpotato.runner import runCouchPotato
        runCouchPotato(self.options, base_path, sys.argv[1:], data_dir = self.data_dir, log_dir = self.log_dir, Env = Env)

        if self.do_restart:
            self.restart()

    def restart(self):
        try:
            # remove old pidfile first
            try:
                if self.runAsDaemon():
                    try:
                        self.daemon.stop()
                    except:
                        pass
            except:
                self.log.critical(traceback.format_exc())

            # Release log files and shutdown logger
            logging.shutdown()

            args = [sys.executable] + [os.path.join(base_path, os.path.basename(__file__))] + sys.argv[1:]
            subprocess.Popen(args)
        except:
            self.log.critical(traceback.format_exc())

    def daemonize(self):

        if self.runAsDaemon():
            try:
                from daemon import Daemon
                self.daemon = Daemon(self.options.pid_file)
                self.daemon.daemonize()
            except SystemExit:
                raise
            except:
                self.log.critical(traceback.format_exc())

    def runAsDaemon(self):
        return self.options.daemon and self.options.pid_file


if __name__ == '__main__':
    l = None
    try:
        l = Loader()
        l.daemonize()
        l.run()
    except KeyboardInterrupt:
        pass
    except select.error:
        pass
    except SystemExit:
        raise
    except socket.error as e:
        # log when socket receives SIGINT, but continue.
        # previous code would have skipped over other types of IO errors too.
        nr, msg = e
        if nr != 4:
            try:
                l.log.critical(traceback.format_exc())
            except:
                print((traceback.format_exc()))
            raise
    except:
        try:
            # if this fails we will have two tracebacks
            # one for failing to log, and one for the exception that got us here.
            if l:
                l.log.critical(traceback.format_exc())
            else:
                print((traceback.format_exc()))
        except:
            print((traceback.format_exc()))
        raise
