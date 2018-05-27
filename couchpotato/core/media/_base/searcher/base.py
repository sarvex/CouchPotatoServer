from couchpotato.core.event import add_event, fire_event
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin

log = CPLog(__name__)


class SearcherBase(Plugin):

    in_progress = False

    def __init__(self):
        super(SearcherBase, self).__init__()

        add_event('searcher.progress', self.getProgress)
        add_event('%s.searcher.progress' % self.getType(), self.getProgress)

        self.initCron()

    def initCron(self):
        """ Set the searcher cronjob
            Make sure to reset cronjob after setting has changed
        """

        _type = self.getType()

        def setCrons():
            fire_event('schedule.cron', '%s.searcher.all' % _type, self.searchAll,
                       day=self.conf('cron_day'), hour=self.conf('cron_hour'), minute=self.conf('cron_minute'))

        add_event('app.load', setCrons)
        add_event('setting.save.%s_searcher.cron_day.after' % _type, setCrons)
        add_event('setting.save.%s_searcher.cron_hour.after' % _type, setCrons)
        add_event('setting.save.%s_searcher.cron_minute.after' % _type, setCrons)

    def getProgress(self, **kwargs):
        """ Return progress of current searcher"""

        progress = {
            self.getType(): self.in_progress
        }

        return progress
