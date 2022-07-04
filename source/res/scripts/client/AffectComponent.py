# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AffectComponent.py
import logging
import BigWorld
import CGF
import GenericComponents
from skeletons.gui.battle_session import IBattleSessionProvider
from battle_royale.gui.battle_control.controllers.vehicles_count_ctrl import IVehicleCountListener
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BREvents
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
_logger = logging.getLogger(__name__)
_HEAL_OVER_TIME_ZONE_ = 0
_DAMAGE_OVER_TIME_ZONE_ = 1
_FIRE_CIRCLE_ZONE_ = 2
_ZONE_ACTIVATE_EVENT_ = {_HEAL_OVER_TIME_ZONE_: BREvents.REPAIR_POINT_ENTER,
 _DAMAGE_OVER_TIME_ZONE_: BREvents.TRAP_POINT_ENTER,
 _FIRE_CIRCLE_ZONE_: BREvents.BR_FIRE_CIRCLE_ENTERED}
_ZONE_DEACTIVATE_EVENT_ = {_HEAL_OVER_TIME_ZONE_: BREvents.REPAIR_POINT_EXIT,
 _DAMAGE_OVER_TIME_ZONE_: BREvents.TRAP_POINT_EXIT,
 _FIRE_CIRCLE_ZONE_: BREvents.BR_FIRE_CIRCLE_LEFT}

class AffectComponent(IVehicleCountListener):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, gameObject, zoneType, isPlayerVehicle, spaceID, hasDebuff, vehicleID=None):
        self.hasDebuff = hasDebuff
        self.__gameObject = gameObject
        self.__spaceID = spaceID
        self.__particle = None
        self.__influenceZoneType = zoneType
        self.__isPlayerVehicle = isPlayerVehicle
        self.__soundPlaying = False
        self.__vehicleEffectConfig = self.getVehicleConfig()
        self.__ownVehicleID = vehicleID
        return

    def activate(self):
        if self.__isPlayerVehicle:
            self._activateSoundEvent()
        self._createParticles()
        ctrl = self.__guiSessionProvider.dynamic.vehicleCount
        if ctrl:
            ctrl.addRuntimeView(self)
        self.__guiSessionProvider.onUpdateObservedVehicleData += self._onUpdateObservedVehicleData

    def deactivate(self):
        self._deactivateSoundEvent()
        self._removeParticles()
        self.__ownVehicleID = None
        ctrl = self.__guiSessionProvider.dynamic.vehicleCount
        if ctrl:
            ctrl.removeRuntimeView(self)
        self.__guiSessionProvider.onUpdateObservedVehicleData -= self._onUpdateObservedVehicleData
        return

    def setPlayerVehicleAlive(self, isAlive):
        if not isAlive and BigWorld.player().isObserver():
            attachedVehicle = BigWorld.player().getVehicleAttached()
            isAlive = attachedVehicle.isAlive() if attachedVehicle else isAlive
        if not isAlive and self.__soundPlaying:
            self._deactivateSoundEvent()

    def _createParticles(self):
        if self.__vehicleEffectConfig is not None:
            self.__particle = gameObject = CGF.GameObject(self.__gameObject.spaceID)
            gameObject.createComponent(GenericComponents.HierarchyComponent, self.__gameObject)
            gameObject.createComponent(GenericComponents.ParticleComponent, self.__vehicleEffectConfig.path, True, self.__vehicleEffectConfig.rate)
            gameObject.createComponent(GenericComponents.TransformComponent, self.__vehicleEffectConfig.offset)
            gameObject.activate()
        return

    def _removeParticles(self):
        if self.__particle is not None:
            CGF.removeGameObject(self.__particle)
            self.__particle = None
        return

    def _activateSoundEvent(self):
        eventName = _ZONE_ACTIVATE_EVENT_[self.__influenceZoneType]
        _logger.debug('Affect: on activate play sound %s', eventName)
        BREvents.playSound(eventName)
        self.__soundPlaying = True

    def _deactivateSoundEvent(self):
        if self.__soundPlaying:
            eventName = _ZONE_DEACTIVATE_EVENT_[self.__influenceZoneType]
            _logger.debug('Affect: on deactivate play sound %s', eventName)
            BREvents.playSound(eventName)
            self.__soundPlaying = False

    def getVehicleConfig(self):
        if self.__influenceZoneType == _HEAL_OVER_TIME_ZONE_:
            vehicleEffect = None
        else:
            dynObjCache = dependency.instance(IBattleDynamicObjectsCache)
            config = dynObjCache.getConfig(BigWorld.player().arenaGuiType)
            pointEffect = config.getTrapPointEffect()
            vehicleEffect = pointEffect.vehicleEffect
        return vehicleEffect

    def _onUpdateObservedVehicleData(self, vehicleID, *args):
        if vehicleID == self.__ownVehicleID:
            self._activateSoundEvent()
        else:
            self._deactivateSoundEvent()


class TrapAffectComponent(AffectComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, gameObject, isPlayerVehicle, spaceID, vehicleID):
        super(TrapAffectComponent, self).__init__(gameObject, _DAMAGE_OVER_TIME_ZONE_, isPlayerVehicle, spaceID, True, vehicleID)


class FireCircleAffectComponent(AffectComponent):

    def __init__(self, gameObject, isPlayerVehicle, spaceID, vehicleID):
        super(FireCircleAffectComponent, self).__init__(gameObject, _FIRE_CIRCLE_ZONE_, isPlayerVehicle, spaceID, True, vehicleID)


class RepairAffectComponent(AffectComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, gameObject, isPlayerVehicle, spaceID, vehicleID):
        super(RepairAffectComponent, self).__init__(gameObject, _HEAL_OVER_TIME_ZONE_, isPlayerVehicle, spaceID, False, vehicleID)


def getInfluenceZoneType(pointDescr):
    return _HEAL_OVER_TIME_ZONE_ if pointDescr.hotParams else _DAMAGE_OVER_TIME_ZONE_


def getEffectConfig(influenceZoneType, config):
    if influenceZoneType == _HEAL_OVER_TIME_ZONE_:
        pointEffect = config.getRepairPointEffect()
    else:
        pointEffect = config.getTrapPointEffect()
    return pointEffect
