# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/new_settings_counter.py
from VOIP import getVOIPManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_SETTINGS_COUNTER

def getNewSettings():
    """Get list of new settings to view
    :return: list ['tabName',]
    """
    settings = __getSettingsFromStorage()
    __patch_getVOIPSettings(settings)
    return [ k for k, v in settings.iteritems() if v ]


def invalidateSettings(tabName):
    """Update viewed settings
    :param tabName: viewed tabName
    """
    settings = __getSettingsFromStorage()
    if tabName in settings.keys():
        settings[tabName] = False
        __setSettingsToStorage(settings)


def __getSettingsFromStorage():
    """Get settings from accountSettings
    """
    return AccountSettings.getSettings(NEW_SETTINGS_COUNTER)


def __setSettingsToStorage(value):
    """Set settings to accountSettings
    """
    AccountSettings.setSettings(NEW_SETTINGS_COUNTER, value)


def __patch_getVOIPSettings(settings):
    """Get VOIP settings, if enabled, then show new settings counter for voice tab
    """
    if any((key in settings for key in ('SoundSettings', 'SoundSettings0', 'SoundSettings1'))):
        return
    else:
        voipRespHandler = getVOIPManager()
        if voipRespHandler is not None and voipRespHandler.isEnabled():
            settings['SoundSettings0'] = True
            settings['SoundSettings1'] = True
        else:
            settings['SoundSettings'] = True
        __setSettingsToStorage(settings)
        return
