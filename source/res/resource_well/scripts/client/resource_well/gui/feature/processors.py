# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/feature/processors.py
from functools import partial
import BigWorld
from adisp import adisp_async, adisp_process
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor, plugins, makeError
from gui.shared.gui_items.processors.plugins import MessageConfirmator, SyncValidator
from helpers import dependency
from resource_well.gui.feature.constants import UNAVAILABLE_REWARD_ERROR, PurchaseMode
from resource_well.gui.feature.resource import processLoadingResources, splitResourcesByType, mergeResources
from resource_well.gui.shared.event_dispatcher import showResourcesLoadingConfirm, showNextSerialVehiclesConfirm
from skeletons.gui.resource_well import IResourceWellController
_RESOURCE_WELL_MESSAGES = R.strings.system_messages.resourceWell

class _ResourceLoadingConfirmator(MessageConfirmator):

    def __init__(self, rewardID, resources, isReturnOperation):
        super(_ResourceLoadingConfirmator, self).__init__(None, True)
        self.__rewardID = rewardID
        self.__resources = resources
        self.__isReturnOperation = isReturnOperation
        return

    def _gfMakeMeta(self):
        return partial(showResourcesLoadingConfirm, self.__rewardID, self.__resources, self.__isReturnOperation)

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
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID):
        super(ResourceWellTakeBackProcessor, self).__init__()
        self.__rewardID = rewardID
        self.addPlugin(_ResourceLoadingConfirmator(self.__rewardID, mergeResources(self.__resourceWell.getBalance(), self.__rewardID), True))

    def _request(self, callback):
        Waiting.show('getResourcesBack')
        resourceWellAccComponent = getattr(BigWorld.player(), 'ResourceWellAccountComponent', None)
        if resourceWellAccComponent is None:
            callback(makeError('Can not find the ResourceWellAccountComponent'))
            return
        else:
            resourceWellAccComponent.takeBack(lambda code: self._response(code, callback))
            return

    def _successHandler(self, code, ctx=None):
        Waiting.hide('getResourcesBack')
        return super(ResourceWellTakeBackProcessor, self)._successHandler(code, ctx)

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('getResourcesBack')
        SystemMessages.pushMessage(text=backport.text(_RESOURCE_WELL_MESSAGES.resourcesReturnError()), type=SM_TYPE.ErrorSimple)
        return super(ResourceWellTakeBackProcessor, self)._errorHandler(code, errStr, ctx)


class _PutRewardValidator(SyncValidator):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID):
        self.__rewardID = rewardID
        super(_PutRewardValidator, self).__init__()

    def _validate(self):
        if not self.__resourceWell.isRewardCountAvailable(self.__rewardID):
            return plugins.makeError()
        mode = self.__resourceWell.getPurchaseMode()
        currentRewardID = self.__resourceWell.getCurrentRewardID()
        isCurrentRewardID = not currentRewardID or currentRewardID == self.__rewardID
        return plugins.makeError() if mode is PurchaseMode.TWO_PARALLEL_PRODUCTS and not isCurrentRewardID else plugins.makeSuccess()


class _BasePutResourcesProcessor(Processor):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID, resources, additionalPlugins):
        super(_BasePutResourcesProcessor, self).__init__()
        self.__rewardID = rewardID
        self.__resources = resources
        self.addPlugins([_PutRewardValidator(rewardID)] + additionalPlugins)

    def _request(self, callback):
        Waiting.show('putResources')
        resourceWellAccComponent = getattr(BigWorld.player(), 'ResourceWellAccountComponent', None)
        if resourceWellAccComponent is None:
            callback(makeError('Can not find the ResourceWellAccountComponent'))
            return
        else:
            resourceWellAccComponent.putResources(splitResourcesByType(self.__resources), self.__rewardID, lambda code, errStr, ctx: self._response(code, callback, errStr=errStr, ctx=ctx if isinstance(ctx, dict) else None))
            return

    def _successHandler(self, code, ctx=None):
        Waiting.hide('putResources')
        return super(_BasePutResourcesProcessor, self)._successHandler(code, ctx)

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('putResources')
        if errStr != UNAVAILABLE_REWARD_ERROR:
            SystemMessages.pushMessage(text=backport.text(_RESOURCE_WELL_MESSAGES.resourcesLoadingError()), type=SM_TYPE.ErrorSimple)
        return super(_BasePutResourcesProcessor, self)._errorHandler(code, errStr, ctx)


class PutResourcesProcessor(_BasePutResourcesProcessor):

    def __init__(self, rewardID, resources):
        resources = processLoadingResources(rewardID, resources)
        super(PutResourcesProcessor, self).__init__(rewardID, resources, [_ResourceLoadingConfirmator(rewardID, resources, False)])


class _NextSerialVehicleConfirmator(MessageConfirmator):

    def __init__(self, rewardID):
        super(_NextSerialVehicleConfirmator, self).__init__(None, True)
        self.__rewardID = rewardID
        return

    def _gfMakeMeta(self):
        return partial(showNextSerialVehiclesConfirm, self.__rewardID)

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


class NextSerialVehicleProcessor(_BasePutResourcesProcessor):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID, resources):
        super(NextSerialVehicleProcessor, self).__init__(rewardID, processLoadingResources(rewardID, resources), [_NextSerialVehicleConfirmator(rewardID)])
