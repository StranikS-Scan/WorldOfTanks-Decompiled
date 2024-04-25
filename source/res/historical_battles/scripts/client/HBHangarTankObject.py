# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBHangarTankObject.py
import logging
from enum import IntEnum
from collections import namedtuple
import BigWorld
import AnimationSequence
from items import vehicles
from helpers import dependency, newFakeModel
from ids_generators import SequenceIDGenerator
from vehicle_systems.stricted_loading import makeCallbackWeak
from cgf_obsolete_script.script_game_object import ScriptGameObject
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.diorama_vehicles_config import DioramaVehiclesConfig
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from historical_battles.gui.shared.hb_events import DioramaVehicleEvent
_logger = logging.getLogger(__name__)

class _ResourceType(IntEnum):
    MODEL = 1
    EFFECTS = 2


class _VehicleVisualInfo(object):
    __slots__ = ('intCD',)

    def __init__(self, intCD):
        self.intCD = intCD

    def __ne__(self, key):
        return not self.__eq__(key)

    def __eq__(self, key):
        return False if key is None else self.intCD == key.intCD


class HBHangarTankObject(BigWorld.Entity, ScriptGameObject):
    _gameEventController = dependency.descriptor(IGameEventController)
    _LoadingTaskId = namedtuple('_LoadingTaskId', ('loadingUniqueId', 'taskId', 'resourceType'))

    def __init__(self):
        BigWorld.Entity.__init__(self)
        ScriptGameObject.__init__(self, self.spaceID, 'HBHangarTankObject')
        self.typeDescriptor = None
        self.__loadingUniqueIdGenerator = SequenceIDGenerator()
        self.__loadingTaskId = None
        self._animators = {}
        self._visualInfo = None
        return

    def getMarkerHeightFactor(self):
        factor = self.markerHeightFactor
        if factor >= 3.0 or factor <= 0:
            _logger.error('The value %f of markerHeightFactor property is incorrect, should be (0; 3]', self.markerHeightFactor)
        return factor

    def _loadTank(self, visualInfo):
        self._visualInfo = visualInfo
        self._cancelTask()
        vehicleData = DioramaVehiclesConfig.getSelectedFrontVehicle(visualInfo.intCD, self._getVehicleIndex())
        loadingUniqueId = self.__loadingUniqueIdGenerator.next()
        callback = makeCallbackWeak(self.__onModelLoaded, vehicleData, loadingUniqueId)
        self.__startLoadingResource(loadingUniqueId, _ResourceType.MODEL, (vehicleData.modelPath,), callback)

    def _getVehicleIndex(self):
        raise NotImplementedError

    def _reloadEffects(self):
        if self.model is None:
            return
        elif self.__loadingTaskId is not None:
            return
        else:
            self.__loadEffects()
            return

    def _removeModel(self):
        self.model = None
        self._cancelTask()
        self._hideVehicleMarker()
        if self._animators:
            self._animators.clear()
        return

    def _cancelTask(self):
        if self.__loadingTaskId is None:
            return
        else:
            BigWorld.stopLoadResourceListBGTask(self.__loadingTaskId.taskId)
            self.__loadingTaskId = None
            return

    def _isModelBeingLoaded(self):
        return self.__loadingTaskId.resourceType == _ResourceType.MODEL if self.__loadingTaskId is not None else False

    def _hideVehicleMarker(self):
        g_eventBus.handleEvent(DioramaVehicleEvent(DioramaVehicleEvent.ON_HB_TANK_DESTROY, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _showVehicleMarker(self):
        _, nationId, itemId = vehicles.parseIntCompactDescr(self._visualInfo.intCD)
        self.typeDescriptor = vehicles.VehicleDescr(typeID=(nationId, itemId))
        playerName = self._getPlayerName()
        clanName = self._getClanName()
        roleId = self._getRoleId()
        isInBattle = self._isInBattle()
        g_eventBus.handleEvent(DioramaVehicleEvent(DioramaVehicleEvent.ON_HB_TANK_LOADED, ctx={'entity': self,
         'name': playerName,
         'clan': clanName,
         'roleId': roleId,
         'inBattle': isInBattle}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _getPlayerName(self):
        raise NotImplementedError

    def _getClanName(self):
        raise NotImplementedError

    def _getRoleId(self):
        raise NotImplementedError

    def _isInBattle(self):
        raise NotImplementedError

    def __loadEffects(self):
        effects = self.__prepareVehicleEffects()
        if not effects:
            return
        else:
            loaders = []
            for name in effects:
                vehicleEffect = DioramaVehiclesConfig.getTankEffectConfig(name)
                if vehicleEffect is None:
                    _logger.error('There is no vehicle effect %s', name)
                    continue
                loader = AnimationSequence.Loader(vehicleEffect.sequencePath, self.spaceID)
                loaders.append(loader)

            if loaders:
                loadingUniqueId = self.__loadingUniqueIdGenerator.next()
                callback = makeCallbackWeak(self.__onAnimationLoaded, effects, loadingUniqueId)
                self.__startLoadingResource(loadingUniqueId, _ResourceType.EFFECTS, loaders, callback)
            return

    def __startLoadingResource(self, loadingUniqueId, resourceType, resources, callback):
        if self.__loadingTaskId is not None:
            _logger.error('The previous loading is not canceled')
            self._cancelTask()
        taskId = BigWorld.loadResourceListBG(resources, callback)
        self.__loadingTaskId = self._LoadingTaskId(loadingUniqueId, taskId, resourceType)
        return

    def __onModelLoaded(self, vehicleData, loadingUniqueId, resourceRefs):
        if self.__loadingTaskId is None or self.__loadingTaskId.loadingUniqueId != loadingUniqueId:
            return
        else:
            self.__loadingTaskId = None
            failedRefs = resourceRefs.failedIDs
            modelName = vehicleData.modelPath
            isOk = modelName not in failedRefs
            if isOk:
                model = resourceRefs[modelName]
                self.model = model
                self.model.addMotor(BigWorld.Servo(self.matrix))
                self._showVehicleMarker()
                self.__loadEffects()
            else:
                _logger.error('The model %s is not found', modelName)
                self._removeModel()
                self._visualInfo = None
            return

    def __onAnimationLoaded(self, effects, loadingUniqueId, resourceRefs):
        if self.__loadingTaskId is None or self.__loadingTaskId.loadingUniqueId != loadingUniqueId:
            return
        else:
            self.__loadingTaskId = None
            if self.model is None:
                _logger.error('The model is missing')
                return
            failedRefs = resourceRefs.failedIDs
            for name in effects:
                vehicleEffect = DioramaVehiclesConfig.getTankEffectConfig(name)
                sequencePath = vehicleEffect.sequencePath
                if sequencePath not in failedRefs:
                    animator = resourceRefs.pop(sequencePath)
                    self.__startEffect(vehicleEffect, animator)
                _logger.error('The sequence %s is not found', sequencePath)

            return

    def __bindEffect(self, effect, animator):
        bindNode = self.__getModelBindNode(effect.hardpoint)
        if bindNode is None:
            _logger.error('The tank effect %s has no hardpoint %s', effect.name, effect.hardpoint)
            return False
        else:
            nullModel = newFakeModel()
            bindNode.attach(nullModel)
            animator.bindTo(AnimationSequence.ModelWrapperContainer(nullModel, self.spaceID))
            return True

    def __startEffect(self, effect, animator):
        animName = effect.name
        if animName in self._animators:
            _logger.error('The animation %s is already bound to a vehicle at the slot %d', animName, self._getVehicleIndex())
        if not self.__bindEffect(effect, animator):
            return
        self._animators[animName] = animator
        animator.start()

    def __getModelBindNode(self, name):
        bindNode = None
        try:
            bindNode = self.model.node(name)
        except ValueError:
            pass

        return bindNode

    def __prepareVehicleEffects(self):
        intCD = self._visualInfo.intCD
        effects = DioramaVehiclesConfig.getSelectedFrontVehicleEffects(intCD, self._getVehicleIndex())
        if self._animators:
            if effects:
                newEffects = set(effects)
                oldEffects = set(self._animators.keys())
                effectsToLoad = newEffects - oldEffects
                effectsToUnload = oldEffects - newEffects
                effectsToUpdate = newEffects.intersection(oldEffects)
                for name in effectsToUpdate:
                    vehicleEffect = DioramaVehiclesConfig.getTankEffectConfig(name)
                    animator = self._animators[name]
                    self.__bindEffect(vehicleEffect, animator)

                for name in effectsToUnload:
                    del self._animators[name]

                effects = tuple(effectsToLoad)
            else:
                self._animators.clear()
                return None
        return effects
