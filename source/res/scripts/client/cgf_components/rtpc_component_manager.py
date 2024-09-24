# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/rtpc_component_manager.py
import typing
import CGF
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from Sound import RTPCComponent
from Vehicular import KineticEnergyGetter, RemainingAmmoClipPercentGetter, DistanceToCannonGetter
from vehicle_systems.cgf_helpers import getVehicleGameObjectByGameObject, getVehicleEntityByGameObject, getVehicleEntityByVehicleGameObject
from vehicle_systems.sound_objects import getGunSoundObjectDistance

class ListenerKeys(object):
    SHOT_DONE_DISTANCE = 0


class RTPCSourceType(object):
    VALUE = 0
    KINETIC_ENERGY = 1
    INTERVAL_BETWEEN_SHOTS = 2
    REMAINIG_AMMO_CLIP_PERCENT = 3
    DISTANCE_TO_CANNON = 4
    COUNT = 5


@autoregister(presentInAllWorlds=True)
class RTPCComponentManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RTPCComponentManager, self).__init__()
        self.__eventHandlers = {}
        self.__rtpcGameObjectToVehicleGameObject = {}

    def getVehicleComponentForRTPC(self, rtpcGameObject):
        vehicleGameObject = self.__rtpcGameObjectToVehicleGameObject.get(rtpcGameObject.id)
        return getVehicleEntityByVehicleGameObject(vehicleGameObject) if vehicleGameObject is not None else None

    @onAddedQuery(CGF.GameObject, RTPCComponent, tickGroup='preInitGroup')
    def onRTPCAdded(self, gameObject, _):
        vehicleGameObject = getVehicleGameObjectByGameObject(gameObject)
        if vehicleGameObject is not None:
            self.__rtpcGameObjectToVehicleGameObject[gameObject.id] = vehicleGameObject
        return

    @onRemovedQuery(CGF.GameObject, RTPCComponent)
    def onRTPCRemoved(self, gameObject, _):
        self.__rtpcGameObjectToVehicleGameObject.pop(gameObject.id, None)
        return

    @onAddedQuery(CGF.GameObject, RTPCComponent, KineticEnergyGetter)
    def onKineticEnergyRTPCAdded(self, gameObject, rtpcComponent, _):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is not None and vehicle.appearance is not None:
            rtpcComponent.setRTPCsBySourceType(RTPCSourceType.KINETIC_ENERGY, vehicle.appearance.weaponEnergy)
        return

    @onProcessQuery(CGF.GameObject, RTPCComponent, RemainingAmmoClipPercentGetter, updatePeriod=0.2)
    def onRemainAmmoClipPercentRTPCProcess(self, gameObject, rtpcComponent, _):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is not None and vehicle.isPlayerVehicle:
            ammo = self.__sessionProvider.shared.ammo
            clipPercent = ammo.getClipPercentLeft() * 100 if ammo is not None else 0.0
            rtpcComponent.setRTPCsBySourceType(RTPCSourceType.REMAINIG_AMMO_CLIP_PERCENT, clipPercent)
        return

    @onAddedQuery(CGF.GameObject, RTPCComponent, DistanceToCannonGetter)
    def onDistanceToCannonRTPCAdded(self, gameObject, rtpcComponent, _):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is not None:
            event, handler = vehicle.onDiscreteShotDone, lambda : self.__setGunSoundDistance(gameObject, rtpcComponent)
            self.__addGameObjectListener(gameObject, ListenerKeys.SHOT_DONE_DISTANCE, event, handler)
        return

    @onRemovedQuery(CGF.GameObject, RTPCComponent, DistanceToCannonGetter)
    def onDistanceToCannonRTPCRemoved(self, gameObject, _, __):
        vehicle = getVehicleEntityByGameObject(gameObject)
        if vehicle is not None:
            self.__removeGameObjectListener(gameObject, ListenerKeys.SHOT_DONE_DISTANCE, vehicle.onDiscreteShotDone)
        return

    def __addGameObjectListener(self, gameObject, listenerKey, event, handler):
        eventKey = (gameObject.id, listenerKey)
        self.__eventHandlers[eventKey] = handler
        event += handler

    def __removeGameObjectListener(self, gameObject, listenerKey, event):
        eventKey = (gameObject.id, listenerKey)
        handler = self.__eventHandlers.pop(eventKey, None)
        event -= handler
        return

    def __setGunSoundDistance(self, gameObject, rtpcComponent):
        vehicle = self.getVehicleComponentForRTPC(gameObject)
        if vehicle is not None and vehicle.isAlive() and vehicle.isStarted:
            distance = getGunSoundObjectDistance(vehicle)
            rtpcComponent.setRTPCsBySourceType(RTPCSourceType.DISTANCE_TO_CANNON, distance)
        return
