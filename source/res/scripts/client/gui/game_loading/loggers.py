# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/loggers.py
import logging

def getLogger(loggerName):
    return logging.getLogger('GameLoading:{}'.format(loggerName))


def getSequencesViewHistoryLogger():
    return getLogger('SequencesViewHistory')


def getCdnConfigLogger():
    return getLogger('CdnConfig')


def getCdnCacheLogger():
    return getLogger('CdnCache')


def getResourcesLogger():
    return getLogger('Resources')


def getStatesLogger():
    return getLogger('States')


def getStateMachineLogger():
    return getLogger('StateMachine')


def getLoaderSettingsLogger():
    return getLogger('LoaderSettings')


def getLoaderLogger():
    return getLogger('Loader')
