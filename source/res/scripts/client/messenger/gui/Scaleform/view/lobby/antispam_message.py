# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/antispam_message.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import CONTACTS
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
MAX_ANTISPAM_MESSAGES = 3

def isShown():
    return _getCounter() < MAX_ANTISPAM_MESSAGES


def close():
    counter = _getCounter()
    newCounter = min(counter + 1, MAX_ANTISPAM_MESSAGES)
    if newCounter != counter:
        _setCounter(newCounter)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def _getCounter(settingsCore=None):
    return settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.CONTACTS, CONTACTS.ANTISPAM_MESSAGES_COUNTER, default=0)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def _setCounter(counter, settingsCore=None):
    return settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.CONTACTS, {CONTACTS.ANTISPAM_MESSAGES_COUNTER: counter})
