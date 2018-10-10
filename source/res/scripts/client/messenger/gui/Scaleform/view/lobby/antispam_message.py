# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/antispam_message.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import CONTACTS
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
MAX_ANTISPAM_MESSAGES = 3
_isClosed = False

def isShown():
    global _isClosed
    return _getCounter() < MAX_ANTISPAM_MESSAGES and not _isClosed


def close():
    global _isClosed
    counter = _getCounter()
    newCounter = min(counter + 1, MAX_ANTISPAM_MESSAGES)
    _isClosed = True
    if newCounter != counter:
        _setCounter(newCounter)


def reset():
    global _isClosed
    _isClosed = False


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def _getCounter(settingsCore=None):
    return settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.CONTACTS, CONTACTS.ANTISPAM_MESSAGES_COUNTER, default=0)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def _setCounter(counter, settingsCore=None):
    return settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.CONTACTS, {CONTACTS.ANTISPAM_MESSAGES_COUNTER: counter})
