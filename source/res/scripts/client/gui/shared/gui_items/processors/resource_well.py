# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/resource_well.py
from functools import partial
import BigWorld
from adisp import adisp_async, adisp_process
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.resource_well.resource import processLoadingResources, splitResourcesByType, mergeResources
from gui.resource_well.resource_well_constants import UNAVAILABLE_REWARD_ERROR
from gui.shared.event_dispatcher import showResourcesLoadingConfirm, showResourceWellNoSerialVehiclesConfirm
from gui.shared.gui_items.processors import Processor, plugins
from gui.shared.gui_items.processors.plugins import MessageConfirmator, SyncValidator
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
from skeletons.gui.shared import IItemsCache
_RESOURCE_WELL_MESSAGES = R.strings.system_messages.resourceWell

class ResourceWellLoadingConfirmator(MessageConfirmator):

    def __init__(self, resources, isReturnOperation):
        super(ResourceWellLoadingConfirmator, self).__init__(None, True)
        self.__resources = resources
        self.__isReturnOperation = isReturnOperation
        return

    def _gfMakeMeta(self):
        return partial(showResourcesLoadingConfirm, self.__resources, self.__isReturnOperation)

    @adisp_async
    @adisp_process
    def _confirm(self, callback):
        yield lambda callback: callback(None)
        if self._activeHandler():
            gfMetaData = self._gfMakeMeta()
            if gfMetaData:
                isOk, data = yield gfMetaData
                result = plugins.makeSuccess(**data) if isOk else plugins.makeError(**data)
                callback(result)
                return


class ResourceWellTakeBackProcessor(Processor):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ResourceWellTakeBackProcessor, self).__init__()
        self.addPlugin(ResourceWellLoadingConfirmator(mergeResources(self.__itemsCache.items.resourceWell.getBalance()), True))

    def _request(self, callback):
        Waiting.show('getResourcesBack')
        BigWorld.player().resourceWell.takeBack(lambda code: self._response(code, callback))

    def _successHandler(self, code, ctx=None):
        Waiting.hide('getResourcesBack')
        return super(ResourceWellTakeBackProcessor, self)._successHandler(code, ctx)

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('getResourcesBack')
        SystemMessages.pushMessage(text=backport.text(_RESOURCE_WELL_MESSAGES.resourcesReturnError()), type=SM_TYPE.ErrorSimple)
        return super(ResourceWellTakeBackProcessor, self)._errorHandler(code, errStr, ctx)


class ResourceWellPutValidator(SyncValidator):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, isTopReward):
        self.__isTopReward = isTopReward
        super(ResourceWellPutValidator, self).__init__()

    def _validate(self):
        isRewardCountAvailable = self.__resourceWell.isRewardCountAvailable(self.__isTopReward)
        return plugins.makeSuccess() if isRewardCountAvailable else plugins.makeError()


class ResourceWellPutProcessor(Processor):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, resources, rewardID):
        super(ResourceWellPutProcessor, self).__init__()
        self.__resources = processLoadingResources(resources)
        self.__rewardID = rewardID
        isTopReward = self.__resourceWell.getRewardID(isTop=True) == self.__rewardID
        self.addPlugins([ResourceWellLoadingConfirmator(self.__resources, False), ResourceWellPutValidator(isTopReward)])

    def _request(self, callback):
        Waiting.show('putResources')
        BigWorld.player().resourceWell.putResources(splitResourcesByType(self.__resources), self.__rewardID, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        Waiting.hide('putResources')
        return super(ResourceWellPutProcessor, self)._successHandler(code, ctx)

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('putResources')
        if errStr != UNAVAILABLE_REWARD_ERROR:
            SystemMessages.pushMessage(text=backport.text(_RESOURCE_WELL_MESSAGES.resourcesLoadingError()), type=SM_TYPE.ErrorSimple)
        return super(ResourceWellPutProcessor, self)._errorHandler(code, errStr, ctx)


class ResourceWellNoTopVehiclesConfirmator(MessageConfirmator):

    def __init__(self):
        super(ResourceWellNoTopVehiclesConfirmator, self).__init__(None, True)
        return

    def _gfMakeMeta(self):
        return showResourceWellNoSerialVehiclesConfirm

    @adisp_async
    @adisp_process
    def _confirm(self, callback):
        yield lambda callback: callback(None)
        if self._activeHandler():
            gfMetaData = self._gfMakeMeta()
            if gfMetaData:
                isOk, data = yield gfMetaData
                result = plugins.makeSuccess(**data) if isOk else plugins.makeError(**data)
                callback(result)
                return


class ResourceWellNoTopVehiclesProcessor(Processor):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, resources):
        super(ResourceWellNoTopVehiclesProcessor, self).__init__()
        self.__resources = processLoadingResources(resources)
        self.addPlugins([ResourceWellNoTopVehiclesConfirmator(), ResourceWellPutValidator(isTopReward=False)])

    def _request(self, callback):
        Waiting.show('putResources')
        rewardID = self.__resourceWell.getRewardID(isTop=False)
        BigWorld.player().resourceWell.putResources(splitResourcesByType(self.__resources), rewardID, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        Waiting.hide('putResources')
        return super(ResourceWellNoTopVehiclesProcessor, self)._successHandler(code, ctx)

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('putResources')
        if errStr != UNAVAILABLE_REWARD_ERROR:
            SystemMessages.pushMessage(text=backport.text(_RESOURCE_WELL_MESSAGES.resourcesLoadingError()), type=SM_TYPE.ErrorSimple)
        return super(ResourceWellNoTopVehiclesProcessor, self)._errorHandler(code, errStr, ctx)
