# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/logger.py
from helpers.log import adapters
DEFAULT_NAME = 'PRC'

def getWithContext(loggerName=DEFAULT_NAME, instance=None, **context):
    return adapters.getWithContext(loggerName, instance, **context)
