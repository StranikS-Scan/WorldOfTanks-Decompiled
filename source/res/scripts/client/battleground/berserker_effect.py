# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/berserker_effect.py
import logging
import BigWorld
import AnimationSequence
import Math
import math_utils
import ResMgr
from helpers import dependency, newFakeModel, CallbackDelayer
from constants import ATTACK_REASON, ATTACK_REASONS
from vehicle_systems.tankStructure import TankPartIndexes
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_VIEW_STATE
from gui.battle_royale.constants import SteelHunterEquipmentNames
from svarog_script.script_game_object import ScriptGameObject, ComponentDescriptorTyped
from battleground.component_loading import loadComponentSystem, Loader
from battleground.components import SequenceComponent, AvatarRelatedComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
_logger = logging.getLogger(__name__)

class BerserkerEffectComponent(AvatarRelatedComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __APPEARANCE_COMPONENT_NAME = 'berserker'

    def __init__(self, componentSystem):
        super(BerserkerEffectComponent, self).__init__(componentSystem)
        self.__loadingEffects = {}
        self.__activeEffectsTime = {}

    def deactivate(self):
        super(BerserkerEffectComponent, self).deactivate()
        for effObject in self.__loadingEffects.itervalues():
            effObject.stopLoading = True
            effObject.destroy()

        self.__loadingEffects.clear()
        self.__activeEffectsTime.clear()
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        progressionCtrl = self.__sessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.onVehicleUpgradeStarted -= self.__onVehicleUpgradeStarted
            progressionCtrl.onVehicleUpgradeFinished -= self.__onVehicleUpgradeFinished
        return

    def _initialize(self):
        super(BerserkerEffectComponent, self)._initialize()
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        progressionCtrl = self.__sessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.onVehicleUpgradeStarted += self.__onVehicleUpgradeStarted
            progressionCtrl.onVehicleUpgradeFinished += self.__onVehicleUpgradeFinished
        _TransformationParser().parse()
        return

    def __onVehicleFeedbackReceived(self, eventID, vehicleId, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_INSPIRE:
            equipmentID = value.get('equipmentID')
            if equipmentID is not None:
                itemName = self.__sessionProvider.shared.equipments.getEquipmentNameByID(equipmentID)
                if itemName == SteelHunterEquipmentNames.BERSERKER and value.get('isInactivation'):
                    self.__addEffect(vehicleId, value.get('endTime'))
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DOT_EFFECT:
            if value is not None and value.attackReasonID == ATTACK_REASONS.index(ATTACK_REASON.BERSERKER):
                vehicle = BigWorld.player().getVehicleAttached()
                if vehicle and vehicle.isAlive():
                    self.__addEffect(vehicle.id, value.endTime)
                else:
                    _logger.error('Can not start berserker effect, vehicle is not available.')
        return

    def __addEffect(self, vehicleId, endTime):
        self.__loadingEffects[vehicleId] = _BerserkerEffectObject(vehicleId, endTime, self.__destroyEffect)
        loadComponentSystem(self.__loadingEffects[vehicleId], self.__onEffectLoaded, self.__getLoaders())

    def __onEffectLoaded(self, effObject):
        vehicle = BigWorld.entities.get(effObject.vehicleId)
        if vehicle is not None and vehicle.appearance is not None:
            self.__activeEffectsTime[effObject.vehicleId] = effObject.endTime
            vehicle.appearance.addTempGameObject(effObject, self.__APPEARANCE_COMPONENT_NAME)
        self.__loadingEffects.pop(effObject.vehicleId)
        return

    def __destroyEffect(self, vehicleId):
        vehicle = BigWorld.entities.get(vehicleId)
        if vehicle is not None and vehicle.appearance is not None:
            vehicle.appearance.removeTempGameObject(self.__APPEARANCE_COMPONENT_NAME)
        self.__activeEffectsTime.pop(vehicleId, None)
        return

    def __getLoaders(self):
        loaders = {}
        arenaGuiType = self.__sessionProvider.arenaVisitor.getArenaGuiType()
        effDescr = self.__dynObjectsCache.getConfig(arenaGuiType).getBerserkerEffects()
        spaceId = BigWorld.player().spaceID
        loaders['turretEffectPlayer'] = Loader(AnimationSequence.Loader(effDescr.turretEffect.effectDescr.path, spaceId))
        loaders['hullEffectPlayer'] = Loader(AnimationSequence.Loader(effDescr.hullEffect.effectDescr.path, spaceId))
        return loaders

    def __onVehicleUpgradeStarted(self, vehicleId):
        if vehicleId in self.__activeEffectsTime:
            endTime = self.__activeEffectsTime[vehicleId]
            if endTime > BigWorld.serverTime():
                self.__destroyEffect(vehicleId)
                self.__activeEffectsTime[vehicleId] = endTime

    def __onVehicleUpgradeFinished(self, vehicleId):
        if vehicleId in self.__activeEffectsTime:
            endTime = self.__activeEffectsTime[vehicleId]
            if endTime > BigWorld.serverTime():
                self.__addEffect(vehicleId, endTime)
            else:
                self.__activeEffectsTime.pop(vehicleId, None)
        return


class _VehicleNodeEffect(SequenceComponent):
    _TANK_PART_INDEX = None

    def __init__(self, sequenceAnimator):
        super(_VehicleNodeEffect, self).__init__(sequenceAnimator)
        self.__fakeModel = None
        self.__vehicleId = None
        return

    @property
    def finished(self):
        return self.sequenceAnimator.getCurrNodeName() == 'end' and not self.sequenceAnimator.isCurrNodePlaying() if self.sequenceAnimator is not None else False

    def setVehicleId(self, vId):
        self.__vehicleId = vId

    def activate(self):
        super(_VehicleNodeEffect, self).activate()
        vehicle = BigWorld.entities.get(self.__vehicleId)
        if vehicle is not None and vehicle.model is not None and vehicle.appearance is not None:
            self.__fakeModel = newFakeModel()
            node = vehicle.model.node(TankPartIndexes.getName(self._TANK_PART_INDEX))
            node.attach(self.__fakeModel, self.__getTransform(vehicle))
            self.bindToModel(self.__fakeModel, BigWorld.player().spaceID)
            self.start()
        return

    def deactivate(self):
        super(_VehicleNodeEffect, self).deactivate()
        self.stop()
        if self.__vehicleId is not None and self.__fakeModel is not None:
            vehicle = BigWorld.entities.get(self.__vehicleId)
            if vehicle is not None and vehicle.model is not None:
                node = vehicle.model.node(TankPartIndexes.getName(self._TANK_PART_INDEX))
                if node is not None:
                    node.detach(self.__fakeModel)
        self.__fakeModel = None
        return

    def _getModuleName(self, typeDescriptor):
        raise NotImplementedError

    def __getTransform(self, vehicle):
        predefinedTransform = _TransformationParser.getTransform(vehicle.typeDescriptor.name.split(':')[1], TankPartIndexes.getName(self._TANK_PART_INDEX), self._getModuleName(vehicle.typeDescriptor))
        translation = predefinedTransform.get('offset') if predefinedTransform is not None else None
        scale = predefinedTransform.get('scale') if predefinedTransform is not None else None
        if translation is None or scale is None:
            minBounds, maxBounds, _ = vehicle.appearance.collisions.getBoundingBox(self._TANK_PART_INDEX)
            translation = translation or Math.Vector3((minBounds[0] + maxBounds[0]) / 2.0, (minBounds[1] + maxBounds[1]) / 2.0, (minBounds[2] + maxBounds[2]) / 2.0)
            scale = scale or Math.Vector3(abs(minBounds[0] - maxBounds[0]), abs(minBounds[1] - maxBounds[1]), abs(minBounds[2] - maxBounds[2]))
        rotation = Math.Vector3(0.0, 0.0, 0.0)
        return math_utils.createSRTMatrix(scale, rotation, translation)


class _VehicleHullEffect(_VehicleNodeEffect):
    _TANK_PART_INDEX = TankPartIndexes.HULL

    def _getModuleName(self, typeDescriptor):
        return typeDescriptor.hull.name


class _VehicleTurretEffect(_VehicleNodeEffect):
    _TANK_PART_INDEX = TankPartIndexes.TURRET

    def _getModuleName(self, typeDescriptor):
        return typeDescriptor.turret.name


class _BerserkerEffectObject(ScriptGameObject):
    turretEffectPlayer = ComponentDescriptorTyped(_VehicleTurretEffect)
    hullEffectPlayer = ComponentDescriptorTyped(_VehicleHullEffect)

    def __init__(self, vehicleId, endTime, doneCallback):
        super(_BerserkerEffectObject, self).__init__(BigWorld.player().spaceID)
        self.__vehicleId = vehicleId
        self.__doneCallback = doneCallback
        self.__endTime = endTime
        self.__callbackDelayer = CallbackDelayer.CallbackDelayer()

    @property
    def vehicleId(self):
        return self.__vehicleId

    @property
    def endTime(self):
        return self.__endTime

    def activate(self):
        for component in self._components:
            component.setVehicleId(self.__vehicleId)

        super(_BerserkerEffectObject, self).activate()
        self.__callbackDelayer.delayCallback(self.__endTime - BigWorld.serverTime(), self.__finish)

    def deactivate(self):
        super(_BerserkerEffectObject, self).deactivate()
        self.__callbackDelayer.clearCallbacks()

    def destroy(self):
        super(_BerserkerEffectObject, self).destroy()
        self.__callbackDelayer.destroy()
        self.__callbackDelayer = None
        self.__doneCallback = None
        return

    def tick(self):
        if self.__doneCallback is not None and self.turretEffectPlayer.finished and self.hullEffectPlayer.finished:
            self.__doneCallback(self.__vehicleId)
            self.__doneCallback = None
        return

    def __finish(self):
        for component in self._components:
            component.setTrigger('stop')


class _TransformationParser(object):
    __DEFAULT_SECTION = 'default'
    __vehicleTransformations = {}
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def parse(cls):
        cls.__vehicleTransformations.clear()
        arenaGuiType = cls.__sessionProvider.arenaVisitor.getArenaGuiType()
        effDescr = cls.__dynObjectsCache.getConfig(arenaGuiType).getBerserkerEffects()
        rootSection = ResMgr.openSection(effDescr.transformPath)
        if rootSection is None:
            return
        else:
            for vehicleName, vehicleSection in rootSection.items():
                vehTransform = {}
                for vehPartName, vehPartSection in vehicleSection.items():
                    vehTransform[vehPartName] = {}
                    for moduleName, moduleSection in vehPartSection.items():
                        vehTransform[vehPartName][moduleName] = {}
                        for tranformKey, transformValue in moduleSection.items():
                            vehTransform[vehPartName][moduleName][tranformKey] = transformValue.asVector3

                cls.__vehicleTransformations[vehicleName] = vehTransform

            return

    @classmethod
    def getTransform(cls, vehName, vehPartName, moduleName):
        vehTransform = cls.__vehicleTransformations.get(vehName)
        if vehTransform is None:
            return
        else:
            partTransform = vehTransform.get(vehPartName)
            return None if not partTransform else partTransform.get(moduleName) or partTransform.get(cls.__DEFAULT_SECTION)
