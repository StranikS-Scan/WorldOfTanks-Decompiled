# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/loggers.py
import logging

def getLogger(loggerName):
    return logging.getLogger('Collections:{}'.format(loggerName))


def getCdnCacheLogger():
    return getLogger('CdnCache')


def getLocalCacheLogger():
    return getLogger('LocalCache')
