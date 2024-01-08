# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/cache_providers/stronghold_event_provider.py
import weakref
import typing
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventEnabled
from gui.clans.cache_providers.base_provider import BaseProvider, RequestSettings, UpdatePeriodType
from gui.wgcg.clan.contexts import StrongholdEventSettingsCtx, StrongholdEventClanInfoCtx
from helpers import time_utils
from shared_utils import CONST_CONTAINER
if typing.TYPE_CHECKING:
    from typing import Optional, Dict
    from gui.clans.data_wrapper.stronghold_event import StrongholdEventClanInfoData, StrongholdEventSettingsData

class _DataNames(CONST_CONTAINER):
    SETTINGS = 'SETTINGS'
    PRIME_TIME = 'PRIME_TIME'


class StrongholdEventProvider(BaseProvider):

    def __init__(self, clanCache):
        self.__clanCache = weakref.proxy(clanCache)
        super(StrongholdEventProvider, self).__init__()

    def start(self):
        super(StrongholdEventProvider, self).start()
        self._requestData(_DataNames.SETTINGS)

    def getSettings(self):
        return self._getData(_DataNames.SETTINGS)

    def getClanPrimeTime(self):
        return self._getData(_DataNames.PRIME_TIME)

    def isRunning(self):
        settings = self.getSettings()
        if settings is None:
            return False
        else:
            return settings.getVisibleStartDate() < time_utils.getServerUTCTime() < settings.getVisibleEndDate()

    @property
    def _dataNameContainer(self):
        return _DataNames

    @property
    def _isEnabled(self):
        return getStrongholdEventEnabled()

    def _getSettings(self):
        return {_DataNames.SETTINGS: RequestSettings(context=StrongholdEventSettingsCtx(), isCached=True, updatePeriodType=UpdatePeriodType.AFTER_BATTLE, updateKwargs=None),
         _DataNames.PRIME_TIME: RequestSettings(context=StrongholdEventClanInfoCtx(), isCached=True, updatePeriodType=UpdatePeriodType.AFTER_BATTLE, updateKwargs=None)}

    def _dataReceived(self, dataName, data):
        if dataName == _DataNames.SETTINGS and self.isRunning() and self.__clanCache.isInClan:
            self._requestData(_DataNames.PRIME_TIME)
        self.onDataReceived(dataName, data)
