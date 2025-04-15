# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/wgcg/providers/base_provider.py
import logging
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import defaultdict, namedtuple
from enum import Enum
from typing import Dict, Optional, NamedTuple, Type, TYPE_CHECKING
import BigWorld
import Event
import ResMgr
from adisp import adisp_process, adisp_async
from data_structures import DictObj
from client_request_lib.requester import Requester as WebRequester
from gui.wgcg.base.contexts import CommonWebRequestCtx
from AccountCommands import CMD_GENERATE_SSR_JWT_TOKEN
from server_side_replay.gui.wgcg.requests import ServerSideReplayRequester, ServerSideReplayRequestsController, ServerSideReplayRequestResponse
from helpers import time_utils, getClientLanguage
if TYPE_CHECKING:
    from typing import DefaultDict, Any
    from shared_utils import CONST_CONTAINER
_logger = logging.getLogger(__name__)

class UpdatePeriodType(Enum):
    BY_TIME = 'BY_TIME'
    AFTER_BATTLE = 'AFTER_BATTLE'
    NONE = 'NONE'


RequestSettings = NamedTuple('RequestSettings', [('contextClazz', Type[CommonWebRequestCtx]),
 ('isCached', bool),
 ('updatePeriodType', UpdatePeriodType),
 ('updateKwargs', Optional[Dict])])

class IBaseProvider(object):

    def start(self):
        raise NotImplementedError

    def stop(self, withClear=False):
        raise NotImplementedError


def _webUrlFetcher(url, callback, headers=None, timeout=30.0, method='GET', postData=''):
    return BigWorld.fetchURL(url, callback, headers, timeout, method, postData)


ServerSideReplayServerSettings = namedtuple('ServerSideReplayServerSettings', ('url', 'type'))

class JwtRequestor(object):

    def __init__(self):
        self.__jwtData = None
        self.__waitAnswer = False
        self.__callbacks = []
        return

    @adisp_async
    def requestJwt(self, callback):
        if self.__jwtData and self.__jwtData['expirationTime'] > time.time():
            callback(self.__jwtData)
            return
        else:
            self.__callbacks.append(callback)
            if self.__waitAnswer:
                return
            self.__waitAnswer = True

            def cmdCallback(requestID, resultID, errorStr, ext=None):
                self.__jwtData = ext or {}
                for callback in self.__callbacks:
                    callback(ext)

                self.__waitAnswer = False
                self.__callbacks = []

            BigWorld.player()._doCmdNoArgs(CMD_GENERATE_SSR_JWT_TOKEN, cmdCallback)
            return


_g_jwtRequestor = JwtRequestor()

class BaseProvider(IBaseProvider):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(BaseProvider, self).__init__()
        self._eManager = Event.EventManager()
        self.onDataReceived = Event.Event(self._eManager)
        self.onDataFailed = Event.Event(self._eManager)
        self.__isStarted = False
        self.__data = defaultdict(lambda : DictObj(isSynced=False, data=None, isWaitingResponse=False, lastUpdate=None))
        hostUrl = ResMgr.openSection('gui/replayer_host_url.xml').readString('url')
        settings = ServerSideReplayServerSettings(hostUrl, 'gateway')
        self.__webRequester = WebRequester.create_requester(_webUrlFetcher, settings, client_lang=getClientLanguage())
        self.__requester = ServerSideReplayRequester(self.__webRequester)
        self.__serverSideRequestsController = ServerSideReplayRequestsController(self.__requester)

    def start(self):
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

    def _getData(self, dataName, useFake=False, *args, **kwargs):
        dataObj = self.__data[dataName]
        settings = self._getSettingsByDataName(dataName)
        if self.__isRequestingAvailable(settings, dataObj):
            self._requestData(dataName, useFake=useFake, *args, **kwargs)
        return dataObj

    @adisp_process
    def _requestData(self, dataName, useFake=False, *args, **kwargs):
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
            ctx = settings.contextClazz(*args, **kwargs)
            dataObj.isWaitingResponse = True
            jwtData = yield _g_jwtRequestor.requestJwt()
            if jwtData:
                ctx.jwtToken = jwtData['token']
            if not useFake:
                response = yield self._sendRequest(ctx=ctx, allowDelay=True)
            else:
                response = ServerSideReplayRequestResponse(code=0, txtStr='', data=self._fakeDataStorage[dataName], extraCode=0, headers={})
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

    @adisp_async
    def _sendRequest(self, ctx, callback, allowDelay=None):
        requestsController = self.__serverSideRequestsController

        def _cbWrapper(result):
            _logger.debug('Response is received: %s %s', ctx, result)
            callback(result)

        requestsController.request(ctx, callback=_cbWrapper, allowDelay=allowDelay)

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
        elif settings.updatePeriodType is UpdatePeriodType.AFTER_BATTLE:
            return not dataObj.isSynced
        elif settings.updatePeriodType is UpdatePeriodType.BY_TIME:
            if dataObj.lastUpdate is None:
                return True
            return time_utils.getServerUTCTime() - dataObj.lastUpdate > settings.updateKwargs.get('updateTime', 0)
        else:
            return True
