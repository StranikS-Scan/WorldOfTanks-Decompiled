# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/cache_providers/stronghold_event_provider.py
import logging
import weakref
from collections import defaultdict
import typing
import Event
from adisp import adisp_process
from data_structures import DictObj
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getStrongholdEventEnabled
from gui.clans.cache_providers.base_provider import IBaseProvider
from gui.clientgw.clan.contexts import StrongholdEventSettingsCtx, StrongholdEventClanInfoCtx
from gui.clientgw.states import WebControllerStates
from helpers import dependency, time_utils
from shared_utils import CONST_CONTAINER
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import DefaultDict, Optional
    from gui.clans.items import StrongholdEventSettingsData, StrongholdEventClanInfoData
_logger = logging.getLogger(__name__)

class _DataNames(CONST_CONTAINER):
    SETTINGS = 'SETTINGS'
    PRIME_TIME = 'PRIME_TIME'


class StrongholdEventProvider(IBaseProvider):
    __webController = dependency.descriptor(IWebController)

    def __init__(self, clanCache):
        super(StrongholdEventProvider, self).__init__()
        self.__clanCache = weakref.proxy(clanCache)
        self.__eManager = Event.EventManager()
        self.onDataReceived = Event.Event(self.__eManager)
        self.__data = defaultdict(lambda : DictObj(isSynced=False, data=None, isWaitingResponse=False))

    def start(self):
        if self.__webController.getStateID() == WebControllerStates.STATE_NOT_DEFINED:
            self.__webController.invalidate()
        self.__requestData(_DataNames.SETTINGS)

    def stop(self, withClear=False):
        self.__eManager.clear()
        for value in self.__data.values():
            value.isSynced = False

        if withClear:
            self.__data.clear()

    def getSettings(self):
        return self.__getData(_DataNames.SETTINGS)

    def getClanPrimeTime(self):
        return self.__getData(_DataNames.PRIME_TIME)

    def isRunning(self):
        settings = self.getSettings()
        if settings is None:
            return False
        else:
            return settings.getVisibleStartDate() < time_utils.getServerUTCTime() < settings.getVisibleEndDate()

    def isSeasonRunning(self):
        settings = self.getSettings()
        if settings is None:
            return False
        else:
            seasonStartDate = settings.event_config.get('visible_start_date', 0)
            seasonEndDate = settings.event_config.get('visible_end_date', 0)
            return seasonStartDate < time_utils.getServerUTCTime() < seasonEndDate

    def isSeasonEnding(self):
        settings = self.getSettings()
        if settings is None:
            return False
        else:
            eventEndDate = settings.event_config.get('event_end_date', 0)
            return eventEndDate < time_utils.getServerUTCTime()

    def __getData(self, dataName):
        data = self.__data[dataName]
        if not data.isSynced:
            self.__requestData(dataName)
        return data.data

    @adisp_process
    def __requestData(self, dataName):
        if not _DataNames.hasValue(dataName):
            return
        else:
            dataObj = self.__data[dataName]
            if not getStrongholdEventEnabled() or dataObj.isSynced or dataObj.isWaitingResponse:
                return
            ctx = self.__getCtxByDataName(dataName)
            dataObj.isWaitingResponse = True
            response = yield self.__webController.sendRequest(ctx=ctx)
            if response.isSuccess():
                formattedData = ctx.getDataObj(response.data)
                isSynced = True
            else:
                formattedData = ctx.getDefDataObj() if dataObj.data is None else dataObj.data
                isSynced = False
                _logger.info('Failed to get Stronghold Event data: %s. Code: %s', dataName, response.getCode())
            dataObj.isWaitingResponse = False
            dataObj.isSynced = isSynced
            dataObj.data = formattedData
            if isSynced:
                self.__dataReceived(dataName, formattedData)
            return

    def __dataReceived(self, dataName, data):
        if dataName == _DataNames.SETTINGS and self.isRunning() and self.__clanCache.isInClan:
            self.__requestData(_DataNames.PRIME_TIME)
        self.onDataReceived(dataName, data)

    @staticmethod
    def __getCtxByDataName(dataName):
        if dataName == _DataNames.SETTINGS:
            return StrongholdEventSettingsCtx()
        return StrongholdEventClanInfoCtx() if dataName == _DataNames.PRIME_TIME else None
