# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/logger.py
import logging
from helpers.log.adapters import LoggerAdapter
DEFAULT_NAME = 'PRC'

class InstanceContextLoggerAdapter(LoggerAdapter):

    def __init__(self, logger, instance=None, **context):
        if instance is not None:
            context['cls'] = instance.__class__.__name__
            context['iid'] = id(instance)
        super(InstanceContextLoggerAdapter, self).__init__(logger, context)
        return

    def process(self, msg, kwargs):
        if self.extra:
            msg = '{} {}'.format(self.extra, msg)
        return (msg, kwargs)


def getWithContext(loggerName=DEFAULT_NAME, instance=None, **context):
    return InstanceContextLoggerAdapter(logging.getLogger(loggerName), instance=instance, **context)
