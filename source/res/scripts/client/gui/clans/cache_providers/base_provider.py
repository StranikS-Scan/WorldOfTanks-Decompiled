# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/cache_providers/base_provider.py
import logging
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import defaultdict
import typing
from enum import Enum
from typing import Dict, Optional, NamedTuple
import Event
from adisp import adisp_process
from data_structures import DictObj
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.requests import WgcgRequestResponse
from gui.wgcg.states import WebControllerStates
from helpers import dependency, time_utils
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import DefaultDict
    from shared_utils import CONST_CONTAINER
_logger = logging.getLogger(__name__)

class UpdatePeriodType(Enum):
    BY_TIME = 'BY_TIME'
    AFTER_BATTLE = 'AFTER_BATTLE'
    NONE = 'NONE'


RequestSettings = NamedTuple('RequestSettings', [('context', CommonWebRequestCtx),
 ('isCached', bool),
 ('updatePeriodType', UpdatePeriodType),
 ('updateKwargs', Optional[Dict])])

class IBaseProvider(object):

    def start(self):
        raise NotImplementedError

    def stop(self, withClear=False):
        raise NotImplementedError


class BaseProvider(IBaseProvider):
    __metaclass__ = ABCMeta
    __webController = dependency.descriptor(IWebController)

    def __init__(self):
        super(BaseProvider, self).__init__()
        self._eManager = Event.EventManager()
        self.onDataReceived = Event.Event(self._eManager)
        self.onDataFailed = Event.Event(self._eManager)
        self.__isStarted = False
        self.__data = defaultdict(lambda : DictObj(isSynced=False, data=None, isWaitingResponse=False, lastUpdate=None))

    def start(self):
        if self.__webController.getStateID() == WebControllerStates.STATE_NOT_DEFINED:
            self.__webController.invalidate()
        self.__isStarted = True

    def stop(self, withClear=False):
        self.__isStarted = False
        self._eManager.clear()
        for dataName, dataObj in self.__data.items():
            settings = self._getSettingsByDataName(dataName)
            if settings.updatePeriodType is not UpdatePeriodType.BY_TIME:
                dataObj.isSynced = False

        if withClear:
            self.__data.clear()

    @abstractproperty
    def _isEnabled(self):
        raise NotImplementedError

    @abstractproperty
    def _dataNameContainer(self):
        raise NotImplementedError

    @property
    def _fakeDataStorage(self):
        return dict()

    @abstractmethod
    def _getSettings(self):
        raise NotImplementedError

    def _dataReceived(self, dataName, data):
        self.onDataReceived(dataName, data)

    def _getData(self, dataName, useFake=False):
        dataObj = self.__data[dataName]
        settings = self._getSettingsByDataName(dataName)
        if self.__isRequestingAvailable(settings, dataObj):
            self._requestData(dataName, useFake=useFake)
        return dataObj

    @adisp_process
    def _requestData(self, dataName, useFake=False):
        if not self.__isStarted:
            return
        elif not self._dataNameContainer.hasValue(dataName):
            return
        else:
            dataObj = self.__data[dataName]
            settings = self._getSettingsByDataName(dataName)
            if not self._isEnabled or not self.__isRequestingAvailable(settings, dataObj):
                return
            elif useFake and dataName not in self._fakeDataStorage:
                _logger.error('There are not %s in fake data storage. Check _fakeDataStorage', dataName)
                return
            ctx = settings.context
            dataObj.isWaitingResponse = True
            if not useFake:
                response = yield self.__webController.sendRequest(ctx=ctx)
            else:
                response = WgcgRequestResponse(code=0, txtStr='', data=self._fakeDataStorage[dataName], extraCode=0, headers={})
            if response.isSuccess():
                formattedData = ctx.getDataObj(response.data)
                isSynced = True
            else:
                formattedData = ctx.getDefDataObj() if dataObj.data is None else dataObj.data
                isSynced = False
                _logger.info('Failed to get data: %s. Code: %s', dataName, response.getCode())
            dataObj.isWaitingResponse = False
            dataObj.lastUpdate = time_utils.getServerUTCTime() if isSynced else None
            dataObj.isSynced = isSynced
            dataObj.data = formattedData
            if isSynced:
                self._dataReceived(dataName, formattedData)
            else:
                self.onDataFailed(dataName)
            return

    def _getSettingsByDataName(self, dataName):
        return self._getSettings().get(dataName)

    def _updateDataCache(self, dataName, updater):
        dataObj = self.__data[dataName]
        if not dataObj.isSynced or not callable(updater):
            return
        if not updater(dataObj.data):
            return
        self.onDataReceived(dataName, dataObj.data)

    @staticmethod
    def __isRequestingAvailable(settings, dataObj):
        if dataObj.isWaitingResponse:
            return False
        elif not settings.isCached:
            return True
        elif settings.updatePeriodType is UpdatePeriodType.AFTER_BATTLE:
            return not dataObj.isSynced
        elif settings.updatePeriodType is UpdatePeriodType.BY_TIME:
            if dataObj.lastUpdate is None:
                return True
            return time_utils.getServerUTCTime() - dataObj.lastUpdate > settings.updateKwargs.get('updateTime', 0)
        else:
            return not dataObj.isSynced
