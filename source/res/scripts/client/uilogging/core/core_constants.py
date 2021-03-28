# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/core/core_constants.py


class SettingsStatuses(object):
    REQUESTED = 'requested'
    ENABLED = 'enabled'
    DISABLED = 'disabled'


class LogLevels(object):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30


HTTP_OK_STATUS = 200
HTTP_DEFAULT_TIMEOUT = 5
HTTP_DEFAULT_HEADERS = {'Content-Type': 'application/json'}
