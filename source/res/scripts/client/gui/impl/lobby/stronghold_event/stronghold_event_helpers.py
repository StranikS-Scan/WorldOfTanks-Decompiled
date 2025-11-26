# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold_event/stronghold_event_helpers.py
import logging
from typing import Optional, TYPE_CHECKING, Any
from account_helpers import AccountSettings
from account_helpers.AccountSettings import StrongholdEvent
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventEnabled
from gui.clans.clan_cache import g_clanCache
if TYPE_CHECKING:
    from gui.clans.data_wrapper.stronghold_event import StrongholdEventSettingsData
_logger = logging.getLogger(__name__)
DEFAULT_EVENT_NAME = 'default_stronghold_event_name'

def getStrongholdEventName(useDefault=True):
    eventSettings = g_clanCache.strongholdEventProvider.getSettings()
    if eventSettings is None:
        if useDefault:
            return DEFAULT_EVENT_NAME
        return
    else:
        eventName = eventSettings.getEventConfig().name
        if not eventName:
            if useDefault:
                return DEFAULT_EVENT_NAME
            return
        return eventName


def getSettings(settingName, defaultValue=None):
    settings = AccountSettings.getSettings(StrongholdEvent.SETTINGS)
    eventName = getStrongholdEventName(useDefault=False)
    if eventName is None:
        _logger.info('Can not to get setting by name %s because event name is empty. Check settings of the event', settingName)
        return
    else:
        section = settings.get(eventName, None)
        if section is None:
            settings[eventName] = section = {}
            AccountSettings.setSettings(StrongholdEvent.SETTINGS, settings)
        return section.get(settingName, defaultValue)


def setSettings(settingName, value):
    settings = AccountSettings.getSettings(StrongholdEvent.SETTINGS)
    eventName = getStrongholdEventName(useDefault=False)
    if eventName is None:
        _logger.info('Can not to set setting by name %s because event name is empty. Check settings of the event', settingName)
        return False
    else:
        section = settings.get(eventName, None)
        if section is None:
            settings[eventName] = section = {}
        section[settingName] = value
        AccountSettings.setSettings(StrongholdEvent.SETTINGS, settings)
        return True


def isStrongholdEventBannerAvailable():
    return False if not getStrongholdEventEnabled() else bool(g_clanCache.strongholdEventProvider.getSettings())
