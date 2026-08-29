# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/sub_systems/pbh_vehicle_apperance_mover.py
from __future__ import absolute_import
import logging
import weakref
from copy import copy
import typing
import BigWorld
from CGF import TransformComponent
from gui.battle_control.controllers.prebattle_highlights.pbh_helpers import getPointTransformComponent
from gui.battle_control.controllers.prebattle_highlights.sub_systems.base_sub_system import BasePbhSubSystem
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from wg_async import AsyncScope, AsyncEvent, wg_await, wg_async, BrokenPromiseError, AsyncReturn
if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict
    from skeletons.gui.battle_session import IBattleContext
_logger = logging.getLogger(__name__)

class PbhVehicleAppearanceMover(BasePbhSubSystem):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, readyCallback, winnersGetter, sizeGetter, onVehiclesDataReadyEvent):
        self.__winnersGetter = winnersGetter
        self.__sizeGetter = sizeGetter
        self.__onVehiclesDataReadyEvent = onVehiclesDataReadyEvent
        self.__presentingVehiclesData = {}
        self.__originalMatrixProviders = {}
        self.__vehicleEntities = None
        self.__startCallbackID = None
        self.__vehiclesWaitingCallbackID = None
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        super(PbhVehicleAppearanceMover, self).__init__(readyCallback)
        return

    def subscribe(self):
        pass

    def unsubscribe(self):
        pass

    def isReady(self):
        return self.__getVehicleEntities() is not None

    def startFlow(self):
        self.__startCallbackID = None
        if not self.isReady():
            self.__startCallbackID = BigWorld.callback(0.0, self.startFlow)
            return
        else:
            self.__moveVehicles()
            return

    def stopFlow(self):
        self.__resetVehiclePositions()
        if self.__startCallbackID is not None:
            BigWorld.cancelCallback(self.__startCallbackID)
            self.__startCallbackID = None
        if self.__vehiclesWaitingCallbackID is not None:
            BigWorld.cancelCallback(self.__vehiclesWaitingCallbackID)
            self.__vehiclesWaitingCallbackID = None
        return

    def clear(self):
        self.__winnersGetter = None
        self.__sizeGetter = None
        self.__onVehiclesDataReadyEvent = None
        self.__presentingVehiclesData.clear()
        self.__originalMatrixProviders.clear()
        self.__vehicleEntities = None
        self.__scope.destroy()
        super(PbhVehicleAppearanceMover, self).clear()
        return

    def getPresentingVehiclesData(self):
        return self.__presentingVehiclesData

    @wg_async
    def historicalOutfitCompliance(self, level):
        vehs = self.__getVehicleEntities()
        if vehs is None:
            try:
                self.__vehiclesWaitingCallbackID = BigWorld.callback(0.0, self._vehiclesWaiter)
                self.__event.clear()
                yield wg_await(self.__event.wait())
                vehs = self.__getVehicleEntities()
            except BrokenPromiseError:
                _logger.debug('[PBH] Historical compliance check promise broken, aborting.')
                raise AsyncReturn(False)

        otherTiers = [ v.appearance.outfit.originalCustomizationDisplayType for v in vehs if hasattr(v, 'isPlayerVehicle') and not v.isPlayerVehicle ]
        maxType = max(otherTiers) if otherTiers else level
        raise AsyncReturn(level >= maxType)
        return

    def _vehiclesWaiter(self):
        vehicles = self.__getVehicleEntities()
        if vehicles is None:
            self.__vehiclesWaitingCallbackID = BigWorld.callback(0.0, self._vehiclesWaiter)
        else:
            self.__vehiclesWaitingCallbackID = None
            self.__event.set()
        return

    def __getVehicleEntities(self):
        if self.__vehicleEntities is not None:
            return self.__vehicleEntities
        else:
            vehEntities = []
            for data in self.__winnersGetter():
                vehEntity = BigWorld.entities.get(data['id'])
                if vehEntity is not None and vehEntity.inWorld and vehEntity.appearance is not None:
                    if vehEntity.appearance.isCompositionReady:
                        vehEntities.append(weakref.proxy(vehEntity))
                    else:
                        return

            if vehEntities:
                self.__vehicleEntities = vehEntities
            return self.__vehicleEntities

    def __moveVehicles(self):
        battleContext = self.__sessionProvider.getCtx()
        size = self.__sizeGetter()
        self.__presentingVehiclesData = {}
        for idx, vehEntity in enumerate(self.__vehicleEntities, 1):
            pointTransformCmp = getPointTransformComponent(idx, size)
            if pointTransformCmp is None:
                continue
            vehEntity.appearance.highlighter.suspendHighlight()
            pointWorldTransform = pointTransformCmp.worldTransform
            self.__presentingVehiclesData[vehEntity.id] = {'translation': pointWorldTransform.translation,
             'info': battleContext.getVehicleInfo(vehEntity.id)}
            appearanceTransformCmp = vehEntity.appearance.gameObject.findWrite(TransformComponent)
            vehTransformCmp = vehEntity.entityGameObject.findRead(TransformComponent)
            newLocalTransform = copy(pointTransformCmp.worldTransform)
            invParent = copy(vehTransformCmp.worldTransform)
            invParent.invert()
            newLocalTransform.postMultiply(invParent)
            compound = vehEntity.appearance.compoundModel
            self.__originalMatrixProviders[vehEntity.id] = {'compound': compound.matrix,
             'appearance': copy(appearanceTransformCmp.transform)}
            appearanceTransformCmp.transform = newLocalTransform
            compound.matrix = pointWorldTransform

        self.__onVehiclesDataReadyEvent()
        return

    def __resetVehiclePositions(self):
        for vehEntity in self.__vehicleEntities:
            original = self.__originalMatrixProviders.get(vehEntity.id)
            if original is not None:
                appearanceTransform = vehEntity.appearance.gameObject.findWrite(TransformComponent)
                vehEntity.appearance.compoundModel.matrix = original['compound']
                appearanceTransform.transform = original['appearance']
            vehEntity.appearance.highlighter.resumeHighlight()

        self.__originalMatrixProviders.clear()
        return
